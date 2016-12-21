# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=2>

# ROMS Glider

# <markdowncell>

# Virtual glider extraction: (lon,lat,time) interpolation from ROMS files using the OKEAN python package: https://github.com/martalmeida/okean

# <codecell>

%matplotlib inline
from okean.roms import glider
from okean import netcdf
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import MO, TU, WE, TH, FR, SA, SU

# <markdowncell>

# Lets use some ROMS-ESPRESSO output and load info from a glider:

# <codecell>

froms='http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2009_da/his'
fglider='http://tds.marine.rutgers.edu/thredds/dodsC/cool/glider/mab/Gridded/20121025T000000_20121105T000000_maracoos_ru23.nc'

x=netcdf.use(fglider,'longitude')
y=netcdf.use(fglider,'latitude')
t=netcdf.nctime(fglider,'time')

a=glider.RomsGlider(froms,x,y,t)
a.plot()

# <markdowncell>

# Extract and plot the glider data

# <codecell>

z=netcdf.use(fglider,'depth')
v=netcdf.use(fglider,'temperature')

# <codecell>

print z.shape
print v.shape
print t.shape

# <codecell>

vmin=10.0
vmax=17.0
fig = plt.figure(figsize=(12,4))
plt.pcolormesh(t,z,v.T,vmin=vmin,vmax=vmax)
plt.ylim([-60,0])
plt.colorbar()

wk=plt.matplotlib.dates.WeekdayLocator(byweekday=MO)
fmt=plt.matplotlib.dates.DateFormatter('%d-%b-%Y')
ax=plt.gca()
ax.xaxis.set_major_locator(wk)
ax.xaxis.set_major_formatter(fmt)
plt.title('Observed Glider data: 20121025T000000_20121105T000000_maracoos_ru23.nc)');

# <markdowncell>

# Extract and plot a ROMS-Espresso variable:

# <codecell>

v2=a.extract('temp',method='fast')
z2=a.depth('temp')
t2=np.tile(a.t[:,np.newaxis],(1,v2.shape[1]))

# <markdowncell>

# Plot with same vertical scale as obs data

# <codecell>

fig = plt.figure(figsize=(12,4))
plt.pcolormesh(t2,z2,v2,vmin=vmin,vmax=vmax)
plt.ylim([-60,0])
plt.colorbar()

wk=plt.matplotlib.dates.WeekdayLocator(byweekday=MO)
fmt=plt.matplotlib.dates.DateFormatter('%d-%b-%Y')
ax=plt.gca()
ax.xaxis.set_major_locator(wk)
ax.xaxis.set_major_formatter(fmt)
plt.title('Virtual Glider data from ROMS Espresso');

# <codecell>

fig = plt.figure(figsize=(12,4))
plt.pcolormesh(t2,z2,v2,vmin=vmin,vmax=vmax)
plt.colorbar()

wk=plt.matplotlib.dates.WeekdayLocator(byweekday=MO)
fmt=plt.matplotlib.dates.DateFormatter('%d-%b-%Y')
ax=plt.gca()
ax.xaxis.set_major_locator(wk)
ax.xaxis.set_major_formatter(fmt)
plt.title('Virtual Glider data from ROMS Espresso');

# <codecell>


# <codecell>


