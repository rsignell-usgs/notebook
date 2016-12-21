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

v=a.extract('salt',method='fast')
z=a.depth('salt')
t2=np.tile(a.t[:,np.newaxis],(1,v.shape[1]))
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


