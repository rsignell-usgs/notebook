# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=2>

# Try using Xray to convert CSV to netcdf

# <codecell>

import pandas as pd
import xray
%matplotlib inline

# <codecell>

url = 'http://www.cpc.ncep.noaa.gov/products/precip/CWlink/'

ao_file = url + 'daily_ao_index/monthly.ao.index.b50.current.ascii'
nao_file = url + 'pna/norm.nao.monthly.b5001.current.ascii'

kw = dict(sep='\s*', parse_dates={'dates': [0, 1]},
          header=None, index_col=0, squeeze=True, engine='python')

# read into Pandas Series
s1 = pd.read_csv(ao_file, **kw)
s2 = pd.read_csv(nao_file, **kw)

s1.name='AO'
s2.name='NAO'

# concatenate two Pandas Series into a Pandas DataFrame
df=pd.concat([s1, s2], axis=1)

# <codecell>

df.plot(figsize=(16,4));

# <codecell>

# create xray Dataset from Pandas DataFrame
xr = xray.Dataset.from_dataframe(df)

# <codecell>

# add variable attribute metadata
xr['AO'].attrs={'units':'1', 'long_name':'Arctic Oscillation'}
xr['NAO'].attrs={'units':'1', 'long_name':'North Atlantic Oscillation'}

# <codecell>

# add global attribute metadata
xr.attrs={'Conventions':'CF-1.0', 'title':'AO and NAO', 'summary':'Arctic and North Atlantic Oscillation Indices'}

# <codecell>

print xr

# <codecell>

# save to netCDF
xr.to_netcdf('/usgs/data2/notebook/data/ao_and_nao.nc')

