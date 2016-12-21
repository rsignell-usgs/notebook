# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Computing tidal constituent amplitude and phase from ROMS AVERAGES_DETIDE output

# <codecell>

import netCDF4
import numpy as np
from IPython.display import HTML

# <codecell>

#url='http://geoport.whoi.edu/thredds/dodsC/usgs/data0/bbleh/tidal/bbleh_base_detide.nc'
url='/usgs/data0/bbleh/tidal/bbleh_base_detide.nc'

# <codecell>

nc = netCDF4.Dataset(url)
ncv = nc.variables

# <codecell>

ncv.keys()

# <codecell>

NTC = len(ncv['tide_period'])
print NTC

# <codecell>

print ncv['tide_period'][:]

# <codecell>

zt = ncv['zeta_tide']
print zt

# <codecell>

Hcount =ncv['Hcount'][:]
print Hcount

# <codecell>

"""
Comments from ROMS/Modules/mod_tides.F:

!  Detided time-averaged fields via least-squares fitting. Notice that !
!  the harmonics for the state variable have an extra dimension of     !
!  size (0:2*NTC) to store several terms:                              !
!                                                                      !
!               index 0               mean term (accumulated sum)      !
!                     1:NTC           accumulated sine terms           !
!                     NTC+1:2*NTC     accumulated cosine terms         !
!                                                                      !
!  CosW_avg     Current time-average window COS(omega(k)*t).           !
!  CosW_sum     Time-accumulated COS(omega(k)*t).                      !
!  SinW_avg     Current time-average window SIN(omega(k)*t).           !
!  SinW_sum     Time-accumulated SIN(omega(k)*t).                      !
!  CosWCosW     Time-accumulated COS(omega(k)*t)*COS(omega(l)*t).      !
!  SinWSinW     Time-accumulated SIN(omega(k)*t)*SIN(omega(l)*t).      !
!  SinWCosW     Time-accumulated SIN(omega(k)*t)*COS(omega(l)*t).      !
!                                                                      !
!  ubar_detided Time-averaged and detided 2D u-momentum.               !
!  ubar_tide    Time-accumulated 2D u-momentum tide harmonics.         !
!  vbar_detided Time-averaged and detided 2D v-momentum.               !
!  vbar_tide    Time-accumulated 2D v-momentum tide harmonics.         !
!  zeta_detided Time-averaged and detided free-surface.                !
!  zeta_tide    Time-accumulated free-surface tide harmonics.          !
""";

# <markdowncell>

# To calculate the `m2` elevation amplitude and phase from the variable `zeta_tide`, we will need to add one to the tide_period index to get the `sin` term, and then add the number of analyzed constituents to get the `cos` term.  

# <codecell>

i_m2sin = 1+3
i_m2cos = 1+3+NTC

# <codecell>

cosW = ncv['CosW'][:]
sinW = ncv['SinW']{}

# <codecell>

# represent tide as complex
z_m2 = (zt[i_m2cos,:] + 1j* zt[i_m2sin,:]) /Hcount

# <codecell>

# compute amplitude and phase
z_m2_amp = np.abs(z_m2)
z_m2_pha = np.angle(z_m2)

# <codecell>

z_m2_amp.min()

# <codecell>

z_m2_amp.max()

# <codecell>


