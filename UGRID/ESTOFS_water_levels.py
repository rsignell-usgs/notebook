# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# #Extract ESTOFS water levels using NetCDF4-Python and analyze/visualize with Pandas

# <codecell>

# Plot forecast water levels from NECOFS model from list of lon,lat locations
# (uses the nearest point, no interpolation)
%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
import netCDF4
import datetime as dt
import pandas as pd
from StringIO import StringIO
import matplotlib.tri as Tri

# <codecell>

#NECOFS MassBay grid
#url='http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc'
# GOM3 Grid
#model='GOM3'
url='http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc'
#ESTOFS
url='http://geoport-dev.whoi.edu/thredds/dodsC/estofs/atlantic'

# <codecell>

# open NECOFS remote OPeNDAP dataset 
nc=netCDF4.Dataset(url)
ncv = nc.variables
print nc.title

# <codecell>

# Get lon,lat coordinates for nodes (depth)
lat = ncv['y'][:]
lon = ncv['x'][:]
h = ncv['depth'][:]
# Get Connectivity array
nv = ncv['element'][:].T - 1 

# <codecell>

tri = Tri.Triangulation(lon,lat, triangles=nv.T)

# <codecell>

# Plot model domain
plt.figure(figsize=(18,10))
plt.subplot(111,adjustable='box',aspect=(1.0/np.cos(lat.mean()*np.pi/180.0)))
plt.tricontourf(tri, -h,50,shading='flat');

# <codecell>

# Enter desired (Station, Lat, Lon) values here:
x = '''
Station, Lat, Lon
Boston,             42.368186, -71.047984
Scituate Harbor,    42.199447, -70.720090
Scituate Beach,     42.209973, -70.724523
Falmouth Harbor,    41.541575, -70.608020
Marion,             41.689008, -70.746576
Marshfield,         42.108480, -70.648691
Provincetown,       42.042745, -70.171180
Sandwich,           41.767990, -70.466219
Hampton Bay,        42.900103, -70.818510
Gloucester,         42.610253, -70.660570
'''

# <codecell>

# Create a Pandas DataFrame
obs=pd.read_csv(StringIO(x.strip()), sep=",\s*",index_col='Station', engine='python')

# <codecell>

obs

# <codecell>

# find the indices of the points in (x,y) closest to the points in (xi,yi)
def nearxy(x,y,xi,yi):
    ind = np.ones(len(xi),dtype=int)
    for i in xrange(len(xi)):
        dist = np.sqrt((x-xi[i])**2+(y-yi[i])**2)
        ind[i] = dist.argmin()
    return ind

# <codecell>

# find closest NECOFS nodes to station locations
obs['0-Based Index'] = nearxy(ncv['x'][:],ncv['y'][:],obs['Lon'],obs['Lat'])
obs

# <codecell>

# Desired time for snapshot
# ....right now (or some number of hours from now) ...
start = dt.datetime.utcnow() + dt.timedelta(hours=-72)
stop = dt.datetime.utcnow() + dt.timedelta(hours=+72)
# ... or specific time (UTC)
#start = dt.datetime(2014,9,9,0,0,0) + dt.timedelta(hours=-1)

# <codecell>

timev = ncv['time']
istart = netCDF4.date2index(start,timev,select='nearest')
istop = netCDF4.date2index(stop,timev,select='nearest')
jd = netCDF4.num2date(timev[istart:istop],timev.units)

# <codecell>

# get all time steps of water level from each station
nsta = len(obs)
z =  np.ones((len(jd),nsta))
for i in range(nsta):
    z[:,i] = ncv['zeta'][istart:istop,obs['0-Based Index'][i]]
    

# <codecell>

# make a DataFrame out of the interpolated time series at each location
zvals=pd.DataFrame(z,index=jd,columns=obs.index)

# <codecell>

# list out a few values
zvals.head()

# <codecell>

# plotting at DataFrame is easy!
ax = zvals.plot(figsize=(16,6),grid=True,title=('Forecast Water Level from %s Forecast' % nc.title),legend=False);
# read units from dataset for ylabel
plt.ylabel(ncv['zeta'].units)
# plotting the legend outside the axis is a bit tricky
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5));

# <codecell>

# make a new DataFrame of maximum water levels at all stations
b=pd.DataFrame(zvals.idxmax(),columns=['time of max water level (UTC)'])
# create heading for new column containing max water level
zmax_heading='zmax (%s)' % ncv['zeta'].units
# Add new column to DataFrame
b[zmax_heading]=zvals.max()

# <codecell>

b

# <codecell>

zvals.describe()

# <codecell>


# <codecell>


