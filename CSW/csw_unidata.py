
# coding: utf-8

# # How to search the IOOS CSW catalog with Python tools
# 
# 
# This notebook demonstrates a how to query a [Catalog Service for the Web (CSW)](https://en.wikipedia.org/wiki/Catalog_Service_for_the_Web), like the IOOS Catalog, and to parse its results into endpoints that can be used to access the data.

# In[1]:

import os
import sys

ioos_tools = os.path.join(os.path.pardir)
sys.path.append(ioos_tools)


# Let's start by creating the search filters.
# The filter used here constraints the search on a certain geographical region (bounding box), a time span (last week), and some [CF](http://cfconventions.org/Data/cf-standard-names/37/build/cf-standard-name-table.html) variable standard names that represent sea surface temperature.

# In[2]:

from datetime import datetime, timedelta
import dateutil.parser

service_type = 'WMS'

min_lon, min_lat = -90.0, 30.0 
max_lon, max_lat = -80.0, 40.0 

bbox = [min_lon, min_lat, max_lon, max_lat]
crs = 'urn:ogc:def:crs:OGC:1.3:CRS84'

# Temporal range: Last week.
now = datetime.utcnow()
start, stop = now - timedelta(days=(7)), now

start = dateutil.parser.parse('2017-03-01T00:00:00Z')
stop  = dateutil.parser.parse('2017-04-01T00:00:00Z')


# Ocean Model Names
model_names = ['NAM', 'GFS']


# With these 3 elements it is possible to assemble a [OGC Filter Encoding (FE)](http://www.opengeospatial.org/standards/filter) using the `owslib.fes`\* module.
# 
# \* OWSLib is a Python package for client programming with Open Geospatial Consortium (OGC) web service (hence OWS) interface standards, and their related content models.

# In[3]:

from owslib import fes
from ioos_tools.ioos import fes_date_filter

kw = dict(wildCard='*', escapeChar='\\',
          singleChar='?', propertyname='apiso:AnyText')

or_filt = fes.Or([fes.PropertyIsLike(literal=('*%s*' % val), **kw)
                  for val in model_names])

kw = dict(wildCard='*', escapeChar='\\',
          singleChar='?', propertyname='apiso:ServiceType')

serviceType = fes.PropertyIsLike(literal=('*%s*' % service_type), **kw)


begin, end = fes_date_filter(start, stop)
bbox_crs = fes.BBox(bbox, crs=crs)

filter_list = [
    fes.And(
        [
            bbox_crs,  # bounding box
            begin, end,  # start and end date
            or_filt,  # or conditions (CF variable names)
            serviceType  # search only for datasets that have WMS services
        ]
    )
]


# In[4]:

from owslib.csw import CatalogueServiceWeb


endpoint = 'https://data.ioos.us/csw'

csw = CatalogueServiceWeb(endpoint, timeout=60)


# The `csw` object created from `CatalogueServiceWeb` did not fetched anything yet.
# It is the method `getrecords2` that uses the filter for the search. However, even though there is a `maxrecords` option, the search is always limited by the server side and there is the need to iterate over multiple calls of `getrecords2` to actually retrieve all records.
# The `get_csw_records` does exactly that.

# In[5]:

def get_csw_records(csw, filter_list, pagesize=10, maxrecords=1000):
    """Iterate `maxrecords`/`pagesize` times until the requested value in
    `maxrecords` is reached.
    """
    from owslib.fes import SortBy, SortProperty
    # Iterate over sorted results.
    sortby = SortBy([SortProperty('dc:title', 'ASC')])
    csw_records = {}
    startposition = 0
    nextrecord = getattr(csw, 'results', 1)
    while nextrecord != 0:
        csw.getrecords2(constraints=filter_list, startposition=startposition,
                        maxrecords=pagesize, sortby=sortby)
        csw_records.update(csw.records)
        if csw.results['nextrecord'] == 0:
            break
        startposition += pagesize + 1  # Last one is included.
        if startposition >= maxrecords:
            break
    csw.records.update(csw_records)


# In[6]:

get_csw_records(csw, filter_list, pagesize=10, maxrecords=1000)

records = '\n'.join(csw.records.keys())
print('Found {} records.\n'.format(len(csw.records.keys())))
for key, value in list(csw.records.items()):
    print('[{}]\n{}\n'.format(value.title, key))


# In[7]:

csw.request


# In[8]:

#write to JSON for use in TerriaJS
csw_request = '"{}": {}"'.format('getRecordsTemplate',str(csw.request,'utf-8'))

import io
import json
with io.open('query.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(csw_request, ensure_ascii=False))
            f.write('\n')

