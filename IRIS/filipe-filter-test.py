# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import os
from IPython.core.display import HTML
import netCDF4
import pandas as pd

# <codecell>

%matplotlib inline
from datetime import datetime

# <codecell>

url='http://geoport.whoi.edu/thredds/dodsC/usgs/data2/emontgomery/stellwagen/CF-1.6/HURRIRENE_BB/9141wh-a.nc'
nc = netCDF4.Dataset(url)
ncv = nc.variables
uvar = ncv['u_1205']
time_var = ncv['time']
jd = netCDF4.num2date(time_var[:],time_var.units)

# <codecell>

shape(uvar)

# <codecell>

u=uvar[:,15]
ts = pd.Series(u,index=jd)
ts1h = pd.rolling_mean(ts, window=10, center=True, freq='1H')
df = pd.DataFrame(ts1h,columns=['u'])

# <codecell>

shape(ts1h)

# <codecell>

roll_l = pd.rolling_mean(df['u'], window=40, center=True, freq='1H')
df.plot()

# <codecell>

import numpy as np
from oceans import lanc

window_size = 96+1+96
freq = 1./40
wt = lanc(window_size, freq)
df['low'] = np.convolve(wt, df['u'], mode='same')
df['high'] = df['u'] - df['low']

# <codecell>

import pandas as pd

roll_l = pd.rolling_mean(df['u'], window=40, center=True, freq='1H')
roll_h = df['u'] - roll_l

# <codecell>

import iris
from iris.pandas import as_cube

cube = as_cube(df['u'])

low = cube.rolling_window('index',
                        iris.analysis.SUM,
                        len(wt),
                        weights=wt)
t = low.coord('index')
t = t.units.num2date(t.points)

pad = np.zeros(window_size) * np.NaN
low = np.r_[pad, low.data, pad]

high = df['u'] - low

# <codecell>

%matplotlib inline

import matplotlib.pyplot as plt

fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, figsize=(15, 7),
                                    sharex=True, sharey=True)
x = df.index.to_pydatetime()

ax0.plot(x, df['u'], label='original')
ax0.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
           ncol=3, fancybox=True, shadow=True, numpoints=1)

ax1.plot(x, df['high'], label='lanc high')
ax1.plot(x, roll_h, label='pandas high')
ax1.plot(x, high, label='iris high')
ax1.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
           ncol=3, fancybox=True, shadow=True, numpoints=1)

ax2.plot(x, df['low'], label='lanc low')
ax2.plot(x, roll_l, label='pandas low')
ax2.plot(x, low, label='iris low')
ax2.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
           ncol=3, fancybox=True, shadow=True, numpoints=1)

# <codecell>


# <codecell>


