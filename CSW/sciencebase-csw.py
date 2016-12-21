# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# #Testing ScienceBase CSW

# <codecell>

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import numpy as np

# <codecell>

endpoint = 'http://catalog.data.gov/csw-all'  #granule level catalog
endpoint = 'https://www.sciencebase.gov/catalog/item/54dd2326e4b08de9379b2fb1/csw'
csw = CatalogueServiceWeb(endpoint,timeout=60)
print csw.version

# <codecell>

csw.get_operation_by_name('GetRecords').constraints

# <codecell>

val = 'prism'
filter1 = fes.PropertyIsLike(propertyname='AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]

# <codecell>

csw.getrecords2(constraints=filter_list,maxrecords=100,esn='full')
print len(csw.records.keys())
for rec in list(csw.records.keys()):
    print csw.records[rec].title 

# <codecell>

choice = np.random.choice(list(csw.records.keys()))
print(csw.records[choice].title)
csw.records[choice].references

# <codecell>


