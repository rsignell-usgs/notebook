# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import iris
import time

# <codecell>

iris.__version__

# <codecell>

%%timeit -r 3

url='http://geoport.whoi.edu/thredds/dodsC/coawst_4/use/fmrc/coawst_4_use_best.ncd'
var='sea_water_potential_temperature'

cube = iris.load_cube(url,var)

# <codecell>

%%timeit -r 3
url='http://geoport.whoi.edu/thredds/dodsC/coawst_4/use/fmrc/coawst_4_use_best.ncd'
var='sea_water_potential_temperature'
cube = iris.load_raw(url,var)

# <codecell>

import netCDF4

# <codecell>

%%timeit -r 3
url='http://geoport.whoi.edu/thredds/dodsC/coawst_4/use/fmrc/coawst_4_use_best.ncd'
nc = netCDF4.Dataset(url)
t = nc.variables['temp']
lon = nc.variables['lon_rho']
lat = nc.variables['lat_rho']
tvar = nc.variables['time']
z = nc.variables['s_rho']

# <codecell>


