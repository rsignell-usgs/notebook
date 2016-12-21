
# coding: utf-8

# #Query CSW to find all COAWST WMS services

# Find all the COAWST (ocean model) datasets that have WMS services by using the CSW queryables `apiso:anyText` and `apiso:ServiceType` on different CSW endpoints.

# In[1]:

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import numpy as np


# In[2]:

endpoint = 'http://geoport.whoi.edu/csw'
#endpoint = 'http://catalog.data.gov/csw-all'
#endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw'
#endpoint = 'http://www.nodc.noaa.gov/geoportal/csw'
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


# ## Query for all COAWST datasets 

# In[5]:

val = 'COAWST'
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


# ## Query for all COAWST datsets that also contain WMS endpoints

# Since all COAWST datasets contain WMS endpoints, this should return the same number of dataset records

# In[8]:

val = 'COAWST'
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?',matchCase=True)
val = 'WMS'
filter2 = fes.PropertyIsLike(propertyname='apiso:ServiceType',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?',matchCase=False)
filter_list = [ [filter1, filter2] ]
csw.getrecords2(constraints=filter_list, maxrecords=1000)
print(len(csw.records.keys()))


# In[9]:

for rec in list(csw.records.keys()):
    print('title:'+csw.records[rec].title) 
    print('identifier:'+csw.records[rec].identifier)
    print('modified:'+csw.records[rec].modified)


# In[11]:

val = 'wms'
filter2 = fes.PropertyIsLike(propertyname='apiso:ServiceType',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?',matchCase=True)
filter_list = [  filter2 ]
csw.getrecords2(constraints=filter_list, maxrecords=1000)
print(len(csw.records.keys()))


# In[10]:



