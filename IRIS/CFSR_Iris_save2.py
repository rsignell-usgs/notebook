
# coding: utf-8

# In[1]:

from pylab import * 
import iris
import iris.plot as iplt
import cartopy.crs as ccrs
import netCDF4
import datetime as dt


# In[22]:

year = 2005
start = dt.datetime(year,1,1,0,0,0)
stop = dt.datetime(year,12,31,18,0,0)
bbox = [-77.+360., -63.+360., 34., 46.]   # [lon_min lon_max lat_min lat_max]


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

var_name = 'Potential_temperature'
cube = cubes[where([cube.var_name==var_name for cube in cubes])[0]]
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


# In[30]:

nci = netCDF4.Dataset(url)
lon = nci.variables['lon'][:]
lat = nci.variables['lat'][:]
bi=(lon>=bbox[0])&(lon<=bbox[1])
bj=(lat>=bbox[2])&(lat<=bbox[3])
nci.close()


# In[31]:

origin = dt.datetime(1900,1,1,0,0,0)
nsteps = int((stop - start).total_seconds()/3600/6)  # 6 hour time steps
print nsteps

nc = netCDF4.Dataset(ofile,'r+')
nc.variables['time'].units = 'hours since 1900-01-01T00:00:00Z'

for i in range(nsteps):
    dtime = start + dt.timedelta(hours=(6*i))
    dhours=(dtime - origin).total_seconds()/3600.
    url='http://nomads.ncdc.noaa.gov/thredds/dodsC/modeldata/cmd_ocnh/%4.4d/%4.4d%2.2d/%4.4d%2.2d%2.2d/ocnh01.gdas.%4.4d%2.2d%2.2d%2.2d.grb2'     % (dtime.year,
       dtime.year,dtime.month,
       dtime.year,dtime.month,dtime.day,
       dtime.year,dtime.month,dtime.day,dtime.hour)
    print '%5.2f percent complete in %5.3f hours' % (i*100./nsteps, (time()-time0)/3600.)
    nci = netCDF4.Dataset(url)
    data = nci.variables[var_name][:,:,bj,bi]
    nci.close()
    # hack here to convert Kelvin to Celcius since we are using NetCDF4
    nc.variables[var_name][i,:,:,:]= data - 273.15
    nc.variables['time'][i] = int(dhours)


# In[ ]:

nc.close()


# In[ ]:

# check file we created
cubes = iris.load(ofile)
print cubes[0]

