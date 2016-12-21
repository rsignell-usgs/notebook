
# coding: utf-8

# # plot a ugrid mesh

# In[4]:

get_ipython().magic(u'matplotlib inline')


# In[5]:

import matplotlib.tri as tri
import pyugrid


# In[8]:

url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/mwra/fvcom'


# In[10]:

ug = pyugrid.UGrid.from_ncfile(url)
lon = ug.nodes[:,0]
lat = ug.nodes[:,1]
nv = ug.faces
triang = tri.Triangulation(lon,lat,triangles=nv)


# In[25]:

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER


def make_map(projection=ccrs.PlateCarree()):
    fig, ax = plt.subplots(figsize=(8, 6),
                           subplot_kw=dict(projection=projection))
    ax.coastlines(resolution='10m')
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    return fig, ax


# In[27]:

#geodetic = ccrs.Geodetic(globe=ccrs.Globe(datum='WGS84'))
#fig, ax = make_map(projection=geodetic)
fig, ax = make_map()

kw = dict(marker='.', linestyle='-', alpha=0.85, color='darkgray')
ax.triplot(triang, **kw)  # or lon, lat, triangules
#ax.set_extent([-84, -78, 25, 32])


# In[31]:

from cartopy.io.img_tiles import MapQuestOpenAerial, MapQuestOSM, OSM
geodetic = ccrs.Geodetic(globe=ccrs.Globe(datum='WGS84'))

fig = plt.figure(figsize=(8,8))
tiler = MapQuestOpenAerial()
ax = plt.axes(projection=tiler.crs)

bbox=[-71, -70, 42, 43]
#ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent(bbox,geodetic)
ax.add_image(tiler, 8)

#ax.coastlines()
kw = dict(marker='.', linestyle='-', alpha=0.85, color='darkgray', transform=geodetic)
ax.triplot(triang, **kw)  # or lon, lat, triangules
#ax.set_extent()
gl = ax.gridlines(draw_labels=True)
gl.xlabels_top = False
gl.ylabels_right = False


# In[ ]:



