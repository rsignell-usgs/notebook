# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
%matplotlib inline

# <codecell>

def make_map(projection=ccrs.PlateCarree(), extent=[-42, 0, -32, 0.5]):
    subplot_kw = dict(projection=projection)
    fig, ax = plt.subplots(subplot_kw=subplot_kw)
    ax.set_extent(extent)
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    return fig, ax

# <codecell>

from owslib.wms import WebMapService
url = "http://nowcoast.noaa.gov/wms/com.esri.wms.Esrimap/analyses"
wms = WebMapService(url)

layer = 'NCEP_RAS_ANAL_RTG_SST'
fig, ax = make_map(projection=ccrs.PlateCarree())
ax.add_wms(wms, layer)
_ = ax.set_title(layer)

# <codecell>

url = "http://nowcoast.noaa.gov/wms/com.esri.wms.Esrimap/analyses"
layer = 'NCEP_RAS_ANAL_RTG_SST'

ax = plt.axes(projection=ccrs.PlateCarree())
ax.add_wms(url, layer)
ax.set_extent((-15, 25, 35, 60))

# <codecell>

url = 'http://map1c.vis.earthdata.nasa.gov/wmts-geo/wmts.cgi'
layer = 'VIIRS_CityLights_2012'

ax = plt.axes(projection=ccrs.PlateCarree())
ax.add_wmts(url, layer)
ax.set_extent((-15, 25, 35, 60))

plt.title('Suomi NPP Earth at night April/October 2012')
plt.show()

# <codecell>

url='http://coast.noaa.gov/arcgis/services/CCAP/All_Change_0106/MapServer/WMSServer?request=GetCapabilities&service=WMS'
wms = WebMapService(url)

# <codecell>

for k,v in wms.contents.iteritems():
    print v.name,v.title

# <codecell>

layer = '2'

# <codecell>

ax = plt.axes(projection=ccrs.PlateCarree())
ax.add_wms(url, layer, crs='CRS:84')
ax.set_extent((-71.5, 41.5, -71.0, 42))

# <codecell>

url='http://services.arcgisonline.com/arcgis/rest/services/Ocean_Basemap/MapServer/WMTS/1.0.0/WMTSCapabilities.xml'
layer='Ocean_Basemap'
ax = plt.axes(projection=ccrs.PlateCarree())
ax.add_wmts(url, layer)
ax.set_extent((-15, 25, 35, 60))

# <codecell>


# <codecell>

http://coast.noaa.gov/arcgis/services/CCAP/All_Change_0106/MapServer/WMSServer?request=GetCapabilities&service=WMS

