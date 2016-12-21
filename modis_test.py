# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import iris

# <markdowncell>

# Try opening the east coast MODIS chlorophyll from PFEG

# <codecell>

url='http://oceanwatch.pfeg.noaa.gov/thredds/dodsC/satellite/ME/chla/1day'

# <codecell>

c = iris.load_cube(url,'concentration_of_chlorophyll_in_sea_water')

# <markdowncell>

# print last time step

# <codecell>

print c[-1,0,0]

# <markdowncell>

# Try opening the Global MODIS chlorophyll from PFEG

# <codecell>

url='http://oceanwatch.pfeg.noaa.gov/thredds/dodsC/satellite/MH1/chla/1day'
c = iris.load_cube(url,'concentration_of_chlorophyll_in_sea_water')

# <markdowncell>

# print last time step

# <codecell>

print c[-1,0,0]

# <codecell>


