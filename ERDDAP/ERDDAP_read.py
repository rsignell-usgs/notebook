# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Read Chlorophyll data from ERDDAP

# <codecell>

import urllib
import netCDF4

# <codecell>

url=('http://coastwatch.pfeg.noaa.gov/erddap/griddap/erdVHchla8day.nc?'
     'chla[(2014-05-29T00:00:00Z):1:(2014-05-29T00:00:00Z)]'
     '[(47.97916666666667):1:(34.89583333333334)][(-76.5625):1:(-63.47916666666666)]')
file='chla.nc'
urllib.urlretrieve (url, file)
nc = netCDF4.Dataset(file)
ncv = nc.variables
ncv.keys()

# <codecell>

figure(figsize=(10,8))
pcolormesh(ncv['longitude'][:],ncv['latitude'][:],log(ncv['chla'][0,:,:]),vmin=-2,vmax=2);

# <codecell>


