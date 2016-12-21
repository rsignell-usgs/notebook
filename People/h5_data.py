
# coding: utf-8

# In[ ]:

# Let's see if we can read a generic h5 file using netCDF4


# In[1]:

get_ipython().magic(u'matplotlib inline')
import matplotlib.pyplot as plt
import netCDF4


# In[2]:

url='/usgs/data2/rsignell/temp_delta_newer.h5'


# In[3]:

nc = netCDF4.Dataset(url)


# In[4]:

nc.variables.keys()


# In[5]:

lat = nc.variables['lat'][:]
lon = nc.variables['lon'][:]


# Do we have groups?   Yep!

# In[6]:

g = nc.groups


# In[7]:

g


# In[8]:

g['2020']['45'].variables.keys()


# In[9]:

t = g['2020']['45'].variables['10'][:,:]


# In[10]:

print lat.shape,lon.shape,t.shape


# In[14]:

plt.pcolormesh(lon,lat,t)
plt.colorbar();


# In[ ]:



