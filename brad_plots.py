# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Brad's Realtime Data Plots

# <codecell>

import netCDF4

# <codecell>

#trans
url='http://www.neracoos.org/thredds/dodsC/UMO/All/E0131/realtime/E0131.sbe16.trans.realtime.nc'

# <codecell>

nc=netCDF4.Dataset(url)

# <codecell>

ncv=nc.variables

# <codecell>

ncv.keys()

# <codecell>

time =

