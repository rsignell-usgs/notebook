# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# #Calculate speed and write to NetCDF using Xray and Iris

# <codecell>

url = 'http://geoport.whoi.edu/thredds/dodsC/usgs/data2/emontgomery/stellwagen/CF-1.6/RCNWR/9541aqd-cal.nc'

# <codecell>

def calc_speed(u, v):
    """Calculate the speed"""
    speed = (u**2 + v**2)**0.5
    return speed

# <markdowncell>

# ##1. Xray

# <codecell>

import xray

# <codecell>

ds = xray.open_dataset(url)

# <codecell>

# return varaibles matching standard name as a dict
def get_std_name_vars(ds,sn):
    return {k: v for k, v in ds.data_vars.iteritems() if 'standard_name' in v.attrs.keys() and sn in v.standard_name}

# <codecell>

sn = 'eastward_sea_water_velocity'
u = get_std_name_vars(ds,sn=sn)
sn = 'northward_sea_water_velocity'
v = get_std_name_vars(ds,sn=sn)

# <codecell>

# convert to list and extract value from first key,value pair
u = list(u.values())[0]
v = list(v.values())[0]

# <codecell>

spData = calc_speed(u,v)

# copy variable attribute data from 'u' variable
spData.attrs = u.attrs

# modify specific variable attribute data
spData.attrs['standard_name']='sea_water_speed'

# <codecell>

ds_out = xray.Dataset({'speed': spData})

# <codecell>

ds_out.attrs = ds.attrs

# <codecell>

ds_out.to_netcdf('speed_xray.nc')

# <codecell>

!ncdump -h speed_xray.nc

# <markdowncell>

# ##2. Iris

# <codecell>

import iris

# <codecell>

u = iris.load_cube(url,'eastward_sea_water_velocity')
v = iris.load_cube(url,'northward_sea_water_velocity')

# <codecell>

spData = calc_speed(u[:],v[:])

# <codecell>

spData.attributes = u.attributes

# <codecell>

spData.var_name = 'speed'

# <codecell>

spData.standard_name = 'sea_water_speed'

# <codecell>

iris.FUTURE.netcdf_no_unlimited=True
iris.save(spData,'speed_iris.nc')

# <codecell>

!ncdump -h speed_iris.nc

# <codecell>


