# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import iris
url='http://oceanmodeling.pmc.ucsc.edu:8080/thredds/dodsC/ccsnrt/fmrc/CCSNRT_Aggregation_best.ncd'
var='potential temperature'
cube = iris.load_cube(url,var)

# <codecell>

print cube

# <codecell>


