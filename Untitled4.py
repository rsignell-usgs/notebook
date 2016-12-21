# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import netCDF4
url='https://weather.rsmas.miami.edu/repository/opendap/synth:100ae90b-71ac-4d38-add9-f8982a976322:L2FsbGZpZWxkcy5uYw==/entry'
nc = netCDF4.Dataset(url)

# <codecell>

ncv = nc.variables

# <codecell>

ncv.keys()

# <codecell>

tvar = ncv['T_mjo']

# <codecell>

timevar = ncv['time']

# <codecell>

timevar[0]

# <codecell>

nc.dimensions.keys()

# <codecell>

print nc.history

# <codecell>


