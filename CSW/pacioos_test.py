# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import numpy as np

# <codecell>

endpoint='http://oos.soest.hawaii.edu/pacioos/ogc/csw.py'

# <codecell>

csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version

# <codecell>

csw.get_operation_by_name('GetRecords').constraints

# <codecell>

val = 'ROMS'
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]

# <codecell>

csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())

# <codecell>


# <codecell>


