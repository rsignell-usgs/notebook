# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# # Testing data.gov using the CKAN API

# <markdowncell>

# We want to find all Data.gov datasets that match a specific criteria.  Here we try using the CKAN API with the  `ckanclient` package.

# <codecell>

import ckanclient

# <codecell>

ckan = ckanclient.CkanClient('http://catalog.data.gov/api/3')
#ckan = ckanclient.CkanClient('https://data.noaa.gov/api/3')

# <codecell>

search_params = { 
    'fq': 'res_format:WMS',
    'rows': 10 
}
      
d = ckan.action('package_search', **search_params) 
print d['count']

# <codecell>

for rec in d['results']:
    print rec['title']

# <markdowncell>

# Find all WMS data matching additional query criteria

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

search_params = { 'q': 'tags:"temperature"',
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
        

