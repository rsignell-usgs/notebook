# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import iris
iris.FUTURE.netcdf_promote = True

#url = 'http://geoport.whoi.edu/thredds/dodsC/usgs/data2/rsignell/usf_fvcom.ncml'
url = 'http://crow.marine.usf.edu:8080/thredds/dodsC/FVCOM-Nowcast-Agg.nc'
cubes = iris.load_raw(url)

cube = cubes.extract_strict('sea_surface_height_above_geoid')

print(cube)

# <codecell>

cubes

# <codecell>


