# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from matplotlib.collections import PolyCollection
from matplotlib.collections import TriMesh
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.tri as Tri
from mpl_toolkits.basemap import Basemap
import datetime as dt
import netCDF4
%matplotlib inline

# <codecell>

import matplotlib
matplotlib.__version__

# <codecell>

url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc'
#url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM2_FORECAST.nc'
nc = netCDF4.Dataset(url)
# read node locations
lat = nc.variables['lat'][:]
lon = nc.variables['lon'][:]
# read element centroid locations
latc = nc.variables['latc'][:]
lonc = nc.variables['lonc'][:]
# read connectivity array
nv = nc.variables['nv'][:].T - 1
time_var = nc.variables['time']

# <codecell>

nc.variables['h'].shape

# <codecell>

# create a triangulation object, specifying the triangle connectivity array
tri = Tri.Triangulation(lon,lat, triangles=nv)

# <codecell>

# plot depth using tricontourf
h = nc.variables['h'][:]
fig = plt.figure(figsize=(12,12))
ax = fig.add_subplot(111,aspect=1.0/np.cos(latc.mean() * np.pi / 180.0))
plt.tricontourf(tri,-h,levels=range(-300,10,10))
plt.colorbar();

# <codecell>

# get velocity nearest to current time
start = dt.datetime.utcnow()+ dt.timedelta(hours=0)
istart = netCDF4.date2index(start,time_var,select='nearest')
layer = 0 # surface layer
u = nc.variables['u'][istart, layer, :]
v = nc.variables['v'][istart, layer, :]
mag = np.sqrt((u*u)+(v*v))

# <codecell>

# Now try plotting speed and vectors with Basemap using a PolyCollection
m = Basemap(projection='merc', llcrnrlat=lat.min(), urcrnrlat=lat.max(), 
    llcrnrlon=lon.min(), urcrnrlon=lon.max(), lat_ts=lat.mean(), resolution=None)

# project from lon,lat to mercator
xnode, ynode = m(lon, lat) 
xc, yc = m(lonc, latc) 

# create a TRI object with projected coordinates
tri = Tri.Triangulation(xnode, ynode, triangles=nv)

# make a PolyCollection using triangles
verts = concatenate((tri.x[tri.triangles][..., None],
      tri.y[tri.triangles][..., None]), axis=2)
collection = PolyCollection(verts)
collection.set_edgecolor('none')

# <codecell>

timestamp=start.strftime('%Y-%m-%d %H:%M:%S')

# <codecell>

# set the magnitude of the polycollection to the speed
collection.set_array(mag)
collection.norm.vmin=0
collection.norm.vmax=0.5

# <codecell>

fig = plt.figure(figsize=(12,12))
ax=fig.add_subplot(111)
m.drawmapboundary(fill_color='0.3')
#m.drawcoastlines()
#m.fillcontinents()
# add the speed as colored triangles 
ax.add_collection(collection) # add polygons to axes on basemap instance
# add the vectors
Q = m.quiver(xc,yc,u,v,scale=30)
# add a key for the vectors
qk = plt.quiverkey(Q,0.1,0.1,0.20,'0.2 m/s',labelpos='W')
plt.title('FVCOM Surface Current speed at %s UTC' % timestamp)

# <codecell>

# try using the TriMesh collection: can't figure this out
collection2 = TriMesh(tri)
fig = plt.figure(figsize=(12,12))
ax = fig.add_subplot(111)
ax.add_collection(collection2)

# <codecell>


