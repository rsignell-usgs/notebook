# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Time extracting points from triangular grid ocean model

# <markdowncell>

# Exploring the answer to this stackoverflow question:
#     http://stackoverflow.com/questions/26788112/easy-scriptable-way-to-sub-sample-unstructured-thredds-data

# <codecell>

import netCDF4
import time
import numpy as np

url='http://fvcom.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc'
nc = netCDF4.Dataset(url)
ncv = nc.variables
lon = ncv['lon'][:]
lat = ncv['lat'][:]
tim = ncv['time'][:]

# find indices inside box
box = [-71.4,41,-70.2,41.5]
ii = (lon>=box[0])&(lon<=box[2])&(lat>=box[1])&(lat<=box[3])
jj = where(ii)[0]

# <codecell>

# loop over indices, extracting time series
time0=time.time()
zi = np.zeros((len(tim),len(jj)))
k=0
for j in jj:
    zi[:,k]=ncv['zeta'][:,j]
    k +=1
print('elapsed time: %d seconds' % (time.time()-time0))
    

# <codecell>

# loop over time, extracting range and then indices
time0=time.time()
zi2 = np.zeros((len(tim),len(jj)))
jmin=jj.min()
jmax=jj.max()

for i in range(len(tim)):
    ztmp = ncv['zeta'][i,jmin:jmax+1]
    zi2[i,:] = ztmp[jj-jmin]
print('elapsed time: %d seconds' % (time.time()-time0))
    

