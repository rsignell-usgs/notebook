
# coding: utf-8

# # Test out standardized ADCIRC, SELFE and FVCOM  datasets with pyugrid, IRIS and Cartopy

# The datasets being accessed here are NetCDF files from ADCIRC, SELFE and FVCOM, with attributes added or modified virtually using NcML to meet the [UGRID conevntions standard for unstructured grid models](https://github.com/ugrid-conventions/ugrid-conventions/blob/v0.9.0/ugrid-conventions.md). 
# 
# This example was developed for the Integrated Ocean Observing System (IOOS) Coastal and Ocean Modeling Testbed. 
# 
# You can quickly and easily [set up the IOOS Anaconda python environment that can run this notebook](https://github.com/ioos/conda-recipes/wiki).

# In[1]:

get_ipython().magic(u'matplotlib inline')
from __future__ import (absolute_import, division, print_function)
import numpy as np
import matplotlib.tri as tri
import datetime as dt
import matplotlib.pyplot as plt


# In[2]:

import cartopy.crs as ccrs
import iris
iris.FUTURE.netcdf_promote = True
import pyugrid


# In[3]:

# specify UGRID compliant OPeNDAP Data URL

#ADCIRC
url = 'http://comt.sura.org/thredds/dodsC/data/comt_1_archive/inundation_tropical/UND_ADCIRC/Hurricane_Rita_2D_final_run_without_waves'

#FVCOM
#url = 'http://comt.sura.org/thredds/dodsC/data/comt_1_archive/inundation_tropical/USF_FVCOM/Hurricane_Rita_2D_final_run_without_waves'

#SELFE
#url = 'http://comt.sura.org/thredds/dodsC/data/comt_1_archive/inundation_tropical/VIMS_SELFE/Hurricane_Rita_2D_final_run_without_waves'

# set parameters
bbox = [-95, -85, 27, 32]                  # set the bounding box [lon_min, lon_max, lat_min, lat_max]
var = 'sea_surface_height_above_geoid'     # standard_name (or long_name, if no standard_name)
levs = np.arange(-1,5.0,.2)                # set the contour levels
start = dt.datetime(2005, 9, 24, 5, 0, 0)  # time in UTC
#start = dt.datetime.utcnow() + dt.timedelta(hours=6)


# In[4]:

cube = iris.load_cube(url,var)


# In[5]:

print(cube)


# In[ ]:

ug = pyugrid.UGrid.from_ncfile(url)

# What's in there?
#print("There are %i nodes"%ug.nodes.shape[0])
#print("There are %i edges"%ug.edges.shape[0])
#print("There are %i faces"%ug.faces.shape[0])


# In[ ]:

cube.mesh = ug
cube.mesh_dimension = 1  # (0:time,1:node)


# In[ ]:

lon = cube.mesh.nodes[:,0]
lat = cube.mesh.nodes[:,1]
nv = cube.mesh.faces


# In[ ]:

triang = tri.Triangulation(lon,lat,triangles=nv)


# In[ ]:

tvar = cube.coord('time')
itime = tvar.nearest_neighbour_index(tvar.units.date2num(start))


# In[ ]:

zcube = cube[itime]


# In[ ]:

plt.figure(figsize=(16,6))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent(bbox)
ax.coastlines()
plt.tricontourf(triang, zcube.data, levels=levs)
plt.colorbar(fraction=0.046, pad=0.04)
plt.tricontour(triang, zcube.data, colors='k',levels=levs)
tstr = tvar.units.num2date(tvar.points[itime])
gl = ax.gridlines(draw_labels=True)
gl.xlabels_top = False
gl.ylabels_right = False
plt.title('%s: %s: %s' % (var,tstr,zcube.attributes['title']));


# In[ ]:



