
# coding: utf-8

# In[1]:

import netCDF4
import matplotlib.pyplot as plt
import numpy as np
get_ipython().magic(u'matplotlib inline')


# In[4]:

#%%timeit 
#url = 'http://geoport-dev.whoi.edu/thredds/dodsC/usgs/data0/bbleh/spring2012/00_dir_roms.ncml'
url = 'http://clancy.whoi.edu:8080/thredds/dodsC/data1/dralston/hudson/sandy/sandy009/00_dir_roms.ncml'
nc = netCDF4.Dataset(url)
jd = nc.variables['ocean_time'][:]
lon = nc.variables['lon_rho'][:,:]
lat = nc.variables['lat_rho'][:,:]


# In[8]:

len(jd)


# In[10]:

for i in xrange(len(jd)):
    s = nc.variables['salt'][i,-1,:,:]
    print(i)
fig = plt.figure(figsize=(12,12))
plt.pcolormesh(lon,lat,s)
nc.close()


# In[ ]:



