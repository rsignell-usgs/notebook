# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import matplotlib.pyplot as plt
import numpy as np
import netCDF4 
from IPython.html import widgets

%matplotlib inline

# <codecell>

url = '/usgs/vault0/coawst/coawst_4/Output/use/coawst_us_20150326_01.nc'
url = 'http://geoport.whoi.edu/thredds/dodsC/coawst_4/use/fmrc/coawst_4_use_best.ncd'

# <codecell>

nc = netCDF4.Dataset(url,'r')
ncv = nc.variables
vars = nc.variables.keys()

# <codecell>

vars34 = [var for var, vart in ncv.items() if vart.ndim==3 or vart.ndim==4]
vars4 = [var for var, vart in ncv.items() if vart.ndim==4]

# <codecell>

tvar = ncv[vars4[0]]
siz = tvar.shape
nt = siz[0]
nz = siz[1]

# <codecell>

def sh(var='temp',time=0,lev=0):
    vart=ncv[var]
    ax = plt.figure(figsize=(12,4))
    if vart.ndim==3:
        plt.imshow(vart[time,:,:],origin='lower')
    elif vart.ndim==4:
        plt.imshow(vart[time,lev,:,:],origin='lower')
    else:
        print('no handled')

# <codecell>

widgets.interact(sh, time=(0,nt-1,1), lev=(0,nz-1,1), var=vars34);

# <codecell>


