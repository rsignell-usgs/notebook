# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import matplotlib.pyplot as plt
import numpy.ma as ma
%matplotlib inline

# <codecell>

url = 'http://geoport.whoi.edu/thredds/dodsC/coawst_4/use/fmrc/coawst_4_use_best.ncd'

# <codecell>

#plot with NetCDF4
import netCDF4
nc = netCDF4.Dataset(url)
ncv = nc.variables
lon = ncv['lon_rho'][:,:]
lat = ncv['lat_rho'][:,:]
t = ncv['temp'][-1,-1,:,:]
#rmask = 1 - ncv['mask_rho'][:,:]
#plt.pcolormesh(lon,lat,ma.masked_where(rmask,t),vmin=5,vmax=30)

# <codecell>

plt.pcolormesh(lon,lat,ma.masked_invalid(t),vmin=5,vmax=30)
plt.title('my plot')

# <codecell>

#plot with Iris
import iris
import iris.quickplot as qplt
time0=time.time()
cube = iris.load_cube(url,'sea_water_potential_temperature')

# <codecell>

qplt.pcolormesh(cube[-1,-1,:,:])

# <codecell>

last_step = cube[-1,-1,:,:]
last_step.data = ma.masked_invalid(last_step.data)
qplt.pcolormesh(last_step)

# <codecell>

print cube

# <codecell>

cube.plot

# <codecell>

slice=temp[-1,-1,::2,::2]
print slice

# <codecell>

ma.maske

# <codecell>


