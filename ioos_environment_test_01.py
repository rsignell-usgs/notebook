# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# IOOS Environment Test 01

# <markdowncell>

# Before running this notebook, see the [instructions for setting up the IOOS Python Environment](
# https://github.com/ioos/conda-recipes/wiki/Setting-up-the-IOOS-Python-environment-for-Linux)

# <codecell>

import iris
import pytz
from datetime import datetime, timedelta
from utilities import CF_names

stop = datetime(2014, 7, 7, 12)
stop = stop.replace(tzinfo=pytz.utc)
start = stop - timedelta(days=7)

bbox = [-87.40, 24.25, -74.70, 36.70]

name_list = CF_names['sea_water_temperature']

units = iris.unit.Unit('celsius')

# <codecell>

import warnings
from oceans import wrap_lon180
from utilities import quick_load_cubes, proc_cube, get_surface

# Changed to HYCOM because windows iris bombs with Memory error for big data.
#url = "http://oos.soest.hawaii.edu/thredds/dodsC/pacioos/hycom/global"
url = "http://ecowatch.ncddc.noaa.gov/thredds/dodsC/hycom/hycom_reg1_agg/HYCOM_Region_1_Aggregation_best.ncd"

with warnings.catch_warnings():
    warnings.simplefilter("ignore")  # Suppress iris warnings.
    cube = quick_load_cubes(url, name_list, callback=None, strict=True)

# <codecell>

cube

# <codecell>

cube.coord(axis='X').points[:20]

# <codecell>

# Just found a bug in proc_cube().  Meanwhile lets skip the constraint step.
cube.coord(axis='X').points = wrap_lon180(cube.coord(axis='X').points)

# <codecell>

cube.coord(axis='X').points[:20]

# <codecell>

# cube = proc_cube(cube, bbox=bbox, time=(start, stop), units=units)
cube = get_surface(cube)  # Get a 2D surface cube.  I am working on 3D...
cube

# <codecell>

from utilities import get_nearest_water, make_tree

obs = dict(lon=-77.7867, lat=34.2133)

tree, lon, lat = make_tree(cube)
kw = dict(k=10, max_dist=0.04, min_var=0.01)
series, dist, idx = get_nearest_water(cube, tree, obs['lon'], obs['lat'], **kw)

print('Distance (degrees): {}'.format(dist))
print('Indices: {!r}'.format(idx))

# <codecell>

series

# <codecell>

%matplotlib inline
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from cartopy.feature import NaturalEarthFeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

states = NaturalEarthFeature(category='cultural', scale='50m', facecolor='none',
                             name='admin_1_states_provinces_shp')

# <codecell>

def make_map(projection=ccrs.PlateCarree()):
    fig, ax = plt.subplots(figsize=(10, 10),
                           subplot_kw=dict(projection=projection))
    ax.coastlines(resolution='50m')
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    return fig, ax

# <codecell>

import numpy.ma as ma
from oceans import cm


c = cube[0, ...]
c.data = ma.masked_invalid(c.data)
# I hate when I have to "mask manually."
c.data = ma.masked_greater(c.data, 999)

lon = c.coord(axis='X').points
lat = c.coord(axis='Y').points

extent = (lon.min(), lon.max(),
          lat.min(), lat.max())

fig, ax = make_map()
ax.set_extent(extent)
cs = ax.pcolormesh(lon, lat, c.data, cmap=cm.rscolmap, alpha=0.5)
ax.plot(obs['lon'], obs['lat'], 'k*', label='observation')
# Note that to avoid dealing with the different indices formats
# from the different models (FVCOM, ROMS, ESTOFS etc)
# I recommend using the coords from the series output.
ax.plot(series.coord(axis='X').points,
        series.coord(axis='Y').points,
        'ro', label='model', alpha=0.5)
#ax.set_title(c.attributes['title'])
ax.add_feature(states, edgecolor='gray')
leg = ax.legend(numpoints=1, loc='upper left')

# <codecell>

import iris.quickplot as qplt

# I hate when I have to "mask manually."
series.data = ma.masked_greater(series.data, 999)

fig, ax = plt.subplots(figsize=(9, 2.75))
l, = qplt.plot(series)

# <codecell>

!conda info

# <codecell>

!conda list

