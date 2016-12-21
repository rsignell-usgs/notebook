# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# ##Test out UGRID-0.9 compliant unstructured grid model datasets with PYUGRID

# <codecell>

import datetime as dt
import netCDF4
import pyugrid
import matplotlib.tri as tri
import matplotlib.pyplot as plt
import numpy as np
%matplotlib inline

# <codecell>

#ADCIRC
url =  'http://comt.sura.org/thredds/dodsC/data/comt_1_archive/inundation_tropical/UND_ADCIRC/Hurricane_Ike_2D_final_run_with_waves'
zvar = 'zeta'

#FVCOM
#url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM2_FORECAST.nc'
#zvar = 'zeta'

#SELFE
#url = 'http://comt.sura.org/thredds/dodsC/data/comt_1_archive/inundation_tropical/VIMS_SELFE/Hurricane_Ike_2D_final_run_with_waves'
#zvar='elev'

#ESTOFS Aggregation
#url = 'http://geoport-dev.whoi.edu/thredds/dodsC/estofs/atlantic'
#zvar = 'zeta'

# STCCMOP SELFE
#url='http://amb6400b.stccmop.org:8080/thredds/dodsC/model_data/forecast.nc'
#zvar = 'elev'

# <codecell>

# Desired time for snapshot
# ....right now (or some number of hours from now) ...
start = dt.datetime.utcnow() + dt.timedelta(hours=6)
# ... or specific time (UTC)
start = dt.datetime(2008,9,13,6,0,0)
print start

# <codecell>

ug = pyugrid.UGrid.from_ncfile(url)

# What's in there?
print "There are %i nodes"%ug.nodes.shape[0]
#print "There are %i edges"%ug.edges.shape[0]
print "There are %i faces"%ug.faces.shape[0]

# <codecell>

lon = ug.nodes[:,0]
lat = ug.nodes[:,1]
nv = ug.faces[:]

# <codecell>

triang = tri.Triangulation(lon,lat,triangles=nv)

# <codecell>

nc = netCDF4.Dataset(url)
ncv = nc.variables
# Get desired time step  
time_var = ncv['time']
print 'number of time steps:',len(time_var)
itime = netCDF4.date2index(start,time_var,select='nearest')
start_time = netCDF4.num2date(time_var[0],time_var.units)
stop_time = netCDF4.num2date(time_var[-1],time_var.units)
print 'start time:',start_time.strftime('%Y-%b-%d %H:%M')
print 'stop time:',stop_time.strftime('%Y-%b-%d %H:%M')
dtime = netCDF4.num2date(time_var[itime],time_var.units)
daystr = dtime.strftime('%Y-%b-%d %H:%M')
print 'time selected:', daystr

# <codecell>

z = ncv[zvar][itime,:]

# <codecell>

fig = plt.figure(figsize=(12,12))
levs = np.arange(-1,5,.2)
plt.gca().set_aspect(1./np.cos(lat.mean()*np.pi/180))
plt.tricontourf(triang, z,levels=levs)
plt.colorbar()
plt.tricontour(triang, z, colors='k',levels=levs)
plt.title('%s: Elevation (m): %s' % (nc.title,daystr));

# <codecell>


# <codecell>


