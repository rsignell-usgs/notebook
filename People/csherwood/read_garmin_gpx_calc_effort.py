
# coding: utf-8

# # Read Garmin GPX with heartrate
# 

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


# Within `trk` tags, find `hr` elements and get element text. CRS changed this to return an array of floats.

# In[6]:

elist = tree.xpath("./def:trk//gpxtpx:hr", namespaces=namespace)
hr = np.array([float(e.text) for e in elist])
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


# Calculate speed, effort, and efficiency. I have not figured out how to do this in Pandas, or how to avoid the loop when calculating time differences. The .total_seconds() conversion does not work on np arrays of datetime.deltatime objects.

# In[10]:

latr = np.radians(lat)
lonr = np.radians(lon)
dlatr = np.diff(latr)
dlonr = np.diff(lonr)
# Haversine formula for great circle
a = np.sin(dlatr/2.)**2 + np.cos(latr[0:-1]) * np.cos(latr[1:]) * np.sin(dlonr/2.)**2
c = 2. * np.arcsin(np.sqrt(a)) 
distm = 6367e3 * c
# distm is in meters.
print "distm",distm[0], np.shape(distm)

# this produces an array of datetime.deltatime objects
difft = np.diff(time)
print "np.diff(time)",difft[5].total_seconds(), np.shape(difft)

# there must be a better way:
dt = np.zeros_like(difft)
for i in np.arange(len(difft)):
    dt[i]= float(difft[i].total_seconds())
etime = np.cumsum(dt)

speed = distm/dt

# calculate effort as fraction of usable hr range
hr_rest = 68. # resting rate
hr_ana = 162. # anaerobic threshold
effort = (hr-hr_rest)/(hr_ana-hr_rest)

# calculate efficiency
eff = speed/effort[1:]

print "Effort: ",effort[0], type(effort), np.shape(effort)
fig = plt.figure(figsize=(12,4))
plt.plot(etime/60.,speed,label='Speed')
plt.plot(etime/60.,eff,label='Efficiency')
plt.ylabel('m/s; m/s/effort')
plt.xlabel('Elapsed time (minutes)')
plt.legend()


# Plot lon/lat with Cartopy

# In[11]:

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
plt.plot(lon[1:],lat[1:],'m-',transform=ccrs.PlateCarree());
# sheesh, this is embarassing
# 1) clip lat/lon and hr to length of other stuff (should actually interpolate to centerpoint)
lons = lon[1:]
lats = lat[1:]
# this does not work:
# plt.plot(lons,lats,transform=ccrs.PlateCarree(),marker='o',c=eff);
# nor does this:
# for i in np.arange(len(lons)):
#   plt.plot(lons[i],lats[i],transform=ccrs.PlateCarree(),marker='o',c=eff[i]);
# ax.scatter(lons,lats,transform=ccrs.PlateCarree(),marker='o',c=eff);
# ax.scatter(lons,lats,marker='o',c=eff);

gl=ax.gridlines(draw_labels=True)
gl.xlabels_top = False
gl.ylabels_right = False


# In[12]:

eff = speed/effort[1:]
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
# sheesh, this is embarassing
# 1) clip lat/lon and hr to length of other stuff (should actually interpolate to centerpoint)
lons = lon[1:]
lats = lat[1:]
# this does not work:
# plt.plot(lons,lats,transform=ccrs.PlateCarree(),marker='o',c=eff);
# nor does this:
# for i in np.arange(len(lons)):
#   plt.plot(lons[i],lats[i],transform=ccrs.PlateCarree(),marker='o',c=eff[i]);
kw = dict(alpha=0.5, lw=0 )
ax.scatter(lons,lats,transform=ccrs.PlateCarree(),marker='o',c=eff.tolist(),**kw);
# ax.scatter(lons,lats,marker='o',c=eff);

gl=ax.gridlines(draw_labels=True)
gl.xlabels_top = False
gl.ylabels_right = False


# In[13]:

se = (eff - eff.min()) / eff.ptp()

