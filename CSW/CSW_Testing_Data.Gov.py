# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Exploring CSW access in Python using OWSLib with Data.gov

# <codecell>

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import numpy as np

# <codecell>

endpoint = 'http://catalog.data.gov/csw-all' #  granules
#endpoint = 'http://catalog.data.gov/csw' #  collections
csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version

# <codecell>

[op.name for op in csw.operations]

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

box=[-72.0, 41.0, -69.0, 43.0]   # gulf of maine

# <codecell>

val = 'salinity'
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]

# <codecell>

csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())

# <codecell>

for rec,item in csw.records.iteritems():
    print item.title

# <codecell>

choice=np.random.choice(list(csw.records.keys()))
print csw.records[choice].title
csw.records[choice].references

# <codecell>

offset = 10
startposition = 0

while True:
    csw.getrecords2(startposition=startposition, constraints=filter_list,maxrecords=20,esn='full')
    for rec,item in csw.records.iteritems():
        print item.title
    if csw.results['nextrecord'] == 0:
        break
    startposition += offset

# <codecell>

limit = 1000
offset = 10
 
startposition = 0
 
while True:
    csw.getrecords2(startposition=startposition, maxrecords=limit)
    for record in csw.records:
        print record
    if csw.results['nextrecord'] == 0:
        break
    startposition += offset

# <codecell>

csw.getrecords2(

