# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import netCDF4
import matplotlib.pyplot as plt
import matplotlib.tri as Tri
import numpy as np
%matplotlib inline

# <codecell>

url='http://geoport.whoi.edu/thredds/dodsC/usgs/vault0/models/tides/fvcom/spectral_tides.nc'

# <codecell>

nc = netCDF4.Dataset(url)
ncv = nc.variables

# <codecell>

# read node locations
lat = ncv['lat'][:]
lon = ncv['lon'][:]
# read connectivity array
nv = ncv['nv'][:].T - 1

# <codecell>

# create a triangulation object, specifying the triangle connectivity array
tri = Tri.Triangulation(lon,lat, triangles=nv)

# <codecell>

ncv['h'].shape

# <codecell>

# plot depth using tricontourf
h = nc.variables['h'][:]
fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111,aspect=1.0/np.cos(lat.mean() * np.pi / 180.0))
plt.tricontourf(tri,-h,levels=range(-300,10,10))
plt.colorbar();

