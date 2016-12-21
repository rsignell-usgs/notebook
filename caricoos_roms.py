# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import netCDF4

# <codecell>

root = 'http://dm2.caricoos.org/thredds/dodsC/roms/20131203/ocean_his_%4.4d.nc'

# <codecell>

files = [root % d for d in range(1,3)]
nc = netCDF4.MFDataset(files)

# <codecell>

def start_stop(nc,tvar):
    ncv = nc.variables
    time_var = ncv[tvar]
    first = netCDF4.num2date(time_var[0],time_var.units)
    last = netCDF4.num2date(time_var[-1],time_var.units)

    print first.strftime('%Y-%b-%d %H:%M')
    print last.strftime('%Y-%b-%d %H:%M')

# <codecell>

tvar = 'ocean_time'
start_stop(nc,tvar)

# <codecell>


