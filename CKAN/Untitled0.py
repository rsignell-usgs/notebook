# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import ckanapi

# <codecell>

ckan = ckanapi.RemoteCKAN('https://data.noaa.gov/api/3')

# <codecell>

search_params = {                                           
    'q': 'tags:"sea_water_temperature" AND metadata_modified:[2012-06-01T00:00:00.000Z TO NOW]',  
    'fq': 'res_format:HTML',                                
    'extras': {"ext_bbox":"-71.5,41.,-63,46.0"},                   
    'rows': 3                                                     
}
d = ckan.call_action('package_search', data_dict=search_params) 
print d['count']

# <codecell>

import ckanclient

# <codecell>


