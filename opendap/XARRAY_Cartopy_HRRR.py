
# coding: utf-8

# # Data with projected coordinates using Xarray and Cartopy

# In[1]:

get_ipython().magic(u'matplotlib inline')
import xarray
import matplotlib.pyplot as plt
import numpy as np


# In[2]:

url = 'http://thredds.ucar.edu/thredds/dodsC/grib/NCEP/HRRR/CONUS_2p5km/Best'


# In[3]:

nc = xarray.open_dataset(url)


# In[4]:

var='Temperature_height_above_ground'
ncvar = nc[var]
ncvar


# In[5]:

grid = nc[ncvar.grid_mapping]
grid


# In[6]:

lon0 = grid.longitude_of_central_meridian
lat0 = grid.latitude_of_projection_origin
lat1 = grid.standard_parallel
earth_radius = grid.earth_radius


# ## Try plotting the LambertConformal data with Cartopy

# In[7]:

import cartopy
import cartopy.crs as ccrs


# In[8]:

isub = 10


# In[9]:

ncvar.x


# In[10]:

#cartopy wants meters, not km
x = ncvar.x[::isub].data*1000.
y = ncvar.y[::isub].data*1000.


# In[11]:

#globe = ccrs.Globe(ellipse='WGS84') #default
globe = ccrs.Globe(ellipse='sphere', semimajor_axis=grid.earth_radius)

crs = ccrs.LambertConformal(central_longitude=lon0, central_latitude=lat0, 
                            standard_parallels=(lat0,lat1), globe=globe)


# In[12]:

# find the correct time dimension name
for d in ncvar.dims:
    if "time" in d: 
        timevar = d


# In[13]:

istep = -1
fig = plt.figure(figsize=(12,8))
ax = plt.axes(projection=ccrs.PlateCarree())
mesh = ax.pcolormesh(x,y,ncvar[istep,0,::isub,::isub].data.squeeze()-273.15, transform=crs,zorder=0, vmin=0, vmax=40)
fig.colorbar(mesh)
ax.coastlines(resolution='10m',color='black',zorder=1)
gl = ax.gridlines(draw_labels=True)
gl.xlabels_top = False
gl.ylabels_right = False
plt.title(nc[timevar].data[istep]);


# In[ ]:



