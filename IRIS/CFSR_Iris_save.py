
# coding: utf-8

# In[1]:

from pylab import * 
import iris
import iris.plot as iplt
import cartopy.crs as ccrs
import netCDF4
import datetime as dt
from time import time


# In[2]:

year = 2008
start = dt.datetime(year,1,1,0,0,0)
stop = dt.datetime(year,12,31,18,0,0)
bbox = [-77., -63., 34., 46.]   # [lon_min lon_max lat_min lat_max]


# In[3]:

# CFSR NOMADS OPeNDAP URL
url='http://nomads.ncdc.noaa.gov/thredds/dodsC/modeldata/cmd_ocnh/%4.4d/%4.4d01/%4.4d0101/ocnh01.gdas.%4.4d010100.grb2' % (year,year,year,year)
print url


# In[4]:

# specify name of output file that will be created
ofile = '/usgs/data2/rsignell/models/ncep/CFSR/cfsr_%4.4d.nc' % year
print ofile


# In[5]:

cubes = iris.load(url)


# In[6]:

print cubes


# In[7]:

long_name = 'Potential_temperature @ depth_below_sea'
cube = iris.load_cube(url,long_name)
slice = cube.extract(iris.Constraint(longitude=lambda cell: bbox[0]+360. < cell < bbox[1]+360.,
                                     latitude=lambda cell: bbox[2] < cell < bbox[3]))
shape(slice)


# In[8]:

# convert to degC
slice.convert_units('degC')


# In[9]:

print slice


# In[10]:

# select surface layer at 1st time step for a test plot
slice2d=slice[0,-1,:,:]
shape(slice2d)


# In[11]:

figure(figsize=(12,8))

# set the projection
ax1 = plt.axes(projection=ccrs.Mercator())

# color filled contour plot
h = iplt.contourf(slice2d,64)

# add coastlines, colorbar and title
plt.gca().coastlines(resolution='10m')
colorbar(h,orientation='vertical');
title('Ocean Temperature');


# In[12]:

iris.save(slice,ofile)


# In[ ]:




# In[13]:

origin = dt.datetime(1900,1,1,0,0,0)
nsteps = int((stop - start).total_seconds()/3600/6)  # 6 hour time steps
print nsteps

nc = netCDF4.Dataset(ofile,'r+')
nc.variables['time'].units = 'hours since 1900-01-01T00:00:00Z'

# start from penultimate time step (or 0)
istart=max(len(nc.dimensions['time'])-1,0)
#istart = 439

nc.close()

for i in range(istart,nsteps):
    time0=time()
    nc = netCDF4.Dataset(ofile,'r+')
    dtime = start + dt.timedelta(hours=(6*i))
    dhours=(dtime - origin).total_seconds()/3600.
    url='http://nomads.ncdc.noaa.gov/thredds/dodsC/modeldata/cmd_ocnh/%4.4d/%4.4d%2.2d/%4.4d%2.2d%2.2d/ocnh01.gdas.%4.4d%2.2d%2.2d%2.2d.grb2'     % (dtime.year,
       dtime.year,dtime.month,
       dtime.year,dtime.month,dtime.day,
       dtime.year,dtime.month,dtime.day,dtime.hour)

    
    cube = iris.load_cube(url,long_name)
    slice = cube.extract(iris.Constraint(longitude=lambda cell: bbox[0]+360. < cell < bbox[1]+360.,
                                         latitude=lambda cell: bbox[2] < cell < bbox[3]))   
    slice.convert_units('degC')
    nc.variables['Potential_temperature'][i,:,:,:]=slice.data 
    nc.variables['time'][i] = int(dhours)
    nc.close()
    print '%d, Step %d,  %5.2f percent, elapsed time %5.3f seconds' % (i-istart, i,i*100./nsteps, (time()-time0))


# In[ ]:




# In[ ]:

# check file we created
cubes = iris.load(ofile)
print cubes[0]


# In[ ]:



