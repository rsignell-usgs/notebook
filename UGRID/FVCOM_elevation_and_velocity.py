
# coding: utf-8

# # Access data from the NECOFS (New England Coastal Ocean Forecast System) via OPeNDAP

# Demonstration using the NetCDF4-Python library to access velocity data from a triangular grid ocean model (FVCOM) via OPeNDAP, specifying the desired URL, time, layer and lat/lon region of interest.  The resulting plot of forecast velocity vectors over color-shaded bathymetry is useful for a variety of recreational and scientific purposes. 
# 
# NECOFS (Northeastern Coastal Ocean Forecast System) is run by groups at the University of Massachusetts Dartmouth and the Woods Hole Oceanographic Institution, led by Drs. C. Chen, R. C. Beardsley, G. Cowles and B. Rothschild. Funding is provided to run the model by the NOAA-led Integrated Ocean Observing System and the State of Massachusetts.
# 
# NECOFS is a coupled numerical model that uses nested weather models, a coastal ocean circulation model, and a wave model. The ocean model is a volume-mesh model with horizontal resolution that is finer in complicated regions. It is layered (not depth-averaged) and includes the effects of tides, winds, and varying water densities caused by temperature and salinity changes.
# 
# * Model description: http://fvcom.smast.umassd.edu/research_projects/NECOFS/model_system.html
# * THREDDS server with other forecast and archive products: http://www.smast.umassd.edu:8080/thredds/catalog.html

# In[17]:

from pylab import *
import matplotlib.tri as Tri
import netCDF4
import datetime as dt


# In[18]:

# DAP Data URL
# MassBay GRID
#url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc'
# GOM3 GRID
#url='http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc'
# GOM3 Monthly mean
url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/hindcasts/30yr_gom3/mean'
# Open DAP
nc = netCDF4.Dataset(url).variables
nc.keys()


# In[19]:

# take a look at the "metadata" for the variable "u"
print nc['u']


# In[20]:

shape(nc['temp'])


# In[21]:

shape(nc['nv'])


# In[22]:

# Desired time for snapshot
# ....right now (or some number of hours from now) ...
#start = dt.datetime.utcnow() + dt.timedelta(hours=6)
# ... or specific time (UTC)
start = dt.datetime(1998,4,15,0,0,0)


# In[23]:

# Get desired time step  
time_var = nc['time']
itime = netCDF4.date2index(start,time_var,select='nearest')

# Get lon,lat coordinates for nodes (depth)
lat = nc['lat'][:]
lon = nc['lon'][:]
# Get lon,lat coordinates for cell centers (depth)
latc = nc['latc'][:]
lonc = nc['lonc'][:]
# Get Connectivity array
nv = nc['nv'][:].T - 1 


# In[24]:

dtime = netCDF4.num2date(time_var[itime],time_var.units)
daystr = dtime.strftime('%Y-%b-%d %H:%M')
print daystr


# In[25]:

tri = Tri.Triangulation(lon,lat, triangles=nv)


# In[26]:

# get current at layer [0 = surface, -1 = bottom]
ilayer = 0
u = nc['u'][itime, ilayer, :]
v = nc['v'][itime, ilayer, :]
# Get water level
h = nc['zeta'][itime,:]  # water level 


# In[27]:

#woods hole
levels=arange(-0.3,0.3,0.01)   # water level contours to plot
ax = [-70.7, -70.6, 41.48, 41.55]
maxvel = 1.0
subsample = 2


# In[28]:

#boston harbor
levels=arange(-0.3,0.3,0.01)   # water level contours to plot
ax= [-70.97, -70.82, 42.25, 42.35] # 
maxvel = 0.5
subsample = 3


# In[29]:

# whole gulf
levels=arange(-0.3,0.3,0.01)   # water level contours to plot
ax= [-74.5, -70, 39.0, 41.0] # 
maxvel = 0.2
subsample = 10


# In[34]:

# whole gom3
levels=arange(-0.5,0.5,0.02)   # water level contours to plot
ax= [-80, -55, 34.0, 48.0] # 
maxvel = 1.0
subsample = 20


# In[35]:

# find velocity points in bounding box
ind = argwhere((lonc >= ax[0]) & (lonc <= ax[1]) & (latc >= ax[2]) & (latc <= ax[3]))


# In[36]:

np.random.shuffle(ind)
Nvec = int(len(ind) / subsample)
idv = ind[:Nvec]


# In[40]:

# tricontourf plot of water depth with vectors on top
figure(figsize=(18,10))
subplot(111,aspect=(1.0/cos(mean(lat)*pi/180.0)))
#tricontourf(tri, h-h.mean(),levels=levels,shading='faceted',cmap=plt.cm.gist_earth)
tricontourf(tri, h-h.mean(),levels=levels,shading='faceted')
#axis(ax)
gca().patch.set_facecolor('0.5')
cbar=colorbar()
cbar.set_label('Water Level (m)', rotation=-90)
#Q = quiver(lonc[idv],latc[idv],u[idv],v[idv],scale=20)
#maxstr='%3.1f m/s' % maxvel
#qk = quiverkey(Q,0.92,0.08,maxvel,maxstr,labelpos='W')
title('NECOFS Velocity, Layer %d, %s UTC' % (ilayer, daystr));


# In[37]:


# turn the triangles into a PolyCollection
verts = concatenate((tri.x[tri.triangles][..., None],
      tri.y[tri.triangles][..., None]), axis=2)
collection = PolyCollection(verts)
collection.set_edgecolor('none')


# In[ ]:

# set the magnitude of the polycollection to the speed
collection.set_array(-h)
collection.norm.vmin=-300
collection.norm.vmax=0


# In[ ]:

fig=figure(figsize=(12,12))
ax=fig.add_subplot(111)
m.drawmapboundary(fill_color='0.3')
#m.drawcoastlines()
#m.fillcontinents()
# add the speed as colored triangles 
ax.add_collection(collection) # add polygons to axes on basemap instance
title('FVCOM Bathymetry')

