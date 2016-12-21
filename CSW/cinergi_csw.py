
# coding: utf-8

# # Query  `apiso:ServiceType` on CINERGI csw

# In[1]:

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import numpy as np


# In[2]:

endpoint = 'http://cinergi.cloudapp.net/geoportal/csw'   # NODC/UAF Geoportal: granule level
csw = CatalogueServiceWeb(endpoint,timeout=60)
print csw.version


# In[3]:

csw.get_operation_by_name('GetRecords').constraints


# ## Try a simple query first using just `apiso:AnyText`

# In[4]:

val = 'roms'
#val = 'modflow'
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]


# In[5]:

csw.getrecords2(constraints=filter_list,maxrecords=100,esn='full')
print len(csw.records.keys())
for rec in list(csw.records.keys()):
    print csw.records[rec].title 
    


# ## Add bounding box constraint. 
# 
# To specify lon,lat order for bbox (which we want to do so that we can use the same bbox with either geoportal server or pycsw requests), we need to request the bounding box specifying the CRS84 coordinate reference system.   The CRS84 option is available in `pycsw 1.1.10`+. The ability to specify the `crs` in the bounding box request is available in `owslib 0.8.12`+.  For more info on the bounding box problem and how it was solved, see this [pycsw issue](https://github.com/geopython/pycsw/issues/287), this [geoportal server issue](https://github.com/Esri/geoportal-server/issues/124), and this [owslib issue](https://github.com/geopython/OWSLib/issues/201)

# In[6]:

#bbox = [-87.40, 34.25, -63.70, 66.70]    # [lon_min, lat_min, lon_max, lat_max]      maine
bbox = [-162., 19.0, -154., 23.0]   # Hawaii
bbox_filter = fes.BBox(bbox,crs='urn:ogc:def:crs:OGC:1.3:CRS84')
filter_list = [fes.And([filter1, bbox_filter])]
csw.getrecords2(constraints=filter_list, maxrecords=1000)


# In[7]:

print(len(csw.records.keys()))
for rec in list(csw.records.keys()):
    print('title:'+csw.records[rec].title) 
    print('identifier:'+csw.records[rec].identifier)
    print('modified:'+csw.records[rec].modified)
    print(' ')


# ## Add ServiceType constraint. 

# In[11]:

val = 'opendap'
filter2 = fes.PropertyIsLike(propertyname='apiso:ServiceType',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [fes.And([filter1, filter2, bbox_filter])]
csw.getrecords2(constraints=filter_list, maxrecords=1000, esn='full')


# In[12]:

print(len(csw.records.keys()))
for rec in list(csw.records.keys()):
    print('title:'+csw.records[rec].title) 
    print('identifier:'+csw.records[rec].identifier)
    print('modified:'+csw.records[rec].modified)
    print(' ')


# ## Print out the references.   Expecting to see the opendap link here:

# In[13]:

choice=np.random.choice(list(csw.records.keys()))
print(csw.records[choice].title)
csw.records[choice].references


# In[ ]:




# In[ ]:



