
# coding: utf-8

# # Read Bathy data from ERDDAP

# In[ ]:

get_ipython().system(u'conda install basemap --yes')


# In[1]:

import numpy as np
import matplotlib.pyplot as plt
import urllib
import netCDF4
from mpl_toolkits.basemap import Basemap


# In[2]:

# Definine the domain of interest
minlat = 42
maxlat = 45
minlon = -67
maxlon = -61.5
isub = 5
 
# Read data from: http://coastwatch.pfeg.noaa.gov/erddap/griddap/usgsCeSrtm30v6.html
# using the netCDF output option
base_url='http://coastwatch.pfeg.noaa.gov/erddap/griddap/usgsCeSrtm30v6.nc?'
query='topo[(%f):%d:(%f)][(%f):%d:(%f)]' % (maxlat,isub,minlat,minlon,isub,maxlon)
url = base_url+query
print url


# In[3]:

# store data in NetCDF file
file='usgsCeSrtm30v6.nc'
urllib.urlretrieve (url, file)


# In[4]:

# open NetCDF data in 
nc = netCDF4.Dataset(file)
ncv = nc.variables
print ncv.keys()


# In[5]:

lon = ncv['longitude'][:]
lat = ncv['latitude'][:]
lons, lats = np.meshgrid(lon,lat)
topo = ncv['topo'][:,:]


# In[ ]:

# Create map
m = Basemap(projection='mill', llcrnrlat=minlat,urcrnrlat=maxlat,llcrnrlon=minlon, urcrnrlon=maxlon,resolution='h')
fig1 = plt.figure(figsize=(10,8))
cs = m.pcolormesh(lons,lats,topo,cmap=plt.cm.jet,latlon=True)
m.drawcoastlines()
m.drawmapboundary()
plt.title('SMRT30 - Bathymetry/Topography')
cbar = plt.colorbar(orientation='horizontal', extend='both')
cbar.ax.set_xlabel('meters')
 
# Save figure (without 'white' borders)
plt.savefig('topo.png', bbox_inches='tight')

