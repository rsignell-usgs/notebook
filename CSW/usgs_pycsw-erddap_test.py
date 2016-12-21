
# coding: utf-8

# # Query `apiso:ServiceType` on geoport pycsw 

# In[1]:

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import numpy as np


# In[2]:

endpoint = 'http://geoport.whoi.edu/csw' 
#endpoint = 'http://data.nodc.noaa.gov/geoportal/csw'
#endpoint = 'http://data.ioos.us/csw' 

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


# ## query for a dataset we know comes from THREDDS

# In[5]:

val = 'COAWST Forecast'
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]


# In[6]:

csw.getrecords2(constraints=filter_list,maxrecords=100,esn='full')
print len(csw.records.keys())
for rec in list(csw.records.keys()):
    print csw.records[rec].title 


# In[7]:

for rec in list(csw.records.keys()):
    print(csw.records[rec].references[2]['url'])


# Now add ServiceType OPeNDAP to the query

# In[8]:

val = 'opendap'
filter2 = fes.PropertyIsLike(propertyname='apiso:ServiceType',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [fes.And([filter1, filter2])]
csw.getrecords2(constraints=filter_list, maxrecords=1000)

print(len(csw.records.keys()))
for rec in list(csw.records.keys()):
    print('title:'+csw.records[rec].title) 
    print('identifier:'+csw.records[rec].identifier)
    print('modified:'+csw.records[rec].modified)
    print(' ')


# Print the references

# In[9]:

choice=np.random.choice(list(csw.records.keys()))
print(csw.records[choice].title)
csw.records[choice].references


# In[10]:

print(len(csw.records.keys()))
for rec in list(csw.records.keys()):
    print('title:'+csw.records[rec].title) 
    print('identifier:'+csw.records[rec].identifier)
    print('modified:'+csw.records[rec].modified)
    print(' ')


# ## query for a dataset we know comes from ERDDAP

# In[11]:

val = 'pmelTaoMonT'
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]


# In[12]:

csw.getrecords2(constraints=filter_list,maxrecords=100,esn='full')
print len(csw.records.keys())
for rec in list(csw.records.keys()):
    print csw.records[rec].title 
    


# In[13]:

for rec in list(csw.records.keys()):
    print(csw.records[rec].references[2]['url'])


# In[14]:

val = 'tabledap'
filter2 = fes.PropertyIsLike(propertyname='apiso:ServiceType',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [fes.And([filter1, filter2])]
csw.getrecords2(constraints=filter_list, maxrecords=1000)

print(len(csw.records.keys()))
for rec in list(csw.records.keys()):
    print('title:'+csw.records[rec].title) 
    print('identifier:'+csw.records[rec].identifier)
    print('modified:'+csw.records[rec].modified)
    print(' ')


# In[15]:

choice=np.random.choice(list(csw.records.keys()))
print(csw.records[choice].title)
csw.records[choice].references


# In[ ]:




# In[ ]:



