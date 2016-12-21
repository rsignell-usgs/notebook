# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from pylab import *
import netCDF4

# <codecell>

tidx = 0      # just get the final frame, for now.
scale = 0.03
isub = 3
url = 'http://comt.sura.org/thredds/dodsC/comt_2_full/testing/ucsc2.nc'

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

u = nc.variables['u']
shape(u)

# <codecell>

itime=0
u = nc.variables['u'][tidx, itime, :, :]

# <codecell>

nc = netCDF4.Dataset(url)
mask = nc.variables['mask_rho'][:]
lon_rho = nc.variables['lon_rho'][:]
lat_rho = nc.variables['lat_rho'][:]
anglev = nc.variables['angle'][:]
tidx=0

u = nc.variables['u'][tidx, -1, :, :]
v = nc.variables['v'][tidx, -1, :, :]

u = shrink(u, mask[1:-1, 1:-1].shape)
v = shrink(v, mask[1:-1, 1:-1].shape)

u, v = rot2d(u, v, anglev[1:-1, 1:-1])


# <codecell>

spd=sqrt(u*u+v*v)
spd=ma.masked_invalid(spd)

# <codecell>

lon_c = lon_rho[1:-1, 1:-1]
lat_c = lat_rho[1:-1, 1:-1]

# <markdowncell>

# ##Now we will make a *plot*

# <codecell>

figure = plt.figure(figsize=(12,12))
subplot(111,aspect=(1.0/cos(mean(lat_c)*pi/180.0)))
pcolormesh(lon_c,lat_c,spd)
q = quiver( lon_c[::isub,::isub], lat_c[::isub,::isub], u[::isub,::isub], v[::isub,::isub], 
        scale=1.0/scale, pivot='middle', zorder=1e35, width=0.003)
plt.quiverkey(q, 0.85, 0.07, 1.0, label=r'1 m s$^{-1}$', coordinates='figure');

# <codecell>

url2='http://comt.sura.org/thredds/dodsC/comt_2_full/testing/newer_ucsc2.nc'

nc = netCDF4.Dataset(url2)
mask = nc.variables['mask_rho'][:]
lon_rho = nc.variables['lon_rho'][:]
lat_rho = nc.variables['lat_rho'][:]
anglev = nc.variables['angle'][:]
tidx=0

u2 = nc.variables['u_rho'][tidx, -1, :, :]
v2 = nc.variables['v_rho'][tidx, -1, :, :]
spd2=sqrt(u2*u2+v2*v2)
spd2=ma.masked_invalid(spd2)

# <codecell>

figure = plt.figure(figsize=(12,12))
subplot(111,aspect=(1.0/cos(mean(lat_rho)*pi/180.0)))
pcolormesh(lon_rho,lat_rho,spd2)
q = quiver( lon_rho[::isub,::isub], lat_rho[::isub,::isub], u2[::isub,::isub], v2[::isub,::isub], 
        scale=1.0/scale, pivot='middle', zorder=1e35, width=0.003)
plt.quiverkey(q, 0.85, 0.07, 1.0, label=r'1 m s$^{-1}$', coordinates='figure');

# <codecell>

figure = plt.figure(figsize=(12,12))
subplot(111,aspect=(1.0/cos(mean(lat_rho)*pi/180.0)))
isub=1
q = quiver( lon_rho[::isub,::isub], lat_rho[::isub,::isub], u2[::isub,::isub], v2[::isub,::isub], 
        scale=1.0/scale, pivot='middle', zorder=1e35, width=0.003)
q2 = quiver( lon_c[::isub,::isub], lat_c[::isub,::isub], u[::isub,::isub], v[::isub,::isub], 
        scale=1.0/scale, pivot='middle', zorder=1e35, width=0.003,color='red')
axis([-135, -130,30, 32]);

# <codecell>

figure = plt.figure(figsize=(12,12))
subplot(111,aspect=(1.0/cos(mean(lat_rho)*pi/180.0)))
isub=1
q2 = quiver( lon_c[::isub,::isub], lat_c[::isub,::isub], u[::isub,::isub], v[::isub,::isub], 
        scale=1.0/scale, pivot='middle', zorder=1e35, width=0.003,color='red')
q = quiver( lon_rho[::isub,::isub], lat_rho[::isub,::isub], u2[::isub,::isub], v2[::isub,::isub], 
        scale=1.0/scale, pivot='middle', zorder=1e35, width=0.003)
axis([-135, -130,30, 32]);

# <codecell>


