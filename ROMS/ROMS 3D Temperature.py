
# coding: utf-8

# # ROMS Vertical Section Plot

# In[1]:

get_ipython().magic(u'matplotlib inline')
import matplotlib.pyplot as plt
import numpy as np
import netCDF4


# In[2]:

# CF-Compliant ROMS ocean model output
# browse: http://geoport.whoi.edu/thredds/dodsC/examples/bora_feb.nc.html

# DAP URL
url='http://geoport.whoi.edu/thredds/dodsC/examples/bora_feb.nc'

nc = netCDF4.Dataset(url)
mask = nc.variables['mask_rho'][:]

# read longitude, latitude
lon_rho = nc.variables['lon_rho'][:,:]
lat_rho = nc.variables['lat_rho'][:,:]

# read water depth
depth = nc.variables['h'][:,:]

'''
z(n,k,j,i) = eta(n,j,i)*(1+s(k)) + depth_c*s(k) +
             (depth(j,i)-depth_c)*C(k)

  C(k) = (1-b)*sinh(a*s(k))/sinh(a) + 
         b*[tanh(a*(s(k)+0.5))/(2*tanh(0.5*a)) - 0.5]

formula_terms: s: s_rho eta: zeta depth: h a: theta_s b: theta_b depth_c: hc
'''


# In[3]:

s = nc.variables['s_rho'][:]
a = nc.variables['theta_s'][:]
b = nc.variables['theta_b'][:]
depth_c = nc.variables['hc'][:]

C = (1-b)*np.sinh(a*s)/np.sinh(a) + b*[np.tanh(a*(s+0.5))/(2*np.tanh(0.5*a)) - 0.5]


# In[4]:

nc.variables.keys()
print nc.variables['s_rho']


# In[5]:

# Reshape 1D vertical variables so we can broadcast
C.shape = (np.size(C), 1, 1)
s.shape = (np.size(s), 1, 1)


# In[6]:

tidx = -1       # just get the final time step, for now.
# read a 3D temperature field at specified time step
temp = nc.variables['temp'][tidx, :, :, :]
# read a 2D water level (height of ocean surface) at specified time step
eta = nc.variables['zeta'][tidx, :, :]
# calculate the 3D field of z values (vertical coordinate) at this time step
z = eta*(1+s) + depth_c*s + (depth-depth_c)*C


# In[7]:

(eta*s).shape


# In[8]:

fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(111,aspect=1.0/np.cos(np.mean(lat_rho.flatten()) * np.pi / 180.0))
pc3 = plt.pcolormesh(lon_rho,lat_rho,temp[-1,:,:], vmin=8, vmax=20)# plot surface temperature
plt.plot(lon_rho[::3,::3],lat_rho[::3,::3],'k-');
plt.plot(lon_rho.T[::3,::3],lat_rho.T[::3,::3],'k-');
plt.title('Surface Temperature on ROMS Model Curvilinear Grid')
plt.colorbar();


# In[9]:

lon_rho.shape


# In[10]:

lon3d = np.ones((20,1,1))*lon_rho
lon3d.shape


# In[11]:

jval=30
irange=range(0,130)
fig = plt.figure(figsize=(12,10))
plt.pcolormesh(lon3d[:,jval,irange],z[:,jval,irange],temp[:,jval,irange],shading='faceted')
plt.title('Temperature Section along Adriatic, ocean_s_coordinate vertical coordinate');


# In[ ]:



