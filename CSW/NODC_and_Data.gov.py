
# coding: utf-8

# # Use CSW to find data at NODC and DATA.GOV

# In[1]:

import numpy as np


# In[2]:

from owslib.csw import CatalogueServiceWeb
from owslib import fes


# In[3]:

# Searching: "sea_water_temperature" AND NODC NOT TAO 
# returns 24 datasets on Data.gov

val = 'sea\_water\_temperature'
filter1=fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')

val = 'NODC'
filter2=fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')

val = 'TAO'
filt=fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter3 = fes.Not([filt])

filter_list = [fes.And([filter1, filter2, filter3])]


# ## Find results at NODC

# In[4]:

endpoint = 'http://www.nodc.noaa.gov/geoportal/csw'   # NODC/UAF Geoportal: granule level
csw = CatalogueServiceWeb(endpoint,timeout=60)
print csw.version


# In[5]:

csw.get_operation_by_name('GetRecords').constraints


# In[6]:

csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())


# In[7]:

choice = np.random.choice(list(csw.records.keys()))
print choice
csw.records[choice].references


# ## Find model data at CATALOG.DATA.GOV

# In[8]:

endpoint = 'http://catalog.data.gov/csw-all' # CSW for granules
csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version


# In[9]:

csw.get_operation_by_name('GetRecords').constraints


# In[10]:

csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())


# In[11]:

choice = np.random.choice(list(csw.records.keys()))
print choice
csw.records[choice].references


# In[ ]:




# In[ ]:



