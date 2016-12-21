
# coding: utf-8

# # Use CSW to find model data at NODC, NGDC, DATA.GOV, and PACIOOS

# In[1]:

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import netCDF4
import numpy as np


# ## Find model results at NODC (geoportal)

# In[2]:

endpoint = 'http://www.nodc.noaa.gov/geoportal/csw'   # NODC/UAF Geoportal: granule level
csw = CatalogueServiceWeb(endpoint,timeout=60)
print csw.version


# In[3]:

csw.get_operation_by_name('GetRecords').constraints


# In[4]:

val = 'level'
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]


# In[5]:

csw.getrecords2(constraints=filter_list,maxrecords=100,esn='full')
len(csw.records.keys())


# In[6]:

choice=np.random.choice(list(csw.records.keys()))
print(csw.records[choice].title)
csw.records[choice].references


# ## Find model results at NGDC  (geoportal)

# In[161]:

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw' #  NGDC/IOOS Geoportal
csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version


# In[162]:

csw.get_operation_by_name('GetRecords').constraints


# In[163]:

try:
    csw.get_operation_by_name('GetDomain')
    csw.getdomain('apiso:ServiceType', 'property')
    print(csw.results['values'])
except:
    print('GetDomain not supported')


# In[164]:

val = 'level'
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]


# In[165]:

val = 'erddap'
filter1 = fes.PropertyIsLike(propertyname='apiso:ServiceType',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]


# In[166]:

csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())


# In[167]:

choice=np.random.choice(list(csw.records.keys()))
print choice
csw.records[choice].references


# ## Find model data at CATALOG.DATA.GOV (pycsw)

# In[56]:

endpoint = 'http://catalog.data.gov/csw-all' #  catalog.data.gov CSW
#endpoint = 'http://csw.data.gov.uk/geonetwork/srv/en/csw' # data.gov.uk
#endpoint = 'http://www.nationaalgeoregister.nl/geonetwork/srv/eng/csw'
#endpoint = 'http://www.rndt.gov.it/RNDT/CSW'
csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version


# In[57]:

for oper in csw.operations:
    print(oper.name)


# In[58]:

csw.get_operation_by_name('GetRecords').constraints


# In[59]:

try:
    csw.get_operation_by_name('GetDomain')
    csw.getdomain('apiso:ServiceType', 'property')
    print(csw.results['values'])
except:
    print('GetDomain not supported')


# In[60]:

val = 'salinity'
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]


# In[61]:

csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())


# In[ ]:

csw.getrecords2()


# In[51]:

choice=np.random.choice(list(csw.records.keys()))
print csw.records[choice].title
csw.records[choice].references


# ## Search at geoport.whoi.edu (geoportal)

# In[ ]:

endpoint = 'http://geoport.whoi.edu/geoportal/csw' #  catalog.data.gov CSW
csw = CatalogueServiceWeb(endpoint,timeout=60)
print csw.version


# In[ ]:

for oper in csw.operations:
    if oper.name == 'GetRecords':
        print '\nISO Queryables:\n',oper.constraints['SupportedISOQueryables']['values']


# In[ ]:

csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())


# In[ ]:

choice=random.choice(list(csw.records.keys()))
print choice
csw.records[choice].references


# ## Search at PACIOOS (pycsw)

# In[175]:

endpoint='http://oos.soest.hawaii.edu/pacioos/ogc/csw.py'


# In[176]:

csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version


# In[177]:

csw.get_operation_by_name('GetRecords').constraints


# In[178]:

try:
    csw.get_operation_by_name('GetDomain')
    csw.getdomain('apiso:ServiceType', 'property')
    print(csw.results['values'])
except:
    print('GetDomain not supported')


# In[179]:

val = 'ROMS'
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]


# In[180]:

csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())


# In[181]:

choice=np.random.choice(list(csw.records.keys()))
print choice
csw.records[choice].references


# Working!  Woo hoo!!! 

# ## EPA

# In[ ]:

endpoint = 'https://edg.epa.gov/metadata/csw'
csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version


# In[ ]:

# trying to do this search:
# ('roms' OR 'selfe' OR 'adcirc' OR 'ncom' OR 'hycom' OR 'fvcom') AND 'ocean' NOT 'regridded' NOT 'espresso'
# should return 11 records from NODC geoportal

search_text = ['waves','selfe','adcirc','ncom','hycom','fvcom']
filt=[]
for val in search_text:
    filt.append(fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                                   escapeChar='\\',wildCard='*',singleChar='?'))
filter1=fes.Or(filt)

val = 'ocean'
filter2=fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')

val = 'regridded'
filt=fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter3 = fes.Not([filt])

val = 'espresso'
filt=fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter4 = fes.Not([filt])


filter_list = [fes.And([filter1, filter2, filter3, filter4])]


# In[ ]:

csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())


# In[ ]:

choice=random.choice(list(csw.records.keys()))
print choice
csw.records[choice].references


# In[ ]:

try:
    csw.get_operation_by_name('GetDomain')
    csw.getdomain('apiso:SupportedISOQueryables', 'apiso:ServiceType')
    print(csw.results['values'])
except:
    print('GetDomain not supported')


# ## USGS CGDMS server (geonetwork)

# In[ ]:

endpoint = 'http://cmgds.marine.usgs.gov/geonetwork/srv/en/csw'
csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version


# ## USGS CIDA Server (geonetwork)

# In[ ]:

endpoint = 'http://cida.usgs.gov/gdp/geonetwork/srv/en/csw'
csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version


# In[ ]:

foo=csw.get_operation_by_name('GetRecords')
foo.constraints


# In[ ]:

try:
    csw.get_operation_by_name('GetDomain')
    csw.getdomain('SupportedISOQueryables', 'ServiceType')
    print(csw.results['values'])
except:
    print('GetDomain not supported')


# In[ ]:

val = 'dap'
service_type = fes.PropertyIsLike(propertyname='ServiceType',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ service_type]


# In[ ]:

csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())


# In[ ]:

val = 'climate'
filter1 = fes.PropertyIsLike(propertyname='AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]


# In[ ]:

csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())


# In[ ]:

choice=random.choice(list(csw.records.keys()))
print choice
csw.records[choice].references


# ## INSPIRE

# In[63]:

endpoint ='http://inspire-geoportal.ec.europa.eu/GeoportalProxyWebServices/resources/OGCCSW202/AT'
csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version


# In[ ]:

csw.get_operation_by_name('GetRecords').constraints


# In[14]:

try:
    csw.get_operation_by_name('GetDomain')
    csw.getdomain('apiso:ServiceType', 'property')
    print(csw.results['values'])
except:
    print('GetDomain not supported')


# In[15]:

val = 'data'
filter1 = fes.PropertyIsLike(propertyname='AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]


# In[16]:

csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())


# In[62]:

choice=random.choice(list(csw.records.keys()))
print(csw.records[choice].title)
csw.records[choice].references


# ## Italy

# In[18]:

endpoint = 'http://www.rndt.gov.it/RNDT/CSW'
csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version


# In[19]:

csw.get_operation_by_name('GetRecords').constraints


# In[27]:

val = 'water'
filter1 = fes.PropertyIsLike(propertyname='AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]


# In[28]:

csw.getrecords2(constraints=filter_list,maxrecords=100,esn='full')
len(csw.records.keys())


# In[53]:

choice=random.choice(list(csw.records.keys()))
print(csw.records[choice].title)
print(csw.records[choice].references)


# In[152]:

endpoint='http://172.21.173.15/geonetwork/srv/eng/csw'
csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version


# In[ ]:



