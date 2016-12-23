
# coding: utf-8

# # Subset and plot data with 1D lon,lat coordinates using Xarray and Cartopy

# With one dimensional coordinate values, we can slice these using coordinate values.  This demonstrates the power of Xarray's Pandas-like slicing.  With projected coordinates, there are 2D lon/lat arrays, so one can't slice on lon/lat.  It works here because the weather model is on a regular grid in lon/lat space. 

# In[1]:

get_ipython().magic(u'matplotlib inline')
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# In[2]:

url = 'http://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ghcncams/air.mon.mean.nc'


# In[3]:

ds = xr.open_dataset(url)


# In[4]:

var='air'
dvar = ds[var]
dvar


# In[5]:

# slice a longitude range, a latitute range and a specific time value
lat_bnds, lon_bnds = [50, 18], [-130+360., -64+360.]
ds_cut = ds.sel(lat=slice(*lat_bnds), lon=slice(*lon_bnds), time='2015-03-01')
ds_cut


# ## Plot with Cartopy

# In[6]:

import cartopy.crs as ccrs
import cartopy.feature as cfeature


# In[7]:

# make a nice date string for titling the plot
date_string = pd.Timestamp(ds_cut.time.data).strftime('%B %Y')


# In[8]:

# mask NaN values and convert Kelvin to Celcius
t_c = np.ma.masked_invalid(ds_cut.air)-272.15


# In[9]:

# PlateCarree is rectilinear lon,lat
data_crs = ccrs.PlateCarree()
# Albers projection for the continental US
plot_crs = ccrs.AlbersEqualArea(central_longitude=-96, central_latitude=23.)


# In[10]:

#Cartopy can use features from naturalearthdata.com
states_provinces = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_1_states_provinces_lines',
    scale='50m',
    facecolor='none')


# In[11]:

# plot using Cartopy
# using Albers projection with coastlines, country and state borders
fig = plt.figure(figsize=(12,8))
ax = plt.axes(projection=plot_crs)
mesh = ax.pcolormesh(ds_cut.lon, ds_cut.lat, t_c, transform=data_crs, zorder=0, vmin=-10, vmax=30)
fig.colorbar(mesh)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS)
ax.add_feature(states_provinces, edgecolor='gray')
ax.set_title('{}: {}'.format(dvar.long_name, date_string));

