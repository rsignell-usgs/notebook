
# coding: utf-8

# The problem: CF compliant readers cannot read  HOPS dataset directly.
# The solution: read with the `netCDF4-python` raw interface and create a CF object from the data.
# 
# NOTE: Ideally this should be a `nco` script that could be run as a CLI script and fix the files.
# Here I am using `Python`+`iris`. That works and could be written as a CLI script too.
# The main advantage is that it takes care of the CF boilerplate.
# However, this approach is to "heavy-weight" to be applied in many variables and files.

# In[1]:

from netCDF4 import Dataset

url = ('http://geoport.whoi.edu/thredds/dodsC/usgs/data2/rsignell/gdrive/'
       'nsf-alpha/Data/MIT_MSEAS/MSEAS_Tides_20160317/mseas_tides_2015071612_2015081612_01h.nc')

nc = Dataset(url)


# Extract `lon`, `lat` variables from `vgrid2` and `u`, `v` variables from `vbaro`.
# The goal is to split the joint variables into individual CF compliant phenomena.

# In[2]:

vtime = nc['time']
coords = nc['vgrid2']
vbaro = nc['vbaro']


# Using iris to create the CF object.
# 
# NOTE: ideally `lon`, `lat` should be `DimCoord` like time and not `AuxCoord`,
# but iris refuses to create 2D `DimCoord`. Not sure if CF enforces that though.

# First the Coordinates.
# 
# FIXME: change to a full time slice later!

# In[3]:

import iris
iris.FUTURE.netcdf_no_unlimited = True

longitude = iris.coords.AuxCoord(coords[:, :, 0],
                                 var_name='vlat',
                                 long_name='lon values',
                                 units='degrees')

latitude = iris.coords.AuxCoord(coords[:, :, 1],
                                var_name='vlon',
                                long_name='lat values',
                                units='degrees')

# Dummy Dimension coordinate to avoid default names.
# (This is either a bug in CF or in iris. We should not need to do this!)
lon = iris.coords.DimCoord(range(866),
                           var_name='x',
                           long_name='lon_range',
                           standard_name='longitude')

lat = iris.coords.DimCoord(range(1032),
                           var_name='y',
                           long_name='lat_range',
                           standard_name='latitude')


# Now the phenomena.
# 
# NOTE: You don't need the `broadcast_to` trick if saving more than 1 time step.
# Here I just wanted the single time snapshot to have the time dimension to create a full example.

# In[4]:

import numpy as np

u_cubes = iris.cube.CubeList()
v_cubes = iris.cube.CubeList()


for k in range(2):  # vbaro.shape[0]
    time = iris.coords.DimCoord(vtime[k],
                                var_name='time',
                                long_name=vtime.long_name,
                                standard_name='time',
                                units=vtime.units)
    
    u = vbaro[k, :, :, 0]
    u_cubes.append(iris.cube.Cube(np.broadcast_to(u, (1,) + u.shape),
                                  units=vbaro.units,
                                  long_name=vbaro.long_name,
                                  var_name='u',
                                  standard_name='barotropic_eastward_sea_water_velocity',
                                  dim_coords_and_dims=[(time, 0), (lon, 1), (lat, 2)],
                                  aux_coords_and_dims=[(latitude, (1, 2)),
                                                       (longitude, (1, 2))]))

    v = vbaro[k, :, :, 1]
    v_cubes.append(iris.cube.Cube(np.broadcast_to(v, (1,) + v.shape),
                                  units=vbaro.units,
                                  long_name=vbaro.long_name,
                                  var_name='v',
                                  standard_name='barotropic_northward_sea_water_velocity',
                                  dim_coords_and_dims=[(time, 0), (lon, 1), (lat, 2)],
                                  aux_coords_and_dims=[(longitude, (1, 2)),
                                                       (latitude, (1, 2))]))


# Join the individual CF phenomena into one dataset.

# In[5]:

u_cube = u_cubes.concatenate_cube()
v_cube = v_cubes.concatenate_cube()

cubes = iris.cube.CubeList([u_cube, v_cube])


# Save the CF-compliant file!

# In[6]:

iris.save(cubes, 'hops.nc')


# In[7]:

get_ipython().system(u'ncdump -h hops.nc')

