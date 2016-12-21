# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# # four_panel.py
# ## By: Kevin Goebbert
# 
# Date: 5 October 2014
# 
# This script uses 1 deg GFS model output via nomads URL to plot the 192-h
# forecast in a four panel plot.
# 
# - UL Panel - MSLP, 1000-500 hPa Thickness, Precip (in)
# - UR Panel - 850-hPa Heights and Temperature ($^{\circ}$C)
# - LL Panel - 500-hPa Heights and Absolute Vorticity ($\times 10^{-5}$ s$^{-1}$)
# - LR Panel - 300-hPa Heights and Wind Speed (kts)
# 
# Created using the Anaconda Distribution of Python 2.7
# 
# Install Anaconda from http://continuum.io/downloads
# 
# Then install binstar to use the conda package management software
#      
#      conda install binstar
# 
# Then use conda to install two packages not a part of the main distribution.
# 
#     conda install basemap
#     conda install netcdf4

# <markdowncell>

# Original: http://nbviewer.ipython.org/gist/rsignell-usgs/269d0e3d7c8b64eaa261

# <codecell>

import numpy as np
import numpy.ma as ma
from matplotlib.colors import Normalize

class MidpointNormalize(Normalize):
    """Help with the colormap for 850-hPa Temps."""
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        """Ignoring masked values and all kinds of edge cases to make the
        example simple."""
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.50, 1]
        return ma.masked_array(np.interp(value, x, y))

# <markdowncell>

# Choose a model - right now this program is based on the 0.5 deg GFS output,
# there shouldn't be much to change for other GFS resolution sets, mainly smoothing
# 
# To modify for another model you would need to know variable names and determine
# what array elements are associated with your view window and vertical levels.

# <codecell>

from datetime import datetime


model = 'gfs_0p50'
# model = 'gfs_2p50'
# model = 'gfs_1p00'
# model = 'gfs_0p25'

# Get the current hour from the computer and choose the proper model
# initialization time.
# These times are set based on when they appear on the nomads server.
currhr = int(datetime.utcnow().strftime('%H'))
if currhr >= 4 and currhr < 11:
   run = '00'
elif currhr >= 11 and currhr < 17:
   run = '06'
elif currhr >= 17 and currhr < 23:
   run = '12'
else:
   run = '18'

# <codecell>

import time
from time import mktime

# Setting some time and date strings for use in constructing the filename and for output.
# fdate looks like ... 20141005 ... and is used in constructing the filename
# date looks like ... 2014-10-05 00:00:00 and is used for output
if (run == '18') and (currhr < 3):  # Because we need to go back to the previous day.
   date1 = (datetime.utcnow() - timedelta(hours=24)).strftime('%Y%m%d') + run
   fdate = (datetime.utcnow() - timedelta(hours=24)).strftime('%Y%m%d')
else:
   date1 = datetime.utcnow().strftime('%Y%m%d') + run
   fdate = datetime.utcnow().strftime('%Y%m%d')
   
date = time.strptime(date1, "%Y%m%d%H")
date = datetime.fromtimestamp(mktime(date))

# If you wanted to run a past date (I think they keep a week or two on the website), then
# just uncomment the following three lines to not use the current model run.
# date  = '20141005 00:00:00'
# fdate = '20141005'
# run   = '00'
print(date)

# <codecell>

uri = "http://nomads.ncep.noaa.gov:9090/dods/{}/{}{}/{}_{}z".format
url = uri(model, model[0:3], fdate, model, run)
url

# <codecell>

# Using iris to get the data.
import iris

cubes = iris.load(url)
print(cubes)

# <markdowncell>

# ### Pulling in only the data we need

# <codecell>

# Awfully long lon_names and no standard names...

for cube in cubes:
    if cube.standard_name:
        print(cube.standard_name)

# <codecell>

from iris import Constraint


# ... because of that this part is awkward.
def make_constraint(var_name="hgtprs"):
    return Constraint(cube_func=lambda cube: cube.var_name == var_name)


hgtprs = cubes.extract_strict(make_constraint("hgtprs"))
print(hgtprs)

# <codecell>

times  = hgtprs.coord(axis='T')

resolution = times.attributes['resolution']
print("The time resolution is {} days".format(resolution))

time_step = 24 * resolution
print("The time step between forecast hours is {} hours".format(time_step))

# <codecell>

# But this one makes it worth using iris.

# Set US Bounds for GFS 1 deg data.
lon = Constraint(longitude=lambda x: 220 <= x <= 310)
lat = Constraint(latitude=lambda y: 20 <= y <= 70)

z300 = Constraint(altitude=lambda z: z == 300)
z500 = Constraint(altitude=lambda z: z == 500)
z850 = Constraint(altitude=lambda z: z == 850)
z1000 = Constraint(altitude=lambda z: z == 1000)

hght850 = hgtprs.extract(lon & lat & z850)
# or use the cubes directly.
hght500 = cubes.extract_strict(make_constraint("hgtprs") & lon & lat & z500)
hght1000 = cubes.extract_strict(make_constraint("hgtprs") & lon & lat & z1000)

temp850 = cubes.extract_strict(make_constraint("tmpprs") & lon & lat & z850)

avor500 = cubes.extract_strict(make_constraint("absvprs") & lon & lat & z500)

hght300 = cubes.extract_strict(make_constraint("hgtprs") & lon & lat & z300)
uwnd_300 = cubes.extract_strict(make_constraint("ugrdprs") & lon & lat & z300)
vwnd_300 = cubes.extract_strict(make_constraint("vgrdprs") & lon & lat & z300)

mslp = cubes.extract_strict(make_constraint("prmslmsl") & lon & lat)
precip = cubes.extract_strict(make_constraint("apcpsfc") & lon & lat)

# <codecell>

# Specify units since Nomads doesn't provide!
# We can then use Iris to convert units later
temp850.units='Kelvin'
uwnd_300.units='m/s'
vwnd_300.units='m/s'
precip.units = 'mm'

# <markdowncell>

# ### For a few variables we want to smooth the data to remove non-synoptic scale wiggles

# <codecell>

import scipy.ndimage as ndimage

kw = dict(sigma=1.5, order=0)
Z_1000 = ndimage.gaussian_filter(hght1000.data, **kw)
Z_850 = ndimage.gaussian_filter(hght850.data, **kw)
Z_500 = ndimage.gaussian_filter(hght500.data, **kw)
Z_300 = ndimage.gaussian_filter(hght300.data, **kw)
pmsl = ndimage.gaussian_filter(mslp.data/100., **kw)

# <markdowncell>

# # Convert data to common formats

# <codecell>

temp850.convert_units(iris.unit.Unit('Celsius'))
tmpc850 = temp850.data

avor500.data *= 1e5  # preserve cube info here

uwnd_300.convert_units(iris.unit.Unit('knots'))
vwnd_300.convert_units(iris.unit.Unit('knots'))
wspd300 = np.sqrt(uwnd_300.data**2 + vwnd_300.data**2) 

precip.convert_units(iris.unit.Unit('inch'))
pcpin = precip.data

# <codecell>

# Set number of forecast hours from hght850 data
fhours = times.points.size
print("Number of steps in the loop for all forecast hours in the dataset = {}".format(fhours))

# <codecell>

# Set countour intervals for various parameters.
countours = dict(clevpmsl=range(900, 1100, 4),
                 clevtmpf2m=range(0, 120, 2),
                 clev850=range(1200, 1800, 30),
                 clevrh700=[70, 80, 90],
                 clevtmpc850=range(-30, 40, 2),
                 clev500=range(5100, 6000, 60),
                 clevavor500=range(-4, 1) + range(7, 49, 3),
                 clev300=range(8160, 10080, 120),
                 clevsped300=range(50, 230, 20),
                 clevprecip=[0, 0.01, 0.03, 0.05,
                             0.10, 0.15, 0.20, 0.25,
                             0.30, 0.40, 0.50, 0.60,
                             0.70, 0.80, 0.90, 1.00,
                             1.25, 1.50, 1.75, 2.00, 2.50])


# Colors for Vorticity.
colorsavor500 = ('#660066', '#660099', '#6600CC', '#6600FF',
                 'w', '#ffE800', '#ffD800', '#ffC800', '#ffB800',
                 '#ffA800', '#ff9800', '#ff8800', '#ff7800', '#ff6800',
                 '#ff5800', '#ff5000', '#ff4000', '#ff3000')

# <codecell>

from oceans import wrap_lon180

# Subset the lats and lons from the model according to view desired.
clats1 = hght300.coord(axis='Y').points
clons1 = wrap_lon180(hght300.coord(axis='X').points)

# Make a grid of lat/lon values to use for plotting with Basemap.
clats, clons = np.meshgrid(clons1, clats1)

# <codecell>

%matplotlib inline
import matplotlib.pyplot as plt

import cartopy.crs as ccrs
from cartopy.mpl import geoaxes
import cartopy.feature as cfeature

from mpl_toolkits.basemap import cm


def make_map(ax):
    kw = dict(edgecolor='gray', linewidth=0.5)
    ax.set_extent([-135, -55, 20, 60])
    ax.coastlines(**kw)
    ax.add_feature(states_provinces, **kw)
    ax.add_feature(cfeature.BORDERS, **kw)


states_provinces = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_1_states_provinces_lines',
    scale='50m',
    facecolor='none')

# Options.
colorbar = dict(orientation='horizontal', extend='both', aspect=65, shrink=0.913, pad=0, extendrect='True')
clabel = dict(inline=1, inline_spacing=10, fmt='%i', rightside_up=True)

def update_figure(fh):
    date = times.units.num2date(times.points[fh])
    global ax, fig
    [ax.cla() for ax in axes.ravel()]
    ax0, ax1, ax2, ax3 = axes.ravel()
    if fh == 0:
        # Clear colorbar when 0 is repeated.
        for a in fig.axes:
            if not isinstance(a, geoaxes.GeoAxes):
                fig.delaxes(a) 

    # Upper-left panel MSLP, 1000-500 hPa Thickness, Precip (in).
    make_map(ax0)
    cmap = cm.s3pcpn_l
    if fh % 2 != 0:
        data = pcpin[fh, ...]
    else:
        data = pcpin[fh, ...] - pcpin[fh-1, ...]

    cf = ax0.contourf(clons1, clats1, data,
                      countours['clevprecip'], cmap=cmap)
    if fh == 0:  # Only draw colorbar once!
        cbar = fig.colorbar(cf, ax=ax0, **colorbar)
    cs2 = ax0.contour(clats, clons, Z_500[fh, ...]-Z_1000[fh, ...], countours['clev500'], colors='r', linewidths=1.5,
                      linestyles='dashed')
    cs  = ax0.contour(clats, clons, pmsl[fh, ...], countours['clevpmsl'], colors='k', linewidths=1.5)

    ax0.clabel(cs, fontsize=8, **clabel)
    ax0.clabel(cs2, fontsize=7, **clabel)
    ax0.set_title('MSLP (hPa), 2m TMPF, and Precip',loc='left')
    ax0.set_title('VALID: {}'.format(date), loc='right')

    # Upper-right panel 850-hPa Heights and Temp (C).
    make_map(ax1)
    cmap = plt.cm.jet
    norm = MidpointNormalize(midpoint=10)
    cf = ax1.contourf(clats, clons, tmpc850[fh, ...], countours['clevtmpc850'], cmap=cmap, norm=norm, extend='both')
    
    if fh == 0:  # Only draw colorbar once!
        cbar = fig.colorbar(cf, ax=ax1, **colorbar)
    
    cs = ax1.contour(clats, clons, Z_850[fh, ...], countours['clev850'], colors='k', linewidths=1.5)
    ax1.clabel(cs, fontsize=8, **clabel)
    ax1.set_title('850-hPa HGHTs (m) and TMPC', loc='left')
    ax1.set_title('VALID: {}'.format(date), loc='right')

    # Lower-left panel 500-hPa Heights and AVOR.
    make_map(ax2)
    cf = ax2.contourf(clats, clons, avor500[fh, ...].data, countours['clevavor500'], colors=colorsavor500, extend='both')
    
    if fh == 0:  # Only draw colorbar once!
        cbar = fig.colorbar(cf, ax=ax2, **colorbar)
    
    cs = ax2.contour(clats, clons, Z_500[fh, ...], countours['clev500'], colors='k', linewidths=1.5)
    ax2.clabel(cs, fontsize=8, **clabel)
    ax2.set_title(r'500-hPa HGHTs (m) and AVOR ($\times 10^5$ s$^{-1}$)', loc='left')
    ax2.set_title('VALID: {}'.format(date), loc='right')

    # Lower-right panel 300-hPa Heights and Wind Speed (kts).
    make_map(ax3)
    cmap = plt.cm.get_cmap("BuPu")
    cf = ax3.contourf(clats, clons, wspd300[fh, ...], countours['clevsped300'], cmap=cmap, extend='max')
    
    if fh == 0:  # Only draw colorbar once!
        cbar = fig.colorbar(cf, ax=ax3, **colorbar)
    
    cs = ax3.contour(clats, clons, Z_300[fh, ...], countours['clev300'], colors='k', linewidths=1.5)
    ax3.clabel(cs, fontsize=8, **clabel)
    ax3.set_title('300-hPa HGHTs (m) and SPED (kts)', loc='left')
    ax3.set_title('VALID: {}'.format(date), loc='right')

    # To make a nicer layout use plt.tight_layout()
    fig.tight_layout()

    # Add room at the top of the plot for a main title
    fig.subplots_adjust(top=0.90)
    fig.suptitle('{} GFS {}Z'.format(fdate, run), fontsize=20)

# <markdowncell>

# ### Loop over the forecast hours. Current setting is use all 192-h at the 1 deg resolution

# <codecell>

cd /usgs/data2/notebook/tmp

# <codecell>

from JSAnimation import IPython_display
from matplotlib.animation import FuncAnimation

kw = dict(nrows=2, ncols=2, sharex=True, sharey=True,)
fig, axes = plt.subplots(subplot_kw=dict(projection=ccrs.Miller(central_longitude=0)),
                         figsize=(17, 12), **kw)

FuncAnimation(fig, update_figure, interval=100, frames=times.points.size)

# <codecell>


