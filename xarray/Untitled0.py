# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import netCDF4
import pandas as pd
import numpy as np
import datetime as dt

# <codecell>

url='http://geoport.whoi.edu/thredds/dodsC/usgs/data2/emontgomery/stellwagen/Data/FI14/10001whr-cal.nc'

# <codecell>

nc = netCDF4.Dataset(url)
ncv = nc.variables

# <codecell>

t1 = np.array(ncv['time'][:] - 2440000,dtype='int64')*3600*24*1000
t2 = np.array(ncv['time2'][:], dtype='int64')
dt = dt.datetime('1968-05-23T00:00:00Z'

