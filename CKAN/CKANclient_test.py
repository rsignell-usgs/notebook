# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# # Testing data.noaa.gov using the CKAN API

# <markdowncell>

# We want to find all Data.gov datasets that match a specific type of data (e.g. `sea_water_temperature`), in a specified geospatial extent and time window, and that have a specific type of data endpoint (e.g. OPeNDAP).  Since data.gov uses CKAN, while waiting for a CSW interface, here we try using the CKAN API with the  `ckanclient` package.

# <codecell>

import ckanclient
import pandas as pd
from pprint import pprint

# <codecell>

ckan = ckanclient.CkanClient('http://catalog.data.gov/api/3')
#ckan = ckanclient.CkanClient('https://data.noaa.gov/api/3')

# <markdowncell>

# Try a keyword search: 

# <codecell>

search_params = { 'q': 'tags:"sea_water_temperature" '}
d = ckan.action('package_search', **search_params) 
print d['count']

# <markdowncell>

# Let's try a more complicated search:

# <codecell>

search_params = {                                           
    'q': 'tags:"sea_water_temperature" AND metadata_modified:[2012-06-01T00:00:00.000Z TO NOW]',  
    'fq': 'res_format:HTML',                                
    'extras': {"ext_bbox":"-71.5,41.,-63,46.0"},                   
    'rows': 3                                                     
}
d = ckan.action('package_search', **search_params) 
print d['count']

# <markdowncell>

# Try to find Bodega data through a restricted bounding box:

# <codecell>

search_params = {  
    'q': 'tags:"sea_water_temperature"', 
    'extras': {"ext_bbox":"-125,38,-122,39"},
    'rows': 10  
}
      
d = ckan.action('package_search', **search_params) 
print d['count']

# <markdowncell>

# Did we find it?

# <codecell>

for rec in d['results']:
    print rec['title']

# <markdowncell>

# Find all NetCDF data:

# <codecell>

search_params = { 
    'fq': 'res_format:WMS',
}
      
d = ckan.action('package_search', **search_params) 
print d['count']

# <codecell>

search_params = { 
    'q': 'mvco', 
    'fq': 'res_format:WMS',
    'rows': 10 
}
      
d = ckan.action('package_search', **search_params) 
print d['count']

# <markdowncell>

# So what does one of these results look like? Let's take a look at the keys

# <codecell>

print d['results'][0].keys()

# <markdowncell>

# Now let's see what the urls looks like for all the resources

# <codecell>

pprint(d['results'][0]['resources'])

# <markdowncell>

# So there are multiple resources for each record.  Let's check out a some specific resource parameters for all datasets to see how the service endpoints might be defined:

# <codecell>

urls=[]
for item in d['results']:
    for member in item['resources']:
        print 'url:',member['url']
        print 'resource_locator_protocol:',member['resource_locator_protocol']
        print 'resource_type:',member['resource_type']
        print 'format:',member['format'],'\n'
        if member['format'] == 'NetCDF' or member['resource_locator_protocol'] == 'THREDDS':
            urls.append(member['url'])
        

# <markdowncell>

# Lots of missing metadata information.  

# <codecell>

print(urls)

# <markdowncell>

# Hmmm... None of above URLs work. The THREDDS catalog exists, but none of the datasets here are in that catalog  <http://ecowatch.ncddc.noaa.gov/thredds/catalog/ocean_exploration_research/catalog.html> 

# <codecell>


# <markdowncell>

# Let's back off and see what the broader search yields:

# <codecell>

search_params = { 'q': 'tags:"sea_water_temperature"',
     'extras': {"ext_bbox":"-60,60,-50,70"}
} 
d = ckan.action('package_search', **search_params) 
print d['count']

# <codecell>

urls=[]
for item in d['results']:
    for member in item['resources']:
        print 'url:',member['url']
        print 'resource_locator_protocol:',member['resource_locator_protocol']
        print 'resource_type:',member['resource_type']
        print 'format:',member['format'],'\n'
        if member['format'] == 'NetCDF' or member['resource_locator_protocol'] == 'THREDDS':
            urls.append(member['url'])
        

# <codecell>

print(urls)

# <markdowncell>

# These are not DAP URLS, but collections of datasets on a THREDDS server.
# Lets try opening a DAP url (two clicks away)

# <codecell>

url='http://data.nodc.noaa.gov/thredds/dodsC/glider/seaglider/uw/014/20040924/p0140001_20040924.nc'

# <codecell>

import netCDF4

# <codecell>

nc = netCDF4.Dataset(url)
ncvars = nc.variables
#pprint(ncvars.keys())

# <codecell>

s = ncvars['salinity'][:]
time_var = nc.variables['time']
dtime = netCDF4.num2date(time_var[:],time_var.units)
# Create Pandas time series object
ts = pd.Series(s,index=dtime)
# Use Pandas plot() method
ts.plot(figsize=(16,4))

# <codecell>

#print the last few values
print ts[-5:]

# <codecell>


