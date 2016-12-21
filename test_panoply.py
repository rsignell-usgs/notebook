# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import iris
iris.FUTURE.netcdf_promote = True

# <codecell>

url='http://geoport.whoi.edu/thredds/dodsC/usgs/data2/rsignell/data/panoply.nc'
cubes = iris.load(url)

# <codecell>

print cubes

