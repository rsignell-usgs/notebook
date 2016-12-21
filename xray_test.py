# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import xray
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
%matplotlib inline

# <codecell>

URL = 'http://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_0p5deg/Best'

# <codecell>

ds = xray.open_dataset(URL)

# <codecell>

# select lat,lon region of interest
# note: slice(20.5,55.0) fails
dsloc = ds.sel(lon=slice(230.5,300.0),lat=slice(55.0,20.5))

# <codecell>

# select closest data to time of interest
date = datetime.datetime(2015,7,15,3,0,0)
#date = datetime.datetime.now()
ds_snapshot = dsloc.sel(time1=date,method='nearest')

# <codecell>

# ds.data_vars
# ds.coords
# ds.attrs

# <codecell>

t = ds_snapshot['Temperature_surface']

# <codecell>

t.shape

# <codecell>

plt.pcolormesh(t.lon.data,t.lat.data,t.data)
plt.title(t.name+pd.Timestamp(t.time.values).strftime(': %Y-%m-%d  %H:%M:%S %Z %z'));

# <codecell>

# time series closest to specified lon,lat location
ds_series = ds.sel(lon=250.,lat=33.,method='nearest')

# <codecell>

# Select temperature and convert to Pandas Series
v_series = ds_series['Temperature_surface'].to_series()

# <codecell>

v_series.plot(title=v_series.name);

# <codecell>

ds_snapshot.to_netcdf('ds_snapshot.nc')

# <codecell>

ds_snapshot

# <codecell>


