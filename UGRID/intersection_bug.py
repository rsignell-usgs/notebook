# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import pytz
from datetime import datetime, timedelta

import iris
iris.FUTURE.netcdf_promote = True

from iris.cube import CubeList

import time

# <codecell>

# SECOORA region (NC, SC GA, FL).
bbox = [-87.40, 24.25, -74.70, 36.70]

url = "http://geoport-dev.whoi.edu/thredds/dodsC/estofs/atlantic"

# <markdowncell>

# # Works fine

# <codecell>

t0 = time.time()
cube = iris.load_cube(url, 'sea_surface_height_above_geoid')

lon = iris.Constraint(longitude=lambda l: bbox[0] <= l <= bbox[2])
lat = iris.Constraint(latitude=lambda l: bbox[1] <= l < bbox[3])

cube = cube.extract(lon & lat)
print 'elapsed time = %f seconds' % (time.time()-t0)
print(cube)

# <markdowncell>

# # Hangs and I have to hit the kernel interrupt key

# <codecell>

t0 = time.time()
cube = iris.load_cube(url, 'sea_surface_height_above_geoid')

cube = cube.intersection(longitude=(bbox[0], bbox[2]),
                         latitude=(bbox[1], bbox[3]))
print time.time()-t0
print cube

# <codecell>


