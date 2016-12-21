# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=2>

# ROMS Glider

# <markdowncell>

# Virtual glider extraction: (lon,lat,time) interpolation from ROMS files

# <codecell>

%matplotlib inline
from okean.roms import glider
from okean import netcdf
import numpy as np
import matplotlib.pyplot as plt

# <markdowncell>

# Lets use some ROMS-ESPRESSO output and load info from a glider:

# <codecell>

froms='http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2009_da/his'
fglider='http://tds.marine.rutgers.edu/thredds/dodsC/cool/glider/mab/Gridded/20101025T1600_marcoos_ru22_active.nc'

x=netcdf.use(fglider,'longitude')
y=netcdf.use(fglider,'latitude')
t=netcdf.nctime(fglider,'time')

a=glider.RomsGlider(froms,x,y,t)
a.plot()

# <markdowncell>

# Extract and plot the glider data

# <codecell>

vmin=30.0
vmax=36.0
z=netcdf.use(fglider,'depth')
s=netcdf.use(fglider,'salinity')
fig = plt.figure(figsize=(12,4))
plt.pcolormesh(t,z,s.T,vmin=vmin,vmax=vmax)
plt.colorbar()

wk=plt.matplotlib.dates.WeekdayLocator()
fmt=plt.matplotlib.dates.DateFormatter('%d-%b-%Y')
ax=plt.gca()
ax.xaxis.set_major_locator(wk)
ax.xaxis.set_major_formatter(fmt)
plt.title('Observed Glider data: 20101025T1600_marcoos_ru22_active.nc)');

# <markdowncell>

# Extract and plot a ROMS variable:

# <codecell>

v=a.extract('salt',method='fast')
z=a.depth('salt')
t2=np.tile(a.t[:,np.newaxis],(1,v.shape[1]))

# <codecell>

fig = plt.figure(figsize=(12,4))
plt.pcolormesh(t2,z,v,vmin=vmin,vmax=vmax)
plt.colorbar()

wk=plt.matplotlib.dates.WeekdayLocator()
fmt=plt.matplotlib.dates.DateFormatter('%d-%b-%Y')
ax=plt.gca()
ax.xaxis.set_major_locator(wk)
ax.xaxis.set_major_formatter(fmt)
plt.title('Virtual Glider data from ROMS');

# <codecell>

zeta=a.extract('zeta',quiet=1)
fig = plt.figure(figsize=(12,4))
plt.plot(a.t,zeta)

ax=plt.gca()
ax.xaxis.set_major_locator(wk)
ax.xaxis.set_major_formatter(fmt)

# <markdowncell>

# Different data extraction methods:
# - It is not possible to extract vectors from a >2d netcdf file, so data can be extracted for every needed cell, ie, one xyt point per data access, or the nd array including all the cells needed can be extracted. In the second case, the user can however split the proccess in time, resulting in more accesses, but less data extracted. The split can be linear in the time or user can choose the spltting time indices. Let's try the linear split with different number of accesses:

# <codecell>

import time
t0=time.time()
a.extract('salt',method='fast',quiet=1) # one data access, more data extracted
print '%4.2f min'%((time.time()-t0)/60.)
t0=time.time()
a.extract('salt',method='fast',nfast=5,quiet=1) # 5 data accesses, less data extracted
print '%4.2f min'%((time.time()-t0)/60.)
t0=time.time()
a.extract('salt',method='fast',nfast=10,quiet=1) # 10 data accesses
print '%4.2f min'%((time.time()-t0)/60.)
t0=time.time()
a.extract('salt',method='fast',nfast=20,quiet=1) # 20 data accesses
print '%4.2f min'%((time.time()-t0)/60.)

# <markdowncell>

# - Using nonlinear data splitting (nfast as list) should be the fastest method and the one which extracts less data, but only if the right time indices are choosen. The perfect solution should be choosing time splitting based on cluster analysis, so that the number of accesses and the size of the data cubes extracted would be optimized. A simple example:

# <codecell>

it0=a.uinds['r'][:,2].min()
it1=a.uinds['r'][:,2].max()+1
it=it0,it0+50,it1
t0=time.time()
v=a.extract('salt',method='fast',nfast=it,quiet=1)
print '%4.2f min'%((time.time()-t0)/60.)
fig = plt.figure(figsize=(12,4))
plt.pcolormesh(t2,z,v,vmin=vmin,vmax=vmax)
plt.colorbar()

ax=plt.gca()
ax.xaxis.set_major_locator(wk)
ax.xaxis.set_major_formatter(fmt)
plt.title('Virtual Glider data from ROMS');

# <codecell>


