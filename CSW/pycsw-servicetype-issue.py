# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# #Use CSW to find CMG_Portal data

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

val = 'CMG_Portal'
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
filter_list = [ filter1 ]
csw.getrecords2(constraints=filter_list, maxrecords=1000)
print(len(csw.records.keys()))

# <codecell>

for rec in list(csw.records.keys()):
    print('title:'+csw.records[rec].title) 
    print('identifier:'+csw.records[rec].identifier)
    print('modified:'+csw.records[rec].modified)
    print(' ')

# <codecell>


