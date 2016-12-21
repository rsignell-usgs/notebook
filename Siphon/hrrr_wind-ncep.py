# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import matplotlib.pyplot as plt
import numpy as np
%matplotlib inline

# <codecell>

import xray
import datetime

# <codecell>

# lon/lat bounding box [lon_min, lon_max, lat_min, lat_max]
ax = [-72,-69.6,40.6, 43.5]

# Enter time in EDT
date = datetime.datetime.now()
date = datetime.datetime(2015,7,25,1,0,0)
# convert from EDT to UTC
date += datetime.timedelta(hours=+5)
date

# <codecell>

def get_latest_url(date):  
    # build URL for latest synoptic analysis time

    # keep moving back 6 hours until a valid URL found
    validURL = False; ncount = 0
    while (not validURL and ncount < 24):
#        URL = 'http://thredds-jumbo.unidata.ucar.edu/thredds/dodsC/grib/HRRR/CONUS_3km/surface/HRRR_CONUS_3km_surface_%04i%02i%02i%02i%02i.grib2' %\
#(date.year,date.month,date.day,1*(date.hour//1),0)
        URL='http://thredds-jumbo.unidata.ucar.edu/thredds/dodsC/grib/NCEP/HRRR/CONUS_2p5km/HRRR_CONUS_2p5km_%04i%02i%02i_%02i%02i.grib2' %\
(date.year,date.month,date.day,1*(date.hour//1),0)
#        print(URL)
        try:
            gfs = xray.open_dataset(URL)
            validURL = True
        except RuntimeError:
            date -= datetime.timedelta(hours=1)
            ncount += 1  
    return URL

# <codecell>

url = get_latest_url(date)
url

# <headingcell level=2>

# Try reading extracted data with Xray

# <codecell>

url

# <codecell>

nc = xray.open_dataset(url)

# <codecell>

#nc

# <codecell>

uvar_name='u-component_of_wind_height_above_ground'
vvar_name='v-component_of_wind_height_above_ground'
uvar = nc[uvar_name]
vvar = nc[vvar_name]

# <codecell>

grid = nc[uvar.grid_mapping]
grid

# <codecell>

lon0 = grid.longitude_of_central_meridian
lat0 = grid.latitude_of_projection_origin
lat1 = grid.standard_parallel
earth_radius = grid.earth_radius

# <headingcell level=2>

# Find points of LambertConformal grid withing lon/lat bounding box using Cartopy

# <codecell>

import cartopy
import cartopy.crs as ccrs

# <codecell>

#cartopy wants meters, not km
x = uvar.x.data*1000.
y = uvar.y.data*1000.

# <codecell>

xx,yy = np.meshgrid(x,y)

# <codecell>

#globe = ccrs.Globe(ellipse='WGS84') #default
globe = ccrs.Globe(ellipse='sphere', semimajor_axis=grid.earth_radius)

crs = ccrs.LambertConformal(central_longitude=lon0, central_latitude=lat0, 
                            standard_parallels=(lat0,lat1), globe=globe)

# <codecell>

#Find indices to read based on lon/lat bounding box
#newcs = ccrs.PlateCarree.transform_points(crs,xx,yy)
dest = ccrs.PlateCarree()
lonlat = dest.transform_points(crs, xx, yy)

# <codecell>

uvar.coords

# <codecell>

zmet=10. # want 10 m height
# use xray to select date and height with real numbers, not indices!
uv = uvar.sel(time2=date, height_above_ground3=zmet ,method='nearest')
vv = vvar.sel(time2=date, height_above_ground3=zmet ,method='nearest')

# <codecell>

# determine index range to select data that spans our lon/lat bounding box 
i = np.argwhere((lonlat[:,:,0] >= ax[0]) & 
               (lonlat[:,:,0] <= ax[1]) & 
               (lonlat[:,:,1] >= ax[2]) & 
               (lonlat[:,:,1] <= ax[3]))

j0 = i[:,0].min()
j1 = i[:,0].max()
i0 = i[:,1].min()
i1 = i[:,1].max()

# <codecell>

print(uv.shape)
print(i0,i1,j0,j1)

# <codecell>

uv=uv[j0:j1,i0:i1]
vv=vv[j0:j1,i0:i1]

# <codecell>

uv

# <headingcell level=2>

# Plot Lambert Conformal Conic data in PlateCarree coordinates using Cartopy

# <codecell>

x = uv.x.data*1000.
y = uv.y.data*1000.
u = uv.data
v = vv.data
spd = np.sqrt(u*u+v*v)

# <codecell>

print(spd.shape)
print(x.shape)
print(y.shape)

# <codecell>

fig = plt.figure(figsize=(14,14))
ax1 = plt.axes(projection=ccrs.PlateCarree())
c = ax1.pcolormesh(x,y,spd, transform=crs,zorder=0,vmin=0,vmax=10)
cb = fig.colorbar(c,orientation='vertical',shrink=0.5)
cb.set_label('m/s')
ax1.coastlines(resolution='10m',color='black',zorder=1)
ax1.quiver(x,y,u,v,transform=crs,zorder=2,scale=200)
gl = ax1.gridlines(draw_labels=True)
gl.xlabels_top = False
gl.ylabels_right = False
plt.title(uv.time2.data);
plt.axis(ax);

# <codecell>


# <codecell>


