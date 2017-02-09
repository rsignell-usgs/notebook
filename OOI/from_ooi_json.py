
# coding: utf-8

# # Convert OOI Parsed JSON to NetCDF file
# using CF-1.6, Discrete Sampling Geometry (DSG) conventions, **`featureType=timeSeries`**

# In[2]:

get_ipython().magic('matplotlib inline')
import json
import pandas as pd
import numpy as np

from pyaxiom.netcdf.sensors import TimeSeries


# In[6]:

infile = '/usgs/data2/notebook/data/20170130.superv.json'
infile = '/sand/usgs/users/rsignell/data/ooi/endurance/cg_proc/ce02shsm/D00004/buoy/pwrsys/20170208.pwrsys.json'

outfile = '/usgs/data2/notebook/data/20170130.superv.nc'
with open(infile) as jf:
    js = json.load(jf)
    df = pd.DataFrame({})
    for k, v in js.items():
        df[k] = v
    df['time'] = pd.to_datetime(df.time, unit='s')
    df['depth'] = 0.
df.head()


# In[7]:

df['solar_panel4_voltage'].plot();


# In[8]:

df.index = df['time']
df['solar_panel4_voltage'].plot();


# ### Define the NetCDF global attributes

# In[10]:

global_attributes = {
    'institution':'Oregon State University', 
    'title':'OOI CE02SHSM Pwrsys Data',
    'summary':'OOI Pwrsys data from Coastal Endurance Oregon Shelf Surface Mooring',
    'creator_name':'Chris Wingard',
    'creator_email':'cwingard@coas.oregonstate.edu',
    'creator_url':'http://ceoas.oregonstate.edu/ooi'
}


# ### Create initial file

# In[11]:

ts = TimeSeries(
    output_directory='.',
    latitude=44.64,
    longitude=-124.31,
    station_name='ce02shsm',
    global_attributes=global_attributes,
    times=df.time.values.astype(np.int64) // 10**9,
    verticals=df.depth.values,
    output_filename=outfile,
    vertical_positive='down'
)


# ### Add data variables

# In[12]:

for c in df.columns:
    if c in ts._nc.variables:
        print("Skipping '{}' (already in file)".format(c))
        continue
    if c in ['time', 'lat', 'lon', 'depth', 'cpm_date_time_string']:
        print("Skipping axis '{}' (already in file)".format(c))
        continue
    ts.add_variable(c, df[c].values)
    print("Added {}".format(c))
        


# In[ ]:




# ### Open the NetCDF file and inspect it

# In[9]:

import netCDF4
nc = netCDF4.Dataset(outfile)


# In[10]:

nc


# In[11]:

nc.close()


# In[12]:

import netCDF4
nc = netCDF4.Dataset(outfile)


# In[15]:

nc['z']


# In[16]:

nc['crs']


# In[19]:

nc['iridium_current']


# In[ ]:



