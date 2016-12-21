# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import cartopy.crs as ccrs
map_proj = ccrs.PlateCarree()
ax = plt.axes(projection=map_proj)
ax.stock_img()
ax.set_extent([-150, 60, -25, 60])

 

# <codecell>


