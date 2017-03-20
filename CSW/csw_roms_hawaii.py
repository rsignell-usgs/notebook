
# coding: utf-8

# # How to search the IOOS CSW catalog with Python tools
# 
# 
# This notebook demonstrates a how to query a [Catalog Service for the Web (CSW)](https://en.wikipedia.org/wiki/Catalog_Service_for_the_Web), like the IOOS Catalog, and to parse its results into endpoints that can be used to access the data.

# In[2]:

import os
import sys
from datetime import datetime, timedelta
import dateutil.parser

ioos_tools = os.path.join(os.path.pardir)
sys.path.append(ioos_tools)


# Let's start by creating the search filters.
# The filter used here constraints the search on a certain geographical region (bounding box), a time span (last week), and some [CF](http://cfconventions.org/Data/cf-standard-names/37/build/cf-standard-name-table.html) variable standard names that represent sea surface temperature.

# In[3]:

#Bounding Box
min_lon, min_lat = -166.0, 19.0 
max_lon, max_lat = -157.0, 23.0 

bbox = [min_lon, min_lat, max_lon, max_lat]
crs = 'urn:ogc:def:crs:OGC:1.3:CRS84'


# In[4]:

# Temporal range: Last week.
now = datetime.utcnow()
start, stop = now - timedelta(days=(7)), now


# In[5]:

# Temporal range:  Specified time range
start = dateutil.parser.parse('2017-03-01T00:00:00Z')
stop  = dateutil.parser.parse('2017-04-01T00:00:00Z')


# In[6]:

# Find any of these Ocean Model Names
model_names = ['ROMS', 'FVCOM', 'SELFE', 'ADCIRC', 'Delft3D', 'DelftFM', 'HyCOM', 'NCOM']


# In[7]:

# ServiceType
service_type = 'WMS'


# With these 3 elements it is possible to assemble a [OGC Filter Encoding (FE)](http://www.opengeospatial.org/standards/filter) using the `owslib.fes`\* module.
# 
# \* OWSLib is a Python package for client programming with Open Geospatial Consortium (OGC) web service (hence OWS) interface standards, and their related content models.

# In[8]:

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


# In[9]:

from owslib.csw import CatalogueServiceWeb


endpoint = 'https://data.ioos.us/csw'

csw = CatalogueServiceWeb(endpoint, timeout=60)


# The `csw` object created from `CatalogueServiceWeb` did not fetched anything yet.
# It is the method `getrecords2` that uses the filter for the search. However, even though there is a `maxrecords` option, the search is always limited by the server side and there is the need to iterate over multiple calls of `getrecords2` to actually retrieve all records.
# The `get_csw_records` does exactly that.

# In[10]:

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


# In[11]:

get_csw_records(csw, filter_list, pagesize=10, maxrecords=1000)

records = '\n'.join(csw.records.keys())
print('Found {} records.\n'.format(len(csw.records.keys())))
for key, value in list(csw.records.items()):
    print('[{}]\n{}\n'.format(value.title, key))


# In[12]:

csw.request


# In[13]:

csw_request = '"{}": {}"'.format('getRecordsTemplate',str(csw.request,'utf-8'))


# In[15]:

import io
import json
with io.open('query.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(csw_request, ensure_ascii=False))
            f.write('\n')


# ## look for all modeling records

# In[ ]:

filter_list = [ or_filt ]

get_csw_records(csw, filter_list, pagesize=10, maxrecords=1000)

records = '\n'.join(csw.records.keys())
print('Found {} records.\n'.format(len(csw.records.keys())))
k=0
for key, value in list(csw.records.items()):
    print('[{}]\n{}\n'.format(value.title, key))
    [print(d['scheme']) for d in value.references]
    print('\n')
    if any('None' in d['scheme'] for d in value.references):
        k = k+1


# In[ ]:

[print(d['scheme']) for d in value.references]


# The easiest way to get more information is to explorer the individual records.
# Here is the `abstract` and `subjects` from the station in Astoria, OR.

# In[ ]:

k


# In[ ]:

import textwrap

print('\n'.join(textwrap.wrap(value.abstract)))


# In[ ]:

print('\n'.join(value.subjects))


# The next step is to inspect the type services/schemes available for downloading the data. The easiest way to accomplish that is with by "sniffing" the URLs with `geolinks`.

# In[ ]:

from geolinks import sniff_link

msg = 'geolink: {geolink}\nscheme: {scheme}\nURL: {url}\n'.format
for ref in value.references:
    print(msg(geolink=sniff_link(ref['url']), **ref))


# There are many direct links to Comma Separated Value (`CSV`) and
# eXtensible Markup Language (`XML`) responses to the various variables available in that station. 
# 
# In addition to those links, there are three very interesting links for more information: 1.) the QC document, 2.) the station photo, 3.) the station home page.
# 
# 
# For a detailed description of what those `geolink` results mean check the [lookup](https://github.com/OSGeo/Cat-Interop/blob/master/LinkPropertyLookupTable.csv) table.
# 
# 
# ![](https://tidesandcurrents.noaa.gov/images/stationphotos/9439040A.jpg)

# The original search was focused on sea water temperature,
# so there is the need to extract only the endpoint for that variable.
# 
# PS: see also the [pyoos example](http://ioos.github.io/notebooks_demos/notebooks/2016-10-12-fetching_data/) for fetching data from `CO-OPS`.

# In[ ]:

start, stop


# In[ ]:

for ref in value.references:
    url = ref['url']
    if 'csv' in url and 'sea' in url and 'temperature' in url:
        print(msg(geolink=sniff_link(url), **ref))
        break


# Note that the URL returned by the service has some hard-coded start/stop dates.
# It is easy to overwrite those with the same dates from the filter.

# In[ ]:

fmt = ('http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?'
       'service=SOS&'
       'eventTime={0:%Y-%m-%dT00:00:00}/{1:%Y-%m-%dT00:00:00}&'
       'observedProperty=http://mmisw.org/ont/cf/parameter/sea_water_temperature&'
       'version=1.0.0&'
       'request=GetObservation&offering=urn:ioos:station:NOAA.NOS.CO-OPS:9439040&'
       'responseFormat=text/csv')

url = fmt.format(start, stop)


# Finally, it is possible to download the data directly into a data `pandas` data frame and plot it.

# In[ ]:

import io
import requests
import pandas as pd

r = requests.get(url)

df = pd.read_csv(io.StringIO(r.content.decode('utf-8')),
                 index_col='date_time', parse_dates=True)


# In[ ]:

get_ipython().magic('matplotlib inline')
import matplotlib.pyplot as plt


fig, ax = plt.subplots(figsize=(11, 2.75))
ax = df['sea_water_temperature (C)'].plot(ax=ax)
ax.set_xlabel('')
ax.set_ylabel(r'Sea water temperature ($^\circ$C)')
ax.set_title(value.title)


# <br>
# Right click and choose Save link as... to
# [download](https://raw.githubusercontent.com/ioos/notebooks_demos/master/notebooks/2016-12-19-exploring_csw.ipynb)
# this notebook, or see a static view [here](http://nbviewer.ipython.org/urls/raw.githubusercontent.com/ioos/notebooks_demos/master/notebooks/2016-12-19-exploring_csw.ipynb).
