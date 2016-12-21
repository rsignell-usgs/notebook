# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import netCDF4

# <codecell>

%%timeit
url='http://geoport.whoi.edu/thredds/dodsC/coawst_4/use/fmrc/coawst_4_use_best.ncd'
nc = netCDF4.Dataset(url)
t = nc.variables['temp']
lon = nc.variables['lon_rho']
lat = nc.variables['lat_rho']
pcolormesh(lon[:],lat[:],t[-1,-1,:,:],vmin=10,vmax=30);

# <codecell>


