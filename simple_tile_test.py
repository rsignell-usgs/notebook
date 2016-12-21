# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.img_tiles import GoogleTiles
%matplotlib inline

# <codecell>


# Specify a region of interest, in this case, Sudelfeld Ski Resort (Germany)
lat = 47 + 40 / 60.0 + 30 / 3600.
lon = 12 + 3 / 60.0 + 2 / 3600.

plt.figure(figsize=(10, 8))
ax = plt.subplot(111, projection=ccrs.PlateCarree())
ax.set_extent([12.0, 13.0, 47.0, 48.0])
gg_tiles = GoogleTiles()
ax.add_image(gg_tiles, 10)

plt.scatter(lon, lat, marker=(5, 1), color='red', s=200)
plt.title("Welcome to Sudelfeld")
gl = ax.gridlines(draw_labels=True,)
gl.xlabels_top = False
gl.ylabels_left = False


# <codecell>


