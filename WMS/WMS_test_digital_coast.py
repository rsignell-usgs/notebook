# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from owslib.wms import WebMapService
%matplotlib inline

# <headingcell level=3>

# Digital Coast WMS endpoint

# <codecell>

url='http://coast.noaa.gov/arcgis/services/CCAP/All_Change_0106/MapServer/WMSServer?request=GetCapabilities&service=WMS'
wms = WebMapService(url)

# <codecell>

for k,v in wms.contents.iteritems():
    print v.name,v.title

# <headingcell level=3>

# Plot using manually constructed getMap request

# <codecell>

url='http://coast.noaa.gov/arcgis/services/CCAP/All_Change_0106/MapServer/WMSServer?request=GetMap&service=WMS&version=1.3.0&layers=2&styles=default&bbox=-80,34,-70,46&width=600&height=600&crs=CRS%3A84&format=image%2Fpng'
from IPython.core.display import Image
Image(url=url)

# <headingcell level=3>

# Plot using Cartopy

# <codecell>

layer = '2'

# <codecell>

plt.figure(figsize=(12,12))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.add_wms(wms, layer)
ax.coastlines('50m')
ax.set_extent((-80, -70, 34, 46))

# <headingcell level=3>

# Plot interactively using Folium

# <codecell>

# from Filipe Fernandes:

from folium.folium import Map
from IPython.display import HTML, IFrame


def inline_map(m):
    if isinstance(m, Map):
        m._build_map()
        srcdoc = m.HTML.replace('"', '&quot;')
        embed = HTML('<iframe srcdoc="{srcdoc}" '
                     'style="width: 100%; height: 500px; '
                     'border: none"></iframe>'.format(srcdoc=srcdoc))
    elif isinstance(m, str):
        embed = IFrame(m, width=750, height=500)
    return embed

# <codecell>

m = Map(width=750, height=500, location=[42, -72], zoom_start=5)

url='http://coast.noaa.gov/arcgis/services/CCAP/All_Change_0106/MapServer/WMSServer?request=GetCapabilities&service=WMS'

m.add_wms_layer(wms_name="northeast_0106_all_change_wm",
                wms_url="http://coast.noaa.gov/arcgis/services/CCAP/All_Change_0106/MapServer/WMSServer",
                wms_format="image/png",
                wms_layers='2')

m.add_layers_to_map()
inline_map(m)

# <codecell>


