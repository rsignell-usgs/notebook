
# coding: utf-8

# # Query `apiso:ServiceType` on data.gov pycsw 

# In[31]:

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import numpy as np


# In[32]:

#endpoint = 'http://geoport.whoi.edu/csw' 
#endpoint = 'http://data.nodc.noaa.gov/geoportal/csw'
#endpoint = 'http://catalog.data.gov/csw-all'
endpoint = 'http://geonode.wfp.org/catalogue/csw'
endpoint = 'http://geodata.gov.gr/csw'
csw = CatalogueServiceWeb(endpoint,timeout=60)
print csw.version


# In[33]:

csw.get_operation_by_name('GetRecords').constraints


# In[34]:

try:
    csw.get_operation_by_name('GetDomain')
    csw.getdomain('apiso:ServiceType', 'property')
    print(csw.results['values'])
except:
    print('GetDomain not supported')


# In[44]:

val = u'dams'
#val = 'COADS'
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]


# In[45]:

csw.getrecords2(constraints=filter_list,maxrecords=100,esn='full')
print len(csw.records.keys())
for rec in list(csw.records.keys()):
    print csw.records[rec].title 
    


# In[46]:

choice=np.random.choice(list(csw.records.keys()))
print(csw.records[choice].title)
csw.records[choice].references


# In[27]:

csw.request


# In[28]:

csw.records[choice].xml


# In[30]:

val = 'wms'
filter2 = fes.PropertyIsLike(propertyname='apiso:ServiceType',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [fes.And([filter1, filter2])]
csw.getrecords2(constraints=filter_list, maxrecords=1000)


# In[13]:

print(len(csw.records.keys()))
for rec in list(csw.records.keys()):
    print('title:'+csw.records[rec].title) 
    print('identifier:'+csw.records[rec].identifier)
    print('modified:'+csw.records[rec].modified)
    print(' ')


# In[50]:

val = 'wms'
filter2 = fes.PropertyIsLike(propertyname='apiso:ServiceType',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [filter2]
csw.getrecords2(constraints=filter_list, maxrecords=1000)


# In[51]:

print(len(csw.records.keys()))
for rec in list(csw.records.keys()):
    print('title:'+csw.records[rec].title) 
    print('identifier:'+csw.records[rec].identifier)
    print('modified:'+csw.records[rec].modified)
    print(' ')


# In[ ]:



