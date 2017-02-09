
# coding: utf-8

# # Convert all daily JSON log files for a deployment to a single NetCDF file
# using CF-1.6, Discrete Sampling Geometry (DSG) conventions, **`featureType=timeSeries`**

# In[1]:

get_ipython().magic('matplotlib inline')
import json
import pandas as pd
import numpy as np
import glob

from pyaxiom.netcdf.sensors import TimeSeries


# In[2]:

path = '/sand/usgs/users/rsignell/data/ooi/endurance/cg_proc/ce02shsm/D00004/buoy/pwrsys/*.pwrsys.json'
odir = '/usgs/data2/notebook/data/nc'
ofile = 'ce02shsm_pwrsys_D00004.nc'


# In[3]:

def json2df(infile):
    with open(infile) as jf:
        df = pd.DataFrame(json.load(jf))
        return df


# In[4]:

# single dataframe from all JSONs
df = pd.concat([json2df(file) for file in glob.glob(path)])


# In[5]:

df['time'] = pd.to_datetime(df.time, unit='s')
df.index = df['time']
df['depth'] = 0.0


# In[6]:

df['solar_panel4_voltage'].plot();


# ### Define the NetCDF global attributes

# In[7]:

global_attributes = {
    'institution':'Oregon State University', 
    'title':'OOI CE02SHSM Pwrsys Data',
    'summary':'OOI Pwrsys data from Coastal Endurance Oregon Shelf Surface Mooring',
    'creator_name':'Chris Wingard',
    'creator_email':'cwingard@coas.oregonstate.edu',
    'creator_url':'http://ceoas.oregonstate.edu/ooi'
}


# ### Create initial file

# In[8]:

ts = TimeSeries(
    output_directory=odir,
    latitude=44.64,
    longitude=-124.31,
    station_name='ce02shsm',
    global_attributes=global_attributes,
    times=df.time.values.astype(np.int64) // 10**9,
    verticals=df.depth.values,
    output_filename=ofile,
    vertical_positive='down'
)


# ### Add data variables

# In[9]:

df.columns.tolist()


# In[10]:

for c in df.columns:
    if c in ts._nc.variables:
        print("Skipping '{}' (already in file)".format(c))
        continue
    if c in ['time', 'lat', 'lon', 'depth', 'cpm_date_time_string']:
        print("Skipping axis '{}' (already in file)".format(c))
        continue
    print("Adding {}".format(c))
    try:
        ts.add_variable(c, df[c].values)
    except:
        print('skipping, hit object')
        


# In[13]:

df['error_flag1'].dtype.name


# In[ ]:



