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
#fglider='http://tds.marine.rutgers.edu/thredds/dodsC/cool/glider/mab/Gridded/20101025T1600_marcoos_ru22_active.nc'
fglider='http://tds.marine.rutgers.edu:8080/thredds/dodsC/cool/glider/all/ru23-20121025T1944.ncCFMA.nc3.nc'
x=netcdf.use(fglider,'longitude')
y=netcdf.use(fglider,'latitude')
t=netcdf.nctime(fglider,'time')

# <codecell>

a=glider.RomsGlider(froms,x,y,t)
fig = plt.figure(figsize=(12,12))
a.plot()

# <markdowncell>

# Extract and plot the glider data

# <codecell>

z=netcdf.use(fglider,'depth')
v=netcdf.use(fglider,'temperature')

# <codecell>

print v.shape
print z.shape
print t.shape

# <codecell>

#t=np.tile(t,(362,1)).T
t.shape

# <codecell>

vmin=10.0
vmax=17.0
fig = plt.figure(figsize=(12,4))
plt.pcolormesh(t,-z.T,v.T,vmin=vmin,vmax=vmax)
plt.colorbar()

wk=plt.matplotlib.dates.WeekdayLocator(byweekday=MO)
fmt=plt.matplotlib.dates.DateFormatter('%d-%b-%Y')
ax=plt.gca()
ax.xaxis.set_major_locator(wk)
ax.xaxis.set_major_formatter(fmt)
plt.title('Observed Glider data: ru23-20121025T1944)');

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


