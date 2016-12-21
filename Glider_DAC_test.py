# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Testing Glider DAC access in Python

# <codecell>

import numpy as np
import matplotlib.pyplot as plt
import netCDF4
import numpy.ma as ma
import seawater
%matplotlib inline

# <markdowncell>

# This is a url from Kerfooot's TDS server, using the multidimensional NetCDF datasets created by a private ERDDAP instance.  These multidimensonal datasets are also available from ERDDAP, along with a flattened NetCDF representation and a ragged NetCDF representation.
# 
# The glider ERDDAP is here:
# http://erddap.marine.rutgers.edu/erddap
# 
# The glider TDS is here: http://tds.marine.rutgers.edu:8080/thredds/catalog/cool/glider/all/catalog.html

# <codecell>

url = 'http://tds.marine.rutgers.edu:8080/thredds/dodsC/cool/glider/all/ru22-20130924T2010.ncCFMA.nc3.nc'

# <codecell>

nc = netCDF4.Dataset(url)
ncv = nc.variables

# <codecell>

ncv.keys()

# <codecell>

lon = ncv['longitude'][:]
lat = ncv['latitude'][:]

# <codecell>

import iris

# <codecell>

t = iris.load_cube(url,'sea_water_temperature')

# <codecell>

print t

# <codecell>

lon=t.coord(axis='X')

# <codecell>

lat=t.coord(axis='Y')

# <codecell>

z = t.coord(axis='Z')

# <codecell>

tvar = t.coord(axis='T')

# <codecell>

shape(t)

# <codecell>

tvals= t[0,::5,::2].data

# <codecell>

tvals=ma.masked_where(tvals==-999.,tvals)

# <codecell>

pcolormesh(flipud(tvals.T));colorbar()

# <codecell>

dist, pha = seawater.extras.dist(lat.points[0],lon.points[0],units='km')

# <codecell>

d = np.cumsum(dist)
d = np.insert(d,0,0)

# <codecell>

print shape(d)

# <codecell>

x = (d*np.ones([680,1])).T

# <codecell>

zval = z.points

# <codecell>

shape(zval)

# <codecell>

print shape(x[::5,::2])
print shape(zval[0,::5,::2])
print shape(tvals)

# <codecell>

shape(x)

# <codecell>

pcolormesh(x[::5,::2],zval[0,::5,::2],tvals)

