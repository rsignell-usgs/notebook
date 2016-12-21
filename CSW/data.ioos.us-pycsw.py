
# coding: utf-8

# # Query `apiso:ServiceType` 

# In[43]:

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import numpy as np


# The GetCaps request for these services looks like this:
#     http://catalog.data.gov/csw-all/csw?SERVICE=CSW&VERSION=2.0.2&REQUEST=GetCapabilities

# In[56]:

endpoint = 'http://data.ioos.us/csw'    # FAILS apiso:ServiceType
#endpoint = 'http://catalog.data.gov/csw-all'  # FAILS apiso:ServiceType
#endpoint = 'http://geoport.whoi.edu/csw' # SUCCEEDS apiso:ServiceType

csw = CatalogueServiceWeb(endpoint,timeout=60)
print csw.version


# In[57]:

csw.get_operation_by_name('GetRecords').constraints


# Search first for records containing the text "COAWST" and "experimental". 

# In[45]:

val = 'coawst'
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]


# In[46]:

val = 'experimental'
filter2 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [fes.And([filter1, filter2])] 


# In[47]:

csw.getrecords2(constraints=filter_list,maxrecords=100,esn='full')
print len(csw.records.keys())
for rec in list(csw.records.keys()):
    print csw.records[rec].title 


# Now let's print out the references (service endpoints) to see what types of services are available

# In[48]:

choice=np.random.choice(list(csw.records.keys()))
print(csw.records[choice].title)
csw.records[choice].references


# In[49]:

csw.records[choice].xml


# We see that the `OPeNDAP` service is available, so let's see if we can add that to the query, returning only datasets that have text "COAWST" and "experimental" and that have an "opendap" service available. 
# 
# We should get the same number of records, as all COAWST records have OPeNDAP service endpoints.   If we get no records, something is wrong with the CSW server.

# In[50]:

val = 'OPeNDAP'
filter3 = fes.PropertyIsLike(propertyname='apiso:ServiceType',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [fes.And([filter1, filter2, filter3])]
csw.getrecords2(constraints=filter_list, maxrecords=1000)


# In[51]:

print(len(csw.records.keys()))
for rec in list(csw.records.keys()):
    print('title:'+csw.records[rec].title) 
    print('identifier:'+csw.records[rec].identifier)
    print('modified:'+csw.records[rec].modified)
    print(' ')


# In[53]:

print(csw.request)


# In[ ]:



