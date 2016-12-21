# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import xray
import pandas as pd
import numpy as np
%matplotlib inline
import datetime as dt

# <codecell>

url='http://geoport.whoi.edu/thredds/dodsC/usgs/data2/emontgomery/stellwagen/Data/FI14/10001whr-cal.nc'

# <codecell>

ds = xray.open_dataset(url)

# <codecell>

def convert_epic_time(ds):
    """ convert EPIC time and time2 variables to datenum64 """
    t1 = np.array(ds.coords['time'].values - 2440000,dtype='int64')*3600*24*1000
    t2 = np.array(ds.data_vars['time2'].values, dtype='int64')
    dt64 = [np.datetime64('1968-05-23T00:00:00Z') + np.timedelta64(a,'ms') for a in t1+t2]
    ds.coords['time'] = dt64

# <codecell>

# if we find a time2 variable, convert EPIC time and time2 variables to datetime64 object
if 'time2' in ds.data_vars.keys():
    convert_epic_time(ds)

# <codecell>

ds.coords['time'][0]

# <codecell>

ds.data_vars

# <codecell>

ds2 = ds.data_vars['press'].loc['2014-02-07':'2014-02-10'].isel(sample=0)

# <codecell>

df = ds2.to_dataframe()

# <codecell>

df2 = df.reset_index().set_index('time').drop(['lon', 'lat', 'sample'], axis=1)

# <codecell>

df2.plot(figsize=(12,4))

# <codecell>

ds3 = ds.sel(time=dt.datetime(2014,2,8,1),method='nearest')

# <codecell>

dvar = ds3.data_vars['vel'].sel(beambin=0)
dvar = ds3.data_vars['press']
# why does this return 10 values?
#ds3 = ds.data_vars['press'].isel(time=0)
df3 = dvar.to_dataframe()

# <codecell>

coord_list = dvar.coords.keys()

# <codecell>

#create a drop list (by removing the dimension we want to keep)
idx = 'sample'
coord_list.remove(idx)
df3 = df3.reset_index().set_index(idx).drop(coord_list, axis=1)

# <codecell>

df3.head()

# <codecell>

df3.plot(figsize=(12,4))

# <codecell>

df3.head()

# <codecell>

ds3

# <codecell>

!git add epic_to_xray*

# <codecell>

cd /usgs/data2/notebook/xray

# <codecell>

!git commit -m 'adding epic_to_xray'

# <codecell>

!git push

# <codecell>


