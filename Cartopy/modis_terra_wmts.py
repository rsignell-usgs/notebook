# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from owslib.wmts import WebMapTileService
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

earth_data = WebMapTileService('http://map1c.vis.earthdata.nasa.gov/wmts-geo/wmts.cgi')

plt.figure(figsize=(20, 8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.add_wmts(earth_data, 'MODIS_Terra_CorrectedReflectance_TrueColor')
plt.show()

# <codecell>


