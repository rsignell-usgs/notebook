
# coding: utf-8

# # Query `apiso:ServiceType` on data.gov pycsw 

# In[1]:

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import numpy as np


# In[2]:

#endpoint = 'http://geoport.whoi.edu/csw' 
#endpoint = 'http://data.nodc.noaa.gov/geoportal/csw'
endpoint = 'http://catalog.data.gov/csw-all'
#endpoint = 'http://geonode.wfp.org/catalogue/csw'
csw = CatalogueServiceWeb(endpoint,timeout=60)
print csw.version


# In[3]:

csw.get_operation_by_name('GetRecords').constraints


# In[4]:

try:
    csw.get_operation_by_name('GetDomain')
    csw.getdomain('apiso:ServiceType', 'property')
    print(csw.results['values'])
except:
    print('GetDomain not supported')


# In[5]:

val = 'COAWST'
#val = 'COADS'
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]


# In[6]:

csw.getrecords2(constraints=filter_list,maxrecords=100,esn='full')
print len(csw.records.keys())
for rec in list(csw.records.keys()):
    print csw.records[rec].title 
    


# In[7]:

choice=np.random.choice(list(csw.records.keys()))
print(csw.records[choice].title)
csw.records[choice].references


# In[8]:

csw.request


# In[9]:

csw.records[choice].xml


# Add bounding box constraint. To specify lon,lat order for bbox (which we want to do so that we can use the same bbox with either geoportal server or pycsw requests), we need to request the bounding box specifying the CRS84 coordinate reference system.   The CRS84 option is available in `pycsw 1.1.10`+. The ability to specify the `crs` in the bounding box request is available in `owslib 0.8.12`+.  For more info on the bounding box problem and how it was solved, see this [pycsw issue](https://github.com/geopython/pycsw/issues/287), this [geoportal server issue](https://github.com/Esri/geoportal-server/issues/124), and this [owslib issue](https://github.com/geopython/OWSLib/issues/201)

# In[10]:

bbox = [-87.40, 34.25, -63.70, 66.70]    # [lon_min, lat_min, lon_max, lat_max]
bbox_filter = fes.BBox(bbox,crs='urn:ogc:def:crs:OGC:1.3:CRS84')
filter_list = [fes.And([filter1, bbox_filter])]
csw.getrecords2(constraints=filter_list, maxrecords=1000)


# In[11]:

print(len(csw.records.keys()))
for rec in list(csw.records.keys()):
    print('title:'+csw.records[rec].title) 
    print('identifier:'+csw.records[rec].identifier)
    print('modified:'+csw.records[rec].modified)
    print(' ')


# In[12]:

val = 'WMS'
filter2 = fes.PropertyIsLike(propertyname='apiso:ServiceType',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [fes.And([filter1, filter2, bbox_filter])]
csw.getrecords2(constraints=filter_list, maxrecords=1000)


# In[13]:

print(len(csw.records.keys()))
for rec in list(csw.records.keys()):
    print('title:'+csw.records[rec].title) 
    print('identifier:'+csw.records[rec].identifier)
    print('modified:'+csw.records[rec].modified)
    print(' ')


# In[ ]:




# In[ ]:



