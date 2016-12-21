# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# #Query pycsw to find COAWST data

# <codecell>

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import numpy as np

# <codecell>

endpoint = 'http://geoport.whoi.edu/csw'
csw = CatalogueServiceWeb(endpoint,timeout=60)
print csw.version

# <codecell>

csw.get_operation_by_name('GetRecords').constraints

# <codecell>

try:
    csw.get_operation_by_name('GetDomain')
    csw.getdomain('apiso:ServiceType', 'property')
    print(csw.results['values'])
except:
    print('GetDomain not supported')

# <codecell>

val = 'COAWST'
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]

# <codecell>

csw.getrecords2(constraints=filter_list,maxrecords=100,esn='full')
print len(csw.records.keys())
for rec in list(csw.records.keys()):
    print csw.records[rec].title 
    

# <codecell>

choice=np.random.choice(list(csw.records.keys()))
print(csw.records[choice].title)
csw.records[choice].references

# <headingcell level=2>

# Query for all WMS endpoints

# <codecell>

val = 'wms'
filter1 = fes.PropertyIsLike(propertyname='apiso:ServiceType',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
val = 'COAWST'
filter2 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ [filter1, filter2] ]
csw.getrecords2(constraints=filter_list, maxrecords=1000)
print(len(csw.records.keys()))

# <codecell>

for rec in list(csw.records.keys()):
    print('title:'+csw.records[rec].title) 
    print('identifier:'+csw.records[rec].identifier)
    print('modified:'+csw.records[rec].modified)

# <codecell>

csw.get_operation_by_name('GetDomain')
csw.getdomain('apiso:ServiceType', 'property')

# <codecell>

print(csw.results)

# <codecell>


