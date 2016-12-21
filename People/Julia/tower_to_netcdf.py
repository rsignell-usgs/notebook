# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Save Tower CSV data as NetCDF

# <markdowncell>

# ### Set local variables

# <codecell>

url='http://geoport.whoi.edu/thredds/fileServer/usgs/data2/notebook/data/CR3000_SN3557_Table1_MainTowerCR3000_ground_V6.CR3.txt'
input_data="data.txt"
output_dir="/data"
output_file="julia.nc"
fillvalue=-9999.9

# <markdowncell>

# ### Download the data

# <codecell>

import urllib
urllib.urlretrieve(url, input_data)

# <codecell>

import pandas as pd
df = pd.read_csv(input_data,skiprows=[0,2,3],
                 parse_dates=True,
                 index_col='TIMESTAMP',
                 low_memory=False,
                 na_values=['NAN',''],
                 tupleize_cols=True)
df = df.fillna(fillvalue)
df.head()

# <markdowncell>

# ### Simple plot

# <codecell>

import matplotlib.pyplot as plt
%matplotlib inline
df[['Tsoil10cmTree_Avg','Tsoil20cmTree_Avg']].plot(figsize=(12,4));

# <markdowncell>

# ### Create netCDF file

# <codecell>

import numpy as np
def pd_to_secs(df):
    # convert a pandas datetime index to seconds since 1970
    import calendar
    return np.asarray([ calendar.timegm(x.timetuple()) for x in df.index ], dtype=np.int64)

def cf_safe_name(name):
    # Create a CF safe name for a group/dimension/variable
    import re
    if isinstance(name, basestring):
        if re.match('^[0-9_]', name):
            # Add a letter to the front
            name = "v_{}".format(name)
        return re.sub(r'[^_a-zA-Z0-9]', "_", name)
    return name

# <codecell>

import os
out_file = os.path.join(output_dir, output_file)
if os.path.isfile(out_file):
    os.remove(out_file)

from pyaxiom.netcdf.sensors import TimeSeries
ts = TimeSeries(output_dir,
                latitude=0.39,
                longitude=36.7,
                station_name='urn:ioos:station:edu.princeton.ecohydrolab:MainTower',
                global_attributes={},
                times=pd_to_secs(df),
                verticals=[10],
                output_filename=output_file)

# <codecell>

for c in df.columns[::-1]:
    # Add units based on column name?
    var_attributes = dict()
    ts.add_variable(cf_safe_name(c), df[c].values, attributes=var_attributes, fillvalue=-9999.9)

# <codecell>


