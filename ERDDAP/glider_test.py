# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Try search and access of glider data

# <codecell>

import json, requests

url = 'http://erddap.marine.rutgers.edu/erddap/search/advanced.json'

params = dict(
    page='1',
    itemsPerPage='1000',
    searchFor='',
    protocol='(ANY)',
    cdm_data_type='(ANY)',
    institution='(ANY)',
    ioos_category='(ANY)',
    keywords='(ANY)',
    long_name='(ANY)',
    standard_name='sea_water_temperature',
    variableName='(ANY)',
    maxLat='37.78803',
    minLon='-75.5659',
    maxLon='-74.2846',
    minLat='37.0371',
    minTime='2013-09-23T00%3A00%3A00Z',
    maxTime='2013-10-18T00%3A00%3A00Z'
)

# <codecell>

resp = requests.get(url=url, params=params)
data = json.loads(resp.text)

# <codecell>

data['table']['rows'][0][:]

# <markdowncell>

# Tell ERDDAP to save as NetCDF CF-1.6 multidimensional array

# <codecell>

url='http://erddap.marine.rutgers.edu/erddap/tabledap/ru22-20130924T2010.ncCF?time,latitude,longitude,depth,temperature&trajectory=%22ru22-20130924T2010%22'

# <codecell>

import urllib

# <codecell>

urllib.urlretrieve(url,'glider.nc')

# <codecell>

import netCDF4

# <codecell>

nc = netCDF4.Dataset('glider.nc')
ncv = nc.variables
print ncv.keys()

# <codecell>

print unique(ncv['profile_id'][:])
print unique(ncv['trajectoryIndex'][:])

# <codecell>

import pandas as pd

# <codecell>

print shape(ncv['latitude'])
print shape(ncv['temperature'])
print shape(ncv['depth'])

# <codecell>

t = np.squeeze(ncv['temperature'][:,:,:])
d = np.squeeze(ncv['depth'][:,:,:])
lon = np.squeeze(ncv['longitude'][:,:])
lat = np.squeeze(ncv['latitude'][:,:])

# <codecell>

shape(t)

# <codecell>

pcolormesh(lon.T,d.T,t.T);

# <codecell>


