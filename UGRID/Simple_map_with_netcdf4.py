# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# # Simple map from NetCDF file or OPeNDAP dataset using NetCDF4

# <markdowncell>

# Extract a specific time step from a netcdf file or opendap dataset using netCDF4 and plot without spatial coordinates.  

# <markdowncell>

# Import requirements, taking care to put the "%matplotlib inline" before "import matplotlib" to avoid problems on jupyterhub servers 

# <codecell>

%matplotlib inline   
import matplotlib.pyplot as plt
import numpy as np
import netCDF4
import datetime as dt

# <markdowncell>

# Create a dictionary to hold short titles in keys, OPeNDAP Data URLS in values

# <codecell>

models = {'GFS CONUS 80km':'http://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/CONUS_80km/Best',
          'NAM CONUS 20km':'http://thredds.ucar.edu/thredds/dodsC/grib/NCEP/NAM/CONUS_20km/noaaport/Best'}

# <markdowncell>

# Pick a model

# <codecell>

name = 'NAM CONUS 20km'
url = models[name]

# <codecell>

nc = netCDF4.Dataset(url)
ncv = nc.variables
ncv.keys()

# <codecell>

# take a look at the "metadata" for the variable "u"
var_name = 'Temperature_height_above_ground'
var = ncv[var_name]
print var

# <codecell>

var.shape

# <codecell>

# Desired time for snapshot
# ....right now (or some number of hours from now) ...
start = dt.datetime.utcnow() + dt.timedelta(hours=+2)
# ... or specific time (UTC)
#start = dt.datetime(2014,9,9,0,0,0) + dt.timedelta(hours=-1)

# <markdowncell>

# Identify the time coordinate from the "coordinates" attribute

# <codecell>

var.coordinates

# <markdowncell>

# We want time, not reftimes.  Extract the index closest to the specified time

# <codecell>

time_var = ncv['time']
itime = netCDF4.date2index(start,time_var,select='nearest')

# <markdowncell>

# Access data at specified time step and level

# <codecell>

lev = 0
t = var[itime,lev,:,:]
t.shape

# <markdowncell>

# Make a nice time stamp string

# <codecell>

tm = netCDF4.num2date(time_var[itime],time_var.units)
daystr = tm.strftime('%Y-%b-%d %H:%M UTC')

# <markdowncell>

# Make a pcolormesh plot of the data

# <codecell>

fig=plt.figure(figsize=(18,10))
plt.pcolormesh(t)
cbar = plt.colorbar()
plt.title('%s:%s, %s, Level %d' % (name, daystr, var_name, lev));

