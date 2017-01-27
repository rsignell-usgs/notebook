
# coding: utf-8

# # FVCOM vertical slice along transect

# In[1]:

get_ipython().magic('matplotlib inline')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

import iris
import warnings
import pyugrid
import seawater as sw


# In[2]:

#url = 'http://crow.marine.usf.edu:8080/thredds/dodsC/FVCOM-Nowcast-Agg.nc'
#url ='http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/hindcasts/30yr_gom3/mean'
#url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/hindcasts/30yr_gom3'
url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc'
ugrid = pyugrid.UGrid.from_ncfile(url)


# In[3]:

# [lon,lat] of start point [A] and endpoint [B] for transect

A = [-84, 27]
B = [-82.5, 25.5]


# In[4]:

A = [-70, 41]
B = [-69, 42]


# In[5]:

A = [-70.11129, 43.479881]   # portland
B = [-66.240095, 40.834688]   # offshore Georges Bank


# In[6]:

A = [-70.6, 42.2]    # mass bay
B = [-69.3, 42.5]


# In[7]:

lon = ugrid.nodes[:, 0]
lat = ugrid.nodes[:, 1]
triangles = ugrid.faces[:]

triang = mtri.Triangulation(lon, lat, triangles=triangles)


# In[8]:

def make_map(projection=ccrs.PlateCarree()):
    fig, ax = plt.subplots(figsize=(8, 6),
                           subplot_kw=dict(projection=projection))
    ax.coastlines(resolution='10m')
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    return fig, ax


# In[9]:

def plt_triangle(triang, face, ax=None, **kw):
    if not ax:
        fig, ax = plt.subplots()
    ax.triplot(triang.x[triang.triangles[face]],
               triang.y[triang.triangles[face]],
               triangles=triang.triangles[face], **kw)


# In[10]:

fig, ax = make_map()

kw = dict(marker='.', linestyle='-', alpha=0.25, color='darkgray')
ax.triplot(triang, **kw)  # or lon, lat, triangules
buf=1.0
extent = [lon.min(), lon.max(),
          lat.min(), lat.max()]
extent = [A[0]-buf, B[0]+buf, B[1]-buf, A[1]+buf]
ax.set_extent(extent)
ax.plot(A[0], A[1], 'o')
ax.plot(B[0], B[1], 'o')


# In[11]:

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    cubes = iris.load_raw(url)


# In[12]:

print(cubes)


# In[13]:

cube = cubes.extract_strict('sea_water_potential_temperature')
print(cube)


# In[14]:

# Finding the right `num` is tricky.
num = 60

xi = np.linspace(A[0], B[0], num=num, endpoint=True)
yi = np.linspace(A[1], B[1], num=num, endpoint=True)

dist = sw.dist(xi, yi, 'km')[0].cumsum()
dist = np.insert(dist, 0, 0)


# In[ ]:

# grab a 3D chunk of data at a specific time step
t3d = cube[-1, ...].data


# In[ ]:

# this uses the CF formula terms to compute the z positions in the vertical
z3d = cube[-1, ...].coord('sea_surface_height_above_reference_ellipsoid').points


# In[ ]:

# this uses the CF formula terms to compute the z positions in the vertical
#z3d = [z for z in cube[-1,...].coords(axis='z') if z.units.is_convertible(cf_units.Unit('m'))][0].points


# In[ ]:

def interpolate(triang, xi, yi, data, trifinder=None):
    import matplotlib.tri as mtri
    # We still need to iterate in the vertical :-(
    i, j = data.shape
    slices = []
    for k in range(i):
        interp_lin = mtri.LinearTriInterpolator(triang, data[k, :], trifinder=trifinder)
        slices.append(interp_lin(xi, yi))
    return np.array(slices)

trifinder = triang.get_trifinder()
zi = interpolate(triang, xi, yi, t3d, trifinder=trifinder)
di = interpolate(triang, xi, yi, z3d, trifinder=trifinder)


# In[ ]:

fig, ax = plt.subplots(figsize=(11, 3))
im = ax.pcolormesh(dist, di, zi, shading='gouraud', cmap='jet')
fig.colorbar(im, orientation='vertical');


# In[ ]:



