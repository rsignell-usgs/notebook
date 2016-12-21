# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import numpy as np
import matplotlib.pyplot as plt
import netCDF4
import datetime as dt
%matplotlib inline

# <codecell>

klev = 0    # 0 is bottom, -1 is top
#url = 'http://geoport.whoi.edu/thredds/dodsC/examples/bora_feb.nc'
url = 'http://geoport.whoi.edu/thredds/dodsC/clay/usgs/users/jcwarner/Projects/Sandy/triple_nest/00_dir_NYB05.ncml'

# <codecell>

def shrink(a,b):
    """Return array shrunk to fit a specified shape by triming or averaging.
    
    a = shrink(array, shape)
    
    array is an numpy ndarray, and shape is a tuple (e.g., from
    array.shape). a is the input array shrunk such that its maximum
    dimensions are given by shape. If shape has more dimensions than
    array, the last dimensions of shape are fit.
    
    as, bs = shrink(a, b)
    
    If the second argument is also an array, both a and b are shrunk to
    the dimensions of each other. The input arrays must have the same
    number of dimensions, and the resulting arrays will have the same
    shape.
    Example
    -------
    
    >>> shrink(rand(10, 10), (5, 9, 18)).shape
    (9, 10)
    >>> map(shape, shrink(rand(10, 10, 10), rand(5, 9, 18)))        
    [(5, 9, 10), (5, 9, 10)]   
       
    """

    if isinstance(b, np.ndarray):
        if not len(a.shape) == len(b.shape):
            raise Exception, \
                  'input arrays must have the same number of dimensions'
        a = shrink(a,b.shape)
        b = shrink(b,a.shape)
        return (a, b)

    if isinstance(b, int):
        b = (b,)

    if len(a.shape) == 1:                # 1D array is a special case
        dim = b[-1]
        while a.shape[0] > dim:          # only shrink a
            if (dim - a.shape[0]) >= 2:  # trim off edges evenly
                a = a[1:-1]
            else:                        # or average adjacent cells
                a = 0.5*(a[1:] + a[:-1])
    else:
        for dim_idx in range(-(len(a.shape)),0):
            dim = b[dim_idx]
            a = a.swapaxes(0,dim_idx)        # put working dim first
            while a.shape[0] > dim:          # only shrink a
                if (a.shape[0] - dim) >= 2:  # trim off edges evenly
                    a = a[1:-1,:]
                if (a.shape[0] - dim) == 1:  # or average adjacent cells
                    a = 0.5*(a[1:,:] + a[:-1,:])
            a = a.swapaxes(0,dim_idx)        # swap working dim back

    return a

# <codecell>

def rot2d(x, y, ang):
    '''rotate vectors by geometric angle'''
    xr = x*np.cos(ang) - y*np.sin(ang)
    yr = x*np.sin(ang) + y*np.cos(ang)
    return xr, yr

# <codecell>

nc = netCDF4.Dataset(url)
ncv = nc.variables

mask = ncv['mask_rho'][:]
lon_rho = ncv['lon_rho'][:]
lat_rho = ncv['lat_rho'][:]
anglev = ncv['angle'][:]

depth = ncv['h'][:]

# <codecell>

# Desired time for snapshot
# ....right now (or some number of hours from now) ...
start = dt.datetime.utcnow() + dt.timedelta(hours=+4)
# ... or specific time (UTC)
start = dt.datetime(2012,10,30,0,0,0)

# <codecell>

# Get desired time step  
time_var = ncv['ocean_time']
itime = netCDF4.date2index(start,time_var,select='nearest')

# <codecell>

u = ncv['u'][itime, klev, :, :]
v = ncv['v'][itime, klev, :, :]

u = shrink(u, mask[1:-1, 1:-1].shape)
v = shrink(v, mask[1:-1, 1:-1].shape)

u, v = rot2d(u, v, anglev[1:-1, 1:-1])

# <codecell>

lon_c = lon_rho[1:-1, 1:-1]
lat_c = lat_rho[1:-1, 1:-1]
depth_c = depth[1:-1, 1:-1]

# <codecell>

isub = 2
scale = 0.08
fig = plt.figure(figsize=(12,12))
plt.subplot(111,aspect=(1.0/np.cos(lat_c.mean()*np.pi/180.0)))
plt.pcolormesh(lon_c,lat_c,np.sqrt(u*u + v*v))
cbar = plt.colorbar(orientation='vertical')
plt.contour(lon_c,lat_c,depth_c,colors='k')
q = plt.quiver( lon_c[::isub,::isub], lat_c[::isub,::isub], u[::isub,::isub], v[::isub,::isub], 
        scale=1.0/scale, pivot='middle', zorder=1e35, width=0.003, color=[0.5,0.5,0.5])
plt.quiverkey(q, 0.85, 0.07, 1.0, label=r'1 m s$^{-1}$', coordinates='figure');
plt.axis([-74, -73, 39.8, 40.6]);

# <codecell>


