
# coding: utf-8

# In[2]:

get_ipython().magic(u'matplotlib inline')


# In[3]:

import matplotlib.pyplot as plt
import matplotlib.tri as tri
import cartopy.crs as ccrs
from cartopy.io.img_tiles import MapQuestOpenAerial


# In[4]:

import numpy as np
x = -70.5 + np.random.rand(1000)
y = 42 + np.random.rand(1000)

triang = tri.Triangulation(x,y)


# In[5]:

geodetic = ccrs.Geodetic(globe=ccrs.Globe(datum='WGS84'))

fig = plt.figure(figsize=(12,8))
tiler = MapQuestOpenAerial()
ax = plt.axes(projection=tiler.crs)

bbox=[-71, -69.3, 42, 42.8]
#ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent(bbox)
ax.add_image(tiler, 8)

#ax.coastlines()
kw = dict(marker='.', linestyle='-', alpha=0.85, color='darkgray', transform=geodetic)
ax.triplot(triang, **kw)  # or lon, lat, triangules
#ax.set_extent()
gl = ax.gridlines(draw_labels=True)
gl.xlabels_top = False
gl.ylabels_right = False


# In[6]:

plt.triplot(triang)


# In[ ]:



