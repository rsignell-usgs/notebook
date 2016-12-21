# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Use the new Cartopy WMTS capabilities to plot some MODIS data

# <codecell>

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from owslib.wmts import WebMapTileService

# <codecell>

url = 'http://map1c.vis.earthdata.nasa.gov/wmts-geo/wmts.cgi'
wmts = WebMapTileService(url)

# <codecell>

modis_layers = [s for s in sorted(list(wmts.contents)) if 'MODIS' in s  ]

# <codecell>

modis_layers

# <codecell>

layer = 'MODIS_Terra_CorrectedReflectance_TrueColor'

# <codecell>

plt.figure(figsize=(12,8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.add_wmts(url, layer)
#ax.set_extent((-15, 25, 35, 60))
ax.set_extent((10, 40, 35, 50))
plt.title(layer)
plt.show()

# <codecell>


# <codecell>


