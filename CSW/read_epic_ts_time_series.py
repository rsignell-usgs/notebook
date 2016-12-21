# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import netCDF4
url='http://geoport.whoi.edu/thredds/dodsC/usgs/data2/emontgomery/stellwagen/Data/ARGO_MERCHANT/1211TR-A1H.cdf'
nc=netCDF4.Dataset(url)

# <codecell>

print ncv.keys()
ncv=nc.variables

# <codecell>

nc.summary

# <codecell>

u=ncv['rtrn_4012'][:].flatten()

# <codecell>

plot(u)

# <codecell>

url='http://geoport.whoi.edu/thredds/dodsC/usgs/data2/emontgomery/stellwagen/Data/ARGO_MERCHANT/1211P-A1H.cdf'
nc = netCDF4.Dataset(url)
ncv = nc.variables

# <codecell>

ncv.keys()

# <codecell>

p = ncv['SDP_850'][:].flatten()

# <codecell>

plot(p)

# <codecell>

p = ncv['P_4022'][:].flatten()
plot(p)

# <codecell>


