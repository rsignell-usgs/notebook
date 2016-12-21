# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import iris

# <codecell>

# calculate the current speed using a EPIC NetCDF file
url = 'http://geoport.whoi.edu/thredds/dodsC/usgs/data2/emontgomery/stellwagen/CF-1.6/RCNWR/9541aqd-cal.nc'

# <codecell>

u = iris.load_cube(url,'eastward_sea_water_velocity')
v = iris.load_cube(url,'northward_sea_water_velocity')

# <codecell>

print u

# <codecell>

u.name()

# <codecell>

def calc_speed(u, v):
    """Calculate the speed"""

    speed = (u**2 + v**2)**0.5

    return speed

# <codecell>

spData = calc_speed(u,v)

# <codecell>

print spData

# <codecell>

import matplotlib.pyplot as plt
%matplotlib inline

# <codecell>

u.shape

# <codecell>

u[3000,0].data

# <codecell>

v[3000,0].data

# <codecell>

spData[3000,0].data

# <codecell>

spData.rename('sea_water_speed')

# <codecell>

spData

# <codecell>

spData.attributes = u.attributes

# <codecell>

spData

# <codecell>

print spData

# <codecell>


