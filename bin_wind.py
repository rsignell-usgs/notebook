# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import netCDF4
%matplotlib inline
from scipy.stats import binned_statistic_2d
import datetime as dt
import pandas as pd
import oceans
import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma

# <codecell>

url='http://dods.ndbc.noaa.gov/thredds/dodsC/data/stdmet/brbn4/brbn4.ncml'
nc = netCDF4.Dataset(url)
ncv = nc.variables

# <codecell>

ncv.keys()

# <codecell>

time_var = ncv['time']
dtime = netCDF4.num2date(time_var[:],time_var.units)

# <codecell>

# Extract desired times.  Here we select a specific time of interest
start = dt.datetime(2010,8,1,0,0,0)
istart = netCDF4.date2index(start,time_var,select='nearest')
stop = dt.datetime(2010,9,1,0,0,0)
istop = netCDF4.date2index(stop,time_var,select='nearest')

# <codecell>

# Get all time records of variable [vname] at indices [iy,ix]
vname = 'wind_spd'
var = ncv[vname]
var.shape
wspd = var[istart:istop,:,:].ravel()

# <codecell>

vname = 'wind_dir'
var = ncv[vname]
var.shape
wdir = var[istart:istop,:,:].ravel()

# <codecell>

tim = dtime[istart:istop]

# <codecell>

# Create Pandas time series object
ts = pd.Series(wspd,index=tim)

# <codecell>

ts.plot()

# <codecell>

u,v = oceans.spdir2uv(wspd,wdir,deg=True)

# <codecell>

fig=plt.figure(figsize=(12,4))
plt.plot(tim,u,tim,v)

# <codecell>

f1,x,y,bin1 = binned_statistic_2d(u, v, u, statistic='mean', bins=10, range=None)
f2,x,y,bin2 = binned_statistic_2d(u, v, v, statistic='mean', bins=10, range=None)

# <codecell>

u

# <codecell>

url='http://tds.marine.rutgers.edu/thredds/dodsC/met/ncdc-nam-3hour/Uwind_nam_3hourly_MAB_and_GoM_2009.nc'
nc = netCDF4.Dataset(url)
ncv = nc.variables
print ncv.keys()

# <codecell>

url='http://tds.marine.rutgers.edu/thredds/dodsC/met/ncdc-nam-3hour/Uwind_nam_3hourly_MAB_and_GoM_2009.nc'
vname = 'Uwind'
nc = netCDF4.Dataset(url)
ncv = nc.variables
time_var = ncv['time']
dtime = netCDF4.num2date(time_var[:],time_var.units)
istart = netCDF4.date2index(start,time_var,select='nearest')
istop = netCDF4.date2index(stop,time_var,select='nearest')
var = ncv[vname]
j=78
i=69
v = var[istart:istop,j,i]
tim = dtime[istart:istop]

# <codecell>

tim

# <codecell>

istart

# <codecell>

def get_nam_ts(url,vname,start=None,stop=None,j=None,i=None):
    nc = netCDF4.Dataset(url)
    ncv = nc.variables
    time_var = ncv['time']
    dtime = netCDF4.num2date(time_var[:],time_var.units)
    istart = netCDF4.date2index(start,time_var,select='nearest')
    istop = netCDF4.date2index(stop,time_var,select='nearest')
    var = ncv[vname]
    v = var[istart:istop,j,i]
    tim = dtime[istart:istop]
    return v,tim
    

# <codecell>

ncv.keys()

# <codecell>

time_var = ncv['time']
dtime = netCDF4.num2date(time_var[:],time_var.units)

# <codecell>

# Extract desired times.  Here we select a specific time of interest
start = dt.datetime(2009,1,1,0,0,0)
stop = dt.datetime(2009,12,1,0,0,0)


url='http://tds.marine.rutgers.edu/thredds/dodsC/met/ncdc-nam-3hour/Uwind_nam_3hourly_MAB_and_GoM_2009.nc'
vname = 'Uwind'
u,tim = get_nam_ts(url,vname=vname,start=start,stop=stop,j=78,i=69)

url='http://tds.marine.rutgers.edu/thredds/dodsC/met/ncdc-nam-3hour/Vwind_nam_3hourly_MAB_and_GoM_2009.nc'
vname = 'Vwind'
v,tim = get_nam_ts(url,vname=vname,start=start,stop=stop,j=78,i=69)

fig = plt.figure(figsize=(16,4))
plt.plot(tim,u,tim,v)
plt.grid()

# <codecell>

# since we are binning both u and v the bins will be the same for u and v
ubin,x,y,bin1 = binned_statistic_2d(u, v, u, statistic='mean', bins=10, range=None)
vbin,x,y,bin2 = binned_statistic_2d(u, v, v, statistic='mean', bins=10, range=None)

# <codecell>


ubin = ma.masked_invalid(ubin)
vbin = ma.masked_invalid(vbin)

# <codecell>

plt.pcolormesh(x,y,vbin)

# <codecell>

dirbin,spdbin = oceans.uv2spdir(ubin,vbin)
spdbin = ma.masked_invalid(spdbin)
plt.pcolormesh(x,y,spdbin)

# <codecell>

dir, spd = oceans.uv2spdir(u,v)

# <codecell>

ind = np.where((spd>=3.6) & (spd<=10.8))[0]

# <codecell>

len(ind)*1.0/len(spd)

# <codecell>

hist, bin_edges = np.histogram(dir[ind],18)
bottom = bin_edges[:-1] 
heights = np.diff(bin_edges)
plt.barh(bottom,hist,height=heights)
#plt.barh(bin_edges,hist)

# <codecell>

d, s = oceans.uv2spdir(0,1)
print d,s

# <codecell>

d,s = oceans.uv2spdir(0,0)
print d,s

# <codecell>

heights

# <codecell>

centers

# <codecell>

hist

# <codecell>

7-21 

