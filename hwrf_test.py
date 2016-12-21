# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Test reading HWRF NetCDF files

# <markdowncell>

# Test files obtained from ftp thusly, thanks to info from Vijay Tallapragada (NOAA Federal) <vijay.tallapragada@noaa.gov>:
# ```
# ssh geoport.whoi.edu
# cd /usgs/data2/rsignell/models/ncep/hwrf
# wget ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/hur/prod/hwrf.2014100712/simon19e.2014100712.wrfdiag_d02
# wget ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/hur/prod/hwrf.2014100712/simon19e.2014100712.wrfdiag_d03
# wget ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/hur/prod/hwrf.2014100712/simon19e.2014100712.wrfdiag_d01
# 
# ```
#     

# <codecell>

import netCDF4

# <codecell>

url='http://geoport.whoi.edu/thredds/dodsC/usgs/data2/rsignell/models/ncep/hwrf/simon19e.2014100712.wrfdiag_d02'
nc = netCDF4.Dataset(url)
ncv = nc.variables

# <codecell>

def plot_sst(istep):
    sst = ncv['SST'][istep,:,:]
    lon = ncv['HLON'][istep,:,:]
    lat = ncv['HLAT'][istep,:,:]
    sst = ma.masked_equal(sst,0) - 274.15
    pcolormesh(lon,lat,sst)
    colorbar()
    time_stamp=''.join(ncv['Times'][istep])
    title(time_stamp);

# <codecell>

# plot 1st time step
plot_sst(0)

# <codecell>

#plot last time step
plot_sst(-1)

# <codecell>


# <codecell>


