
# coding: utf-8

# # Convert all daily JSON log files for a deployment to a single NetCDF file
# using CF-1.6, Discrete Sampling Geometry (DSG) conventions, **`featureType=timeSeries`**

# In[1]:

import json
import pandas as pd
import numpy as np
import glob
import os

from pyaxiom.netcdf.sensors import TimeSeries


# In[2]:

var = 'pwrsys'
buoys = {'ce02shsm':{'lon':-124.31, 'lat':44.64, 'z':0.0},
         'ce04ossm':{'lon':-124.95, 'lat':44.37, 'z':0.0},
         'ce07shsm':{'lon':-124.57, 'lat':46.99, 'z':0.0},
         'ce09ossm':{'lon':-124.97, 'lat':46.85, 'z':0.0}
        }
# pick the last deployment
deployment_index = -1


# In[3]:

global_attributes = {
'institution':'Oregon State University', 
'title':'OOI CE02SHSM Pwrsys Data',
'summary':'OOI data from Coastal Endurance',
'creator_name':'Chris Wingard',
'creator_email':'cwingard@coas.oregonstate.edu',
'creator_url':'http://ceoas.oregonstate.edu/ooi'
}


# In[4]:

def json2df(infile):
    with open(infile) as jf:
        df = pd.DataFrame(json.load(jf))
        return df


# In[5]:

ipath = '/sand/usgs/users/rsignell/data/ooi/endurance/cg_proc/'
odir = '/usgs/data2/notebook/data/nc'
for buoy in buoys.keys():
    deployment_path = glob.glob(os.path.join(ipath,buoy,'D*'))[deployment_index]
    deployment = deployment_path.split('/')[-1]
    path = os.path.join(deployment_path,'buoy',var,'*.{}.json'.format(var))
    ofile = '{}_{}_{}.nc'.format(buoy,var,deployment)
    print(path)
    df = pd.concat([json2df(file) for file in glob.glob(path)])  
    df['time'] = pd.to_datetime(df.time, unit='s')
    df.index = df['time']
#    df['z'] = buoys[buoy]['z']

    global_attributes['title']='OOI Endurance Data:{}:{}'.format(buoy,var)
    
    ts = TimeSeries(output_directory=odir,
        latitude=buoys[buoy]['lat'],
        longitude=buoys[buoy]['lon'],
        station_name=buoy,
        global_attributes=global_attributes,
        times=df.time.values.astype(np.int64) // 10**9,
        verticals=buoys[buoy]['z'],
        output_filename=ofile,
        vertical_positive='up'
        )
    
    print(ofile)
    df.columns.tolist();
    for c in df.columns:
        if c in ts._nc.variables:
            print("Skipping '{}' (already in file)".format(c))
            continue
        if c in ['time', 'lat', 'lon', 'depth']: 
            print("Skipping axis '{}' (already in file)".format(c))
            continue
        if 'object' in df[c].dtype.name: 
            print("Skipping object {}".format(c))
            continue
        print("Adding {}".format(c))
        ts.add_variable(c, df[c].values)



# In[ ]:



