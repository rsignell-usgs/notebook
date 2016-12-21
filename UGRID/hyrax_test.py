
# coding: utf-8

# In[1]:

import netCDF4


# In[2]:

#url = 'http://52.70.199.67:8080/opendap/ugrids/RENCI/maxele.63.nc'
url = 'http://ingria.coas.oregonstate.edu/opendap/ACTZ/ocean_his_3990_04-Dec-2015.nc'


# In[3]:

nc = netCDF4.Dataset(url)


# In[4]:

nc.variables.keys()


# In[5]:

nc.variables['lat_rho']


# In[6]:

nc.variables['lat_rho'][:5,:5]


# In[ ]:



