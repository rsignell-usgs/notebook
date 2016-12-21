# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import numpy as np
from iris.cube import Cube
from iris.coords import DimCoord

# <codecell>

def create_cube():
    lon1d = np.arange(5)
    lat1d = np.arange(4)
    data = np.random.random((len(lat1d),len(lon1d)))
    cube = Cube(data)   
    lon = DimCoord(lon1d, standard_name='longitude',
                   units='degrees', circular=False)
    lat = DimCoord(lat1d, standard_name='latitude',
                   units='degrees')
    cube.add_dim_coord(lon, 1)
    cube.add_dim_coord(lat, 0)
    return cube

# <codecell>

cube = create_cube()

# <codecell>

x = cube.coord(axis='X')
x.guess_bounds()
x

# <codecell>

y = cube.coord(axis='Y')
y.guess_bounds()
y

# <codecell>

%matplotlib inline

import matplotlib.pyplot as plt
plt.pcolormesh(x.points, y.points, cube.data)

# <codecell>

import iris.quickplot as qplt

cs = qplt.pcolormesh(cube)

# <codecell>

import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

fig, ax = plt.subplots(subplot_kw=dict(projection=ccrs.PlateCarree()))
cs = qplt.pcolormesh(cube)
ax.set_xticks(x.points, crs=ccrs.PlateCarree())
ax.set_yticks(y.points, crs=ccrs.PlateCarree())
lon_formatter = LongitudeFormatter(zero_direction_label=True)
lat_formatter = LatitudeFormatter()
ax.xaxis.set_major_formatter(lon_formatter)
ax.yaxis.set_major_formatter(lat_formatter)

# <codecell>


# <codecell>


