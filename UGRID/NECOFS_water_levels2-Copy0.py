# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Extract NECOFS water levels using NetCDF4-Python and analyze/visualize with Pandas

# <codecell>

# Plot forecast water levels from NECOFS model from list of lon,lat locations
# (uses the nearest point, no interpolation)
import matplotlib.pyplot as plt
import numpy as np
import netCDF4
import datetime as dt
import pandas as pd
from cStringIO import StringIO
%matplotlib inline

# <codecell>

#NECOFS MassBay grid
#model='Massbay'
#url='http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc'
# GOM3 Grid
model='GOM3'
url='http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc'

# <codecell>

def dms2dd(d,m,s):
    return d+(m+s/60.)/60.
  

# <codecell>

dms2dd(41,33,15.7)

# <codecell>

-dms2dd(70,30,20.2)

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
obs=pd.read_csv(StringIO(x.strip()), sep=",\s*",index_col='Station')

# <codecell>

obs

# <codecell>

# find the indices of the points in (x,y) closest to the points in (xi,yi)
def nearxy(x,y,xi,yi):
    ind=ones(len(xi),dtype=int)
    for i in arange(len(xi)):
        dist=sqrt((x-xi[i])**2+(y-yi[i])**2)
        ind[i]=dist.argmin()
    return ind

# <codecell>

# open NECOFS remote OPeNDAP dataset 
nc=netCDF4.Dataset(url).variables

# <codecell>

# find closest NECOFS nodes to station locations
obs['0-Based Index'] = nearxy(nc['lon'][:],nc['lat'][:],obs['Lon'],obs['Lat'])
obs

# <codecell>

# get time values and convert to datetime objects
times = nc['time']
jd = netCDF4.num2date(times[:],times.units)

# <codecell>

# get all time steps of water level from each station
nsta=len(obs)
z=ones((len(jd),nsta))
for i in range(nsta):
    z[:,i] = nc['zeta'][:,obs['0-Based Index'][i]]
    

# <codecell>

# make a DataFrame out of the interpolated time series at each location
zvals=pd.DataFrame(z,index=jd,columns=obs.index)

# <codecell>

# list out a few values
zvals.head()

# <codecell>

# plotting at DataFrame is easy!
ax=zvals.plot(figsize=(16,4),grid=True,title=('NECOFS Forecast Water Level from %s Forecast' % model),legend=False);
# read units from dataset for ylabel
ylabel(nc['zeta'].units)
# plotting the legend outside the axis is a bit tricky
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5));

# <codecell>

# what is the maximum water level over this period?
zvals['Sandwich'].max()

# <codecell>

# make a new DataFrame of maximum water levels at all stations
b=pd.DataFrame(zvals.idxmax(),columns=['time of max water level (UTC)'])
# create heading for new column containing max water level
zmax_heading='zmax (%s)' % nc['zeta'].units
# Add new column to DataFrame
b[zmax_heading]=zvals.max()

# <codecell>

b

# <codecell>


# <codecell>


