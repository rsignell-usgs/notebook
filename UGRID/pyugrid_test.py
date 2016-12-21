
# coding: utf-8

# ## Test out UGRID-0.9 compliant unstructured grid model datasets with PYUGRID

# In[12]:

import datetime as dt
import netCDF4
import pyugrid
import matplotlib.tri as tri
import matplotlib.pyplot as plt
import numpy as np
get_ipython().magic(u'matplotlib inline')


# In[13]:

#FVCOM
#url =  'http://comt.sura.org/thredds/dodsC/data/comt_1_archive/inundation_tropical/UND_ADCIRC/Hurricane_Ike_3D_final_run_with_waves
url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc'
#url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM2_FORECAST.nc'
zvar = 'zeta'

#ADCIRC 
url = 'http://geoport-dev.whoi.edu/thredds/dodsC/estofs/atlantic/nc4'
#url =  'http://comt.sura.org/thredds/dodsC/data/comt_1_archive/inundation_tropical/UND_ADCIRC/Hurricane_Ike_3D_final_run_with_waves'
zvar = 'zeta'

# SELFE
#url = 'http://comt.sura.org/thredds/dodsC/data/comt_1_archive/inundation_tropical/VIMS_SELFE/Hurricane_Ike_2D_final_run_with_waves'
#url='http://amb6400b.stccmop.org:8080/thredds/dodsC/model_data/forecast.nc'
#zvar = 'elev'


# In[14]:

# Desired time for snapshot
# ....right now (or some number of hours from now) ...
start = dt.datetime.utcnow() + dt.timedelta(hours=6)
# ... or specific time (UTC)
#start = dt.datetime(2013,3,2,15,0,0)
print start


# In[15]:

ug = pyugrid.UGrid.from_ncfile(url)

# What's in there?
print "There are %i nodes"%ug.nodes.shape[0]
#print "There are %i edges"%ug.edges.shape[0]
print "There are %i faces"%ug.faces.shape[0]


# In[ ]:

lon = ug.nodes[:,0]
lat = ug.nodes[:,1]
nv = ug.faces[:]


# In[ ]:

triang = tri.Triangulation(lon,lat,triangles=nv)


# In[ ]:

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


# In[ ]:

z = ncv[zvar][itime,:]


# In[ ]:

fig = plt.figure(figsize=(12,12))
levs = np.arange(-1,5,.2)
plt.gca().set_aspect(1./np.cos(lat.mean()*np.pi/180))
plt.tricontourf(triang, z,levels=levs)
plt.colorbar()
plt.tricontour(triang, z, colors='k',levels=levs)
plt.title('%s: Elevation (m): %s' % (nc.title,daystr));


# In[ ]:




# In[ ]:



