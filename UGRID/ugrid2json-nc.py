# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# # Try to write FVCOM mesh as geojson

# <codecell>

from shapely.geometry import MultiPolygon, mapping, polygon
import json

# <codecell>

#url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc'
#url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc'
url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_WAVE_FORECAST.nc'

# <markdowncell>

# use netcdf4 because UGRID takes longer

# <rawcell>

# import pyugrid
# ug = pyugrid.UGrid.from_ncfile(url)
# lon = ug.nodes[:,0]
# lat = ug.nodes[:,1]
# nv = ug.faces[:]

# <codecell>

import netCDF4
nc = netCDF4.Dataset(url)
ncv = nc.variables
lon = ncv['lon'][:]
lat = ncv['lat'][:]
nv = ncv['nv'][:,:].T - 1

# <codecell>

#mp = MultiPolygon([polygon.Polygon(zip(lon[element],lat[element])) for element in nv])
mp = MultiPolygon([polygon.Polygon(zip(lon[element],lat[element])) for element in nv[0:5]])

# <codecell>

type(mp)

# <codecell>

mp

# <codecell>

json.dumps(mapping(mp))

# <codecell>

with open('ugrid.json','w') as f:
    json.dump(mapping(mp), f)

# <codecell>


# <codecell>


