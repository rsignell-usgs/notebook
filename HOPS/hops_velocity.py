
# coding: utf-8

# ## Plot velocity from non-CF HOPS dataset

# In[5]:

get_ipython().magic(u'matplotlib inline')
import netCDF4
import matplotlib.pyplot as plt


# In[6]:

url='http://geoport.whoi.edu/thredds/dodsC/usgs/data2/rsignell/gdrive/nsf-alpha/Data/MIT_MSEAS/MSEAS_Tides_20160317/mseas_tides_2015071612_2015081612_01h.nc'


# In[8]:

nc = netCDF4.Dataset(url)


# In[9]:

ncv = nc.variables


# In[ ]:

# extract lon,lat variables from vgrid2 variable
lon = ncv['vgrid2'][:,:,0]
lat = ncv['vgrid2'][:,:,1]


# In[20]:

# extract u,v variables from vbaro variable
itime = -1
u = ncv['vbaro'][itime,:,:,0]
v = ncv['vbaro'][itime,:,:,1]


# In[30]:

n=10
fig = plt.figure(figsize=(12,8))
plt.quiver(lon[::n,::n],lat[::n,::n],u[::n,::n],v[::n,::n])
#plt.axis([-70.6,-70.4,41.2,41.4])


# In[ ]:




# In[ ]:




# In[ ]:



