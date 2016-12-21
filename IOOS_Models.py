# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Using Iris to access data from US-IOOS models

# <codecell>

import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import time
import cmtamu
%matplotlib inline

# <markdowncell>

# Note: `iris` is not a default package in Wakari or Anaconda, but just do 
# ```
# conda install -c https://conda.binstar.org/scitools iris
# ```

# <codecell>

import iris

# <codecell>

def find_timevar(cube):
    """Return the variable attached to
    time axis and rename it to time."""
    try:
        cube.coord(axis='T').rename('time')
        print('Renaming {} to time'.format(cube.coord('time').var_name))
    except:
        pass
    timevar = cube.coord('time')
    return timevar

# <codecell>

def time_near(cube, start):
    """Return the nearest time to `start`.
    TODO: Adapt to the new slice syntax"""
    timevar = find_timevar(cube)
    try:
        time1 = timevar.units.date2num(start)
        itime = timevar.nearest_neighbour_index(time1)
    except IndexError:
        itime = -1
    return timevar.points[itime]

# <codecell>

def var_lev_date(url=None,var=None,mytime=None,lev=0,subsample=1):
    time0= time.time()
#    cube = iris.load_cube(url,iris.Constraint(name=var.strip()))[0]
    cube = iris.load_cube(url,var)
#    cube = iris.load(url,var)[0]
#    print cube.coord('time')

    try:
        cube.coord(axis='T').rename('time')
    except:
        pass
    slice = cube.extract(iris.Constraint(time=time_near(cube,mytime)))
    slice = slice[lev,::subsample,::subsample]  
    print 'slice retrieved in %f seconds' % (time.time()-time0)
    return slice

# <codecell>

import cartopy.crs as ccrs
from cartopy.io import shapereader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

def make_map(projection=ccrs.PlateCarree(), figsize=(12,8)):
    fig, ax = plt.subplots(figsize=figsize,
                           subplot_kw=dict(projection=projection))
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    return fig, ax

# <codecell>

def map_plot(c,model=None):
    fig, ax = make_map()
    lat = c.coord(axis='Y').points
    lon = c.coord(axis='X').points
    time = c.coord('time')[0]
    cs = plt.pcolormesh(lon,lat,
                    np.ma.masked_invalid(c.data),
                    vmin = 12, vmax= 30.,
                    zorder=1, cmap=cmtamu.optiond)
    plt.colorbar()
    date=time.units.num2date(time.points)
    date_str=date[0].strftime('%Y-%m-%d %H:%M:%S %Z')
    plt.title('%s: %s: %s' % (model,c.long_name,date_str));
    _ = ax.coastlines('10m')

# <codecell>

# use contraints to select nearest time (UTC)
#mytime=dt.datetime(2008,7,28,12)  #specified time...
mytime=dt.datetime.utcnow() + + dt.timedelta(hours=+2)     # .... or now
print mytime

# <codecell>

model = 'USGS/COAWST'
url = 'http://geoport.whoi.edu/thredds/dodsC/coawst_4/use/fmrc/coawst_4_use_best.ncd'
var = 'sea_water_potential_temperature'
lev = -1
icube = var_lev_date(url=url, var=var, mytime=mytime, lev=lev, subsample=1)
map_plot(icube, model=model)

# <codecell>

model='MARACOOS/ESPRESSO'
url='http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2013_da/his/ESPRESSO_Real-Time_v2_History_Best'
var='sea_water_potential_temperature'
lev=-1
icube = var_lev_date(url=url,var=var, mytime=mytime, lev=lev)
map_plot(icube, model=model)

# <codecell>

model='SECOORA/NCSU'
url='http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/sabgom/SABGOM_Forecast_Model_Run_Collection_best.ncd'
var='sea_water_potential_temperature'
lev=-1
icube = var_lev_date(url=url,var=var, mytime=mytime, lev=lev)
map_plot(icube, model=model)

# <codecell>

model='CENCOOS/UCSC'
url='http://oceanmodeling.pmc.ucsc.edu:8080/thredds/dodsC/ccsnrt/fmrc/CCSNRT_Aggregation_best.ncd'
var='potential temperature'
lev=-1
icube = var_lev_date(url=url,var=var, mytime=mytime, lev=lev)
map_plot(icube, model=model)

# <codecell>

model='HIOOS'
url='http://oos.soest.hawaii.edu/thredds/dodsC/hioos/roms_assim/hiig/ROMS_Hawaii_Regional_Ocean_Model_Assimilation_best.ncd'
var='sea_water_potential_temperature'
lev=0
icube = var_lev_date(url=url,var=var, mytime=mytime, lev=lev)
map_plot(icube, model=model)

# <codecell>

model='Global RTOFS/NCEP'
url='http://ecowatch.ncddc.noaa.gov/thredds/dodsC/hycom/hycom_reg1_agg/HYCOM_Region_1_Aggregation_best.ncd'
var='sea_water_temperature'  
lev=1
icube = var_lev_date(url=url,var=var, mytime=mytime, lev=lev, subsample=1)
map_plot(icube, model=model)

# <codecell>

print icube

# <codecell>


