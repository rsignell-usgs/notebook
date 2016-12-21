# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

cd /usgs/data2/rsignell/data/bathy/dem

# <codecell>

ls *.las

# <codecell>

import laspy
inFile = laspy.File.File("/usgs/data2/rsignell/data/bathy/dem/16RCU384346.las", mode = "r")

# <codecell>

laspy

# <codecell>


# <codecell>


