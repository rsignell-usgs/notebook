
# coding: utf-8

# # Query `apiso:ServiceType` on data.gov 

# In[26]:

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import numpy as np


# In[27]:

endpoint = 'http://catalog.data.gov/csw-all'  #granule level production catalog
#endpoint = 'http://data.ioos.us/csw'
csw = CatalogueServiceWeb(endpoint,timeout=60)
print csw.version


# In[28]:

val = 'coawst'
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]


# In[29]:

val = 'experimental'
filter2 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [fes.And([filter1, filter2])] 


# In[30]:

csw.getrecords2(constraints=filter_list,maxrecords=100,esn='full')
print len(csw.records.keys())
for rec in list(csw.records.keys()):
    print csw.records[rec].title 


# In[31]:

choice=np.random.choice(list(csw.records.keys()))
print(csw.records[choice].title)
csw.records[choice].references


# In[32]:

csw.records[choice].xml


# We see that the `OPeNDAP` service is available, so let's add that to query

# In[34]:

val = 'opendap'
filter3 = fes.PropertyIsLike(propertyname='apiso:ServiceType',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [fes.And([filter1, filter2, filter3])]


# In[35]:

csw.getrecords2(constraints=filter_list,maxrecords=100,esn='full')
print len(csw.records.keys())
for rec in list(csw.records.keys()):
    print csw.records[rec].title 
    


# Oops. We get no records now.  This should have returned the same records.  This should work when data.gov applies this patch to pycsw:
# 
# https://github.com/geopython/pycsw/commit/d1d3c4ea7ba5b651353d22b2759bab64c6d57d87
# 
