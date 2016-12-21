# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import iris
url='http://oceanmodeling.pmc.ucsc.edu:8080/thredds/dodsC/ccsnrt/fmrc/CCSNRT_Aggregation_best.ncd'
var='potential temperature'
cube = iris.load_cube(url,var)

# <codecell>

import iris
url='http://oceanmodeling.pmc.ucsc.edu:8080/thredds/dodsC/ccsnrt/fmrc/CCSNRT_Aggregation_best.ncd'
var='potential temperature'
cube = iris.load_cube(url,var)

# <codecell>

import iris
url='http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/us_east/US_East_Forecast_Model_Run_Collection_best.ncd'
var='sea_water_potential_temperature'
cube = iris.load_cube(url,var)

# <codecell>

iris.__version__

# <codecell>


