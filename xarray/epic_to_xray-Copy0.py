# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import netCDF4
import pandas as pd
import numpy as np
%matplotlib inline

# <codecell>

url='http://geoport.whoi.edu/thredds/dodsC/usgs/data2/emontgomery/stellwagen/Data/FI14/10001whp-cal.nc'

# <codecell>

ds = netCDF4.Dataset(url)
dsv = ds.variables

# <codecell>

def convert_epic_time(ds):
    """ convert EPIC time and time2 variables to datenum64 """
    dsv = ds.variables
    t1 = np.array(dsv['time'][:] - 2440000,dtype='int64')*3600*24*1000
    t2 = np.array(dsv['time2'][:], dtype='int64')
    dt64 = [np.datetime64('1968-05-23T00:00:00Z') + np.timedelta64(a,'ms') for a in t1+t2]
    return dt64

# <codecell>

# if we find a time2 variable, convert EPIC time and time2 variables to datetime64 object
if 'time2' in ds.data_vars.keys():
    dt64 = convert_epic_time(ds)

# <codecell>

pd.DataFrame(index=dt64, data=

# <codecell>

ds.data_vars

# <codecell>

df = ds.data_vars['hght_18'].to_dataframe()

# <codecell>

df.plot(figsize=(12,4))

# <codecell>

t1.dtype()

# <codecell>

t1.type

# <codecell>

t1.dtype

# <codecell>

t2.dtype

# <codecell>


