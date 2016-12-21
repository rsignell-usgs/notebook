# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
%matplotlib inline

# <codecell>

pd.__version__

# <codecell>

dataset_url = 'http://www.neracoos.org/erddap/tabledap/cwwcNDBCMet.csv?time,atmp,wtmp,wspu,wspv&station=\
%2244013%22&time>=2014-06-01T00:00:00Z&time<=2014-09-01T16:00:00Z'

# <codecell>

#dataset_file = 'Dataset.csv'

# <codecell>

#df = pd.read_csv(dataset_file, parse_dates=True, index_col='time', skiprows=[1])
df = pd.read_csv(dataset_url, parse_dates=True, index_col='time', skiprows=[1])
#df.to_csv('Dataset.csv')
df_daily = df.resample(rule='D', how='mean')

# <codecell>

df.head()
#plt.savefig('table.png')

# <codecell>

df_daily['wtmp'].plot(figsize=(10,4))
#plt.savefig('General_watertemp.png')

# <codecell>

st = dt.datetime(2014, 7, 4, 18, 0)
en = dt.datetime(2014, 7, 5, 18, 0)
df[['wtmp']][st:en].plot(figsize=(10,4))
#plt.savefig('Watertemp1.png')

# <codecell>

st = dt.datetime(2014, 7, 2, 18, 0)      #48 hours before temperature drop
en = dt.datetime(2014, 7, 4, 18, 0)
avg_wspu = df['wspu'][st:en].mean()
avg_wspv = df['wspv'][st:en].mean()

# <codecell>

print avg_wspu,avg_wspv

# <codecell>

plt.figure(figsize=(5,5))
ax = plt.gca()
lim=4
ax.arrow(0, 0, avg_wspu, avg_wspv, head_width=0.25, head_length=0.4, fc='k', ec='k')
ax.set_xlim([-lim,lim])
ax.set_ylim([-lim,lim])
ax.grid()

# <codecell>

plt.figure()
ax = plt.gca()
lim=2
ax.quiver(0,0,1,1,angles='xy',scale_units='xy',scale=1)
ax.set_xlim([-lim,lim])
ax.set_ylim([-lim,lim])
ax.grid()

# <codecell>

plt.figure(figsize=(5,5))
ax = plt.gca()
lim=5
ax.quiver([0, avg_wspu],[0, avg_wspv],angles='xy',scale_units='xy',scale=1)
ax.set_xlim([-lim,lim])
ax.set_ylim([-lim,lim])
ax.grid()
#plt.savefig('Wind1.png')

# <codecell>

#Written by Dr. Signell

import netCDF4
import matplotlib.tri as Tri

# swim route
lon_track=[-70.890150,  -70.927933,  -70.951417,  -70.976217,  -70.999150,  -71.034850]
lat_track=[ 42.327400,   42.316150,   42.314800,   42.309300,   42.322633,   42.328700]

# DAP Data URL
# MassBay GRID
url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc'
# GOM3 GRID
#url='http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc'
# Open DAP
url= 'http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/archives/necofs_mb'
nc = netCDF4.Dataset(url).variables
nc.keys()

# Desired time for snapshot in UTC 
# ....right now (or some number of hours from now) ...
#start = dt.datetime.utcnow() + dt.timedelta(hours=48)
# ... or specific time (UTC)    
start = dt.datetime(2014, 7, 3, 13, 0)  #Note: EDT = UTC - 4 hours , EST = UTC -5 hours

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
# Get depth
h = nc['h'][:]  # depth 

dtime = netCDF4.num2date(time_var[itime],time_var.units)
daystr = dtime.strftime('%Y-%b-%d %H:%M')

tri = Tri.Triangulation(lon,lat, triangles=nv)

# get current at layer [0 = surface, -1 = bottom]
ilayer = 0
u = nc['u'][itime, ilayer, :]
v = nc['v'][itime, ilayer, :]
t = nc['temp'][itime,ilayer,:]
t = 32. + t*9./5.    #convert from C to F
u = u*1.94  # convert m/s to knots
v = v*1.94  # convert m/s to knots

#boston light swim
levels=np.arange(52.,61.,1.)   # temperature contours to plot [48 to 65 in intervals of 1]
ax= [-71.10, -70.10, 41.00, 43.00] # region to plot
maxvel = 1.0 # velocity arrow scale
subsample = 9  # subsampling of velocity vectors

# find velocity points in bounding box
ind = np.argwhere((lonc >= ax[0]) & (lonc <= ax[1]) & (latc >= ax[2]) & (latc <= ax[3]))

np.random.shuffle(ind)
Nvec = int(len(ind) / subsample)
idv = ind[:Nvec]

# tricontourf plot of water depth with vectors on top
plt.figure(figsize=(20,10))
plt.subplot(111,aspect=(1.0/np.cos(lat[:].mean()*np.pi/180.0)))
#tricontourf(tri, t,levels=levels,shading='faceted',cmap=plt.cm.gist_earth)
plt.tricontourf(tri, t,levels=levels,shading='faceted')
plt.axis(ax)
plt.gca().patch.set_facecolor('0.5')
cbar=plt.colorbar()
cbar.set_label('Forecast Surface Temperature (F)', rotation=-90)
Q = plt.quiver(lonc[idv],latc[idv],u[idv],v[idv],scale=40)
maxstr='%3.1f knots' % maxvel
qk = plt.quiverkey(Q,0.92,0.08,maxvel,maxstr,labelpos='W')
plt.title('NECOFS Surface Velocity, Layer %d, %s UTC' % (ilayer, daystr))
plt.plot(lon_track,lat_track,'m-o');
plt.savefig('Fig1.png')

# <codecell>

print lonc.min()
print lonc.max()
print latc.min()
print latc.max()

# <codecell>

st = dt.datetime(2014, 7, 13, 6, 0)
en = dt.datetime(2014, 7, 14, 6, 0)
df[['wtmp']][st:en].plot(figsize=(10,10))
plt.savefig('Watertemp2.png')

# <codecell>

st = dt.datetime(2014, 7, 11, 6, 0)     #48 hours before temperature drop
en = dt.datetime(2014, 7, 13, 6, 0)
avg_wspu = df['wspu'][st:en].mean(axis=1)
avg_wspv = df['wspv'][st:en].mean(axis=1)

# <codecell>

plt.figure(figsize=(10,10))
ax = plt.gca()
lim=5
ax.quiver(0,0,avg_wspu,avg_wspv,angles='xy',scale_units='xy',scale=1)
ax.set_xlim([-lim,lim])
ax.set_ylim([-lim,lim])
ax.grid()
plt.savefig('Wind2.png')

# <codecell>

#Written by Dr. Signell

import netCDF4
import matplotlib.tri as Tri

# swim route
lon_track=[-70.890150,  -70.927933,  -70.951417,  -70.976217,  -70.999150,  -71.034850]
lat_track=[ 42.327400,   42.316150,   42.314800,   42.309300,   42.322633,   42.328700]

# DAP Data URL
# MassBay GRID
url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc'
# GOM3 GRID
#url='http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc'
# Open DAP
url= 'http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/archives/necofs_mb'
nc = netCDF4.Dataset(url).variables
nc.keys()

# Desired time for snapshot in UTC 
# ....right now (or some number of hours from now) ...
#start = dt.datetime.utcnow() + dt.timedelta(hours=48)
# ... or specific time (UTC)    
start = dt.datetime(2014, 7, 11, 1, 0)  #Note: EDT = UTC - 4 hours , EST = UTC -5 hours

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
# Get depth
h = nc['h'][:]  # depth 

dtime = netCDF4.num2date(time_var[itime],time_var.units)
daystr = dtime.strftime('%Y-%b-%d %H:%M')

tri = Tri.Triangulation(lon,lat, triangles=nv)

# get current at layer [0 = surface, -1 = bottom]
ilayer = 0
u = nc['u'][itime, ilayer, :]
v = nc['v'][itime, ilayer, :]
t = nc['temp'][itime,ilayer,:]
t = 32. + t*9./5.    #convert from C to F
u = u*1.94  # convert m/s to knots
v = v*1.94  # convert m/s to knots

#boston light swim
levels=np.arange(52.,61.,1.)   # temperature contours to plot [48 to 65 in intervals of 1]
ax= [-71.05, -70.82, 42.28, 42.38] # region to plot
maxvel = 1.0 # velocity arrow scale
subsample = 9  # subsampling of velocity vectors

# find velocity points in bounding box
ind = np.argwhere((lonc >= ax[0]) & (lonc <= ax[1]) & (latc >= ax[2]) & (latc <= ax[3]))

np.random.shuffle(ind)
Nvec = int(len(ind) / subsample)
idv = ind[:Nvec]

# tricontourf plot of water depth with vectors on top
plt.figure(figsize=(20,10))
plt.subplot(111,aspect=(1.0/np.cos(lat[:].mean()*np.pi/180.0)))
#tricontourf(tri, t,levels=levels,shading='faceted',cmap=plt.cm.gist_earth)
plt.tricontourf(tri, t,levels=levels,shading='faceted')
plt.axis(ax)
plt.gca().patch.set_facecolor('0.5')
cbar=plt.colorbar()
cbar.set_label('Forecast Surface Temperature (F)', rotation=-90)
Q = plt.quiver(lonc[idv],latc[idv],u[idv],v[idv],scale=40)
maxstr='%3.1f knots' % maxvel
qk = plt.quiverkey(Q,0.92,0.08,maxvel,maxstr,labelpos='W')
plt.title('NECOFS Surface Velocity, Layer %d, %s UTC' % (ilayer, daystr))
plt.plot(lon_track,lat_track,'m-o');
plt.savefig('Fig2.png')

# <codecell>

st = dt.datetime(2014, 8, 13, 6, 0)
en = dt.datetime(2014, 8, 14, 6, 0)
df[['wtmp']][st:en].plot(figsize=(10,10))
plt.savefig('Watertemp3.png')

# <codecell>

st = dt.datetime(2014, 8, 11, 6, 0)     #48 hours before temperature drop
en = dt.datetime(2014, 8, 13, 6, 0)
avg_wspu = df['wspu'][st:en].mean(axis=1)
avg_wspv = df['wspv'][st:en].mean(axis=1)

# <codecell>

plt.figure(figsize=(10,10))
ax = plt.gca()
lim=5
ax.quiver(0,0,avg_wspu,avg_wspv,angles='xy',scale_units='xy',scale=1)
ax.set_xlim([-lim,lim])
ax.set_ylim([-lim,lim])
ax.grid()
plt.savefig('Wind3.png')

# <codecell>

#Written by Dr. Signell

import netCDF4
import matplotlib.tri as Tri

# swim route
lon_track=[-70.890150,  -70.927933,  -70.951417,  -70.976217,  -70.999150,  -71.034850]
lat_track=[ 42.327400,   42.316150,   42.314800,   42.309300,   42.322633,   42.328700]

# DAP Data URL
# MassBay GRID
url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc'
# GOM3 GRID
#url='http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc'
# Open DAP
url= 'http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/archives/necofs_mb'
nc = netCDF4.Dataset(url).variables
nc.keys()

# Desired time for snapshot in UTC 
# ....right now (or some number of hours from now) ...
#start = dt.datetime.utcnow() + dt.timedelta(hours=48)
# ... or specific time (UTC)    
start = dt.datetime(2014, 8, 11, 1, 0)  #Note: EDT = UTC - 4 hours , EST = UTC -5 hours

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
# Get depth
h = nc['h'][:]  # depth 

dtime = netCDF4.num2date(time_var[itime],time_var.units)
daystr = dtime.strftime('%Y-%b-%d %H:%M')

tri = Tri.Triangulation(lon,lat, triangles=nv)

# get current at layer [0 = surface, -1 = bottom]
ilayer = 0
u = nc['u'][itime, ilayer, :]
v = nc['v'][itime, ilayer, :]
t = nc['temp'][itime,ilayer,:]
t = 32. + t*9./5.    #convert from C to F
u = u*1.94  # convert m/s to knots
v = v*1.94  # convert m/s to knots

#boston light swim
levels=np.arange(52.,61.,1.)   # temperature contours to plot [48 to 65 in intervals of 1]
ax= [-71.05, -70.82, 42.28, 42.38] # region to plot
maxvel = 1.0 # velocity arrow scale
subsample = 9  # subsampling of velocity vectors

# find velocity points in bounding box
ind = np.argwhere((lonc >= ax[0]) & (lonc <= ax[1]) & (latc >= ax[2]) & (latc <= ax[3]))

np.random.shuffle(ind)
Nvec = int(len(ind) / subsample)
idv = ind[:Nvec]

# tricontourf plot of water depth with vectors on top
plt.figure(figsize=(20,10))
plt.subplot(111,aspect=(1.0/np.cos(lat[:].mean()*np.pi/180.0)))
#tricontourf(tri, t,levels=levels,shading='faceted',cmap=plt.cm.gist_earth)
plt.tricontourf(tri, t,levels=levels,shading='faceted')
plt.axis(ax)
plt.gca().patch.set_facecolor('0.5')
cbar=plt.colorbar()
cbar.set_label('Forecast Surface Temperature (F)', rotation=-90)
Q = plt.quiver(lonc[idv],latc[idv],u[idv],v[idv],scale=40)
maxstr='%3.1f knots' % maxvel
qk = plt.quiverkey(Q,0.92,0.08,maxvel,maxstr,labelpos='W')
plt.title('NECOFS Surface Velocity, Layer %d, %s UTC' % (ilayer, daystr))
plt.plot(lon_track,lat_track,'m-o');
plt.savefig('Fig3.png')

