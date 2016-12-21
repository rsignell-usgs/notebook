# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# ##Test out UGRID-0.9 compliant unstructured grid model datasets with PYUGRID

# <codecell>

import matplotlib.tri as tri
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
%matplotlib inline

# <codecell>

import iris
iris.FUTURE.netcdf_promote = True
from iris.fileformats.cf import reference_terms

# <codecell>

import cartopy.crs as ccrs
import pyugrid
%matplotlib inline

# <codecell>

#ADCIRC
#url =  'http://comt.sura.org/thredds/dodsC/data/comt_1_archive/inundation_tropical/UND_ADCIRC/Hurricane_Ike_3D_final_run_with_waves'

#FVCOM
#url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc'

#SELFE
url = 'http://comt.sura.org/thredds/dodsC/data/comt_1_archive/inundation_tropical/VIMS_SELFE/Hurricane_Ike_3D_final_run_with_waves'

# <codecell>

ucube = iris.load_cube(url,'eastward_sea_water_velocity')
vcube = iris.load_cube(url,'northward_sea_water_velocity')

# <codecell>

reference_terms['ocean_s_coordinate_g1'] = ['s', 'c', 'eta', 'depth', 'depth_c']
zcube = iris.load_cube(url,'depth_below_geoid')
z = zcube.data

# <codecell>

# Desired time for snapshot
# ....right now (or some number of hours from now) ...
start = dt.datetime.utcnow() + dt.timedelta(hours=6)
# ... or specific time (UTC)
#start = dt.datetime(2013,3,2,15,0,0)

# <codecell>

ug = pyugrid.UGrid.from_ncfile(url)

# What's in there?
print "There are %i nodes"%ug.nodes.shape[0]
#print "There are %i edges"%ug.edges.shape[0]
#print "There are %i faces"%ug.faces.shape[0]

# <codecell>

ug.data

# <codecell>

lon = ug.nodes[:,0]
lat = ug.nodes[:,1]
nv = ug.faces[:]

# <codecell>

triang = tri.Triangulation(lon,lat,triangles=nv)

# <codecell>


# <codecell>

# skip trying to find the closest time index to requested time, because it's messy
ind = -1 # just take the last time index for now
zcube = cube[ind]

# <codecell>

plt.figure(figsize=(12,12))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([-90, -60, 5, 50])
ax.coastlines()
levs = np.arange(0,5,.2)
plt.tricontourf(triang, z, levels=[10, 20, 50, 100, 200, 500, 1000, 2000])
plt.colorbar()
plt.tricontour(triang, z, colors='k',levels=levs)
tvar = ucube.coord('time')
tstr = tvar.units.num2date(tvar.points[ind])
gl = ax.gridlines(draw_labels=True)
gl.xlabels_top = False
gl.ylabels_right = False
plt.title('%s: Depth (m): %s' % (ucube.attributes['title'],tstr));

# <codecell>


