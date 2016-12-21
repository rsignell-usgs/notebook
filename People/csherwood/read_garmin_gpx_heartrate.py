
# coding: utf-8

# # Read Garmin GPX with heartrate

# In[1]:

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
from lxml import etree

get_ipython().magic(u'matplotlib inline')


# In[2]:

fn = "activity_721671330.gpx"
tree = etree.parse(fn)


# In[3]:

namespace = {'def': 'http://www.topografix.com/GPX/1/1',
             'gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1',
             'gpxx': 'http://www.garmin.com/xmlschemas/GpxExtensions/v3',
             'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
             }


# Within `trk` tags, find  `trkpt` elements get element values

# In[4]:

elist = tree.xpath('./def:trk//def:trkpt',namespaces=namespace)
lonlat = [e.values() for e in elist]
lon = np.array([float(i[0]) for i in lonlat])
lat = np.array([float(i[1]) for i in lonlat])
print lon[0],lat[0],np.shape(lon)


# Within `trk` tags, find `time` elements and get element text

# In[5]:

elist = tree.xpath('./def:trk//def:time',namespaces=namespace)
fmt = '%Y-%m-%dT%H:%M:%S.%fZ'
time = [datetime.strptime(d.text, fmt) for d in elist]
print time[0], np.shape(time)


# Withing `trk` tags, find `hr` elements and get element text

# In[6]:

elist = tree.xpath("./def:trk//gpxtpx:hr", namespaces=namespace)
hr = [float(e.text) for e in elist]
print hr[0], np.shape(hr)


# Make the dataframe

# In[7]:

df = pd.DataFrame.from_dict(dict(time=time, lon=lon, lat=lat, hr=hr))
df.set_index('time', drop=True, inplace=True)


# In[8]:

df.head(5)


# Plot the heartrate

# In[9]:

df['hr'].plot(figsize=(12,4));


# Plot lon/lat with Cartopy

# In[10]:

import cartopy.crs as ccrs
from cartopy.io.img_tiles import MapQuestOpenAerial

geodetic = ccrs.Geodetic(globe=ccrs.Globe(datum='WGS84'))
b=np.array([lon.min(), lat.min(), lon.max(), lat.max()])

plt.figure(figsize=(12,12))
# Open Source Imagery from MapQuest (max zoom = 16?)
tiler = MapQuestOpenAerial()
# Open Street Map (max zoom = 18?)
#tiler = OSM()
ax = plt.axes(projection=tiler.crs)
dx=b[2]-b[0]
dy=b[3]-b[1]
extent = (b[0]-0.1*dx,b[2]+0.1*dx,b[1]-0.1*dy,b[3]+0.1*dy)
ax.set_extent(extent, geodetic)
ax.add_image(tiler, 14)
plt.plot(lon,lat,'m-',transform=ccrs.PlateCarree());
gl=ax.gridlines(draw_labels=True)
gl.xlabels_top = False
gl.ylabels_right = False


# In[ ]:



