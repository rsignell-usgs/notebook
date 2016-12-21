# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from shapely.geometry.polygon import Polygon
from shapely.geometry import MultiPolygon
import pyugrid
import json

# <codecell>

#url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc'
url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc'

# <codecell>

ug = pyugrid.UGrid.from_ncfile(url)

# <codecell>

lon = ug.nodes[:,0]
lat = ug.nodes[:,1]
nv = ug.faces[:]

# <codecell>

mp = MultiPolygon([Polygon(zip(lon[element],lat[element])) for element in nv])

# <codecell>

with open('ugrid.json','w') as f:
    f.write(json.dumps(mp))

