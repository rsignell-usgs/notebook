
# coding: utf-8

# In[1]:

import netCDF4


# In[2]:

nc1 = netCDF4.Dataset('http://www.smast.umassd.edu:8080/thredds/dodsC/models/fvcom/NECOFS/Archive/Seaplan_33_Hindcast_v1/gom3_201301.nc')


# In[3]:

#nc2 = netCDF4.Dataset('/usgs/data2/notebook/data/MassBay_1995_01.nc','r+')
nc2 = netCDF4.Dataset('/usgs/data2/notebook/data/gom3_197801.nc','r+')


# In[4]:

nc2.variables['lon'][:] = nc1.variables['lon'][:]
nc2.variables['lat'][:] = nc1.variables['lat'][:]
nc2.variables['lonc'][:] = nc1.variables['lonc'][:]
nc2.variables['latc'][:] = nc1.variables['latc'][:]


# In[5]:

nc2.close()


# In[ ]:



