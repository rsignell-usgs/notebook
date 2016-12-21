# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Exploring CSW access in Python

# <codecell>

from owslib.csw import CatalogueServiceWeb

# <codecell>

# connect to CSW, explore it's properties
endpoint = 'http://geoport.whoi.edu/pycsw'
csw = CatalogueServiceWeb(endpoint)
csw.version

# <codecell>

import iris

# <codecell>

[op.name for op in csw.operations]

# <codecell>

bbox=[-141,42,-52,84]
#bbox=[-71.5, 39.5, -63.0, 46]
csw.getrecords(keywords=['sea_water_temperature'],bbox=bbox,maxrecords=20)
#csw.getrecords(keywords=['sea_water_temperature'],maxrecords=20)
csw.results

# <codecell>

for rec,item in csw.records.iteritems():
    print rec
    print item.abstract

# <codecell>

a=csw.records['data/oceansites/DATA/STATION-M/OS_STATION-M-1_194810_D_CTD.nc']

# <codecell>

print a.xml

# <codecell>

# get supported result types
csw.getdomain('GetRecords.resultType')
csw.results

