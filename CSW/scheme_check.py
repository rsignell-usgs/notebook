# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from owslib import fes
from owslib.csw import CatalogueServiceWeb

schemes = set()
c   = CatalogueServiceWeb("https://data.noaa.gov/csw", timeout=20)
fil = fes.PropertyIsLike(propertyname='apiso:AnyText', literal="*sea_surface_height_above_sea_level*", wildCard='*')
c.getrecords2(constraints=[fil], maxrecords=1000, esn='full')

# <codecell>

for record, item in c.records.items():
    for d in item.references:
        schemes.add(d['scheme'])

# <codecell>

for scheme in schemes:
    print scheme

# <codecell>

type(schemes)

# <codecell>


