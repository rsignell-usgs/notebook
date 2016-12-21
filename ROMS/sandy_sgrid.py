# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# ### `pysgrid` only works with raw netCDF4 (for now!)

# <codecell>

from netCDF4 import Dataset

url = ('http://geoport.whoi.edu/thredds/dodsC/clay/usgs/users/'
               'jcwarner/Projects/Sandy/triple_nest/00_dir_NYB05.ncml')

nc = Dataset(url)

# <markdowncell>

# ### The sgrid object

# <codecell>

import pysgrid

# The object creation is a little bit slow.  Can we defer some of the loading/computations?
sgrid = pysgrid.from_nc_dataset(nc)

sgrid  # We need a better __repr__ and __str__ !!!

# <markdowncell>

# ### The object knows about sgrid conventions

# <codecell>

sgrid.edge1_coordinates, sgrid.edge1_dimensions, sgrid.edge1_padding

# <codecell>

u_var = sgrid.u
u_var.center_axis, u_var.node_axis

# <codecell>

v_var = sgrid.v
v_var.center_axis, v_var.node_axis

# <markdowncell>

# ### Being generic is nice!  This is an improvement up on my first design ;-) ...

# <codecell>

u_var.center_slicing

# <codecell>

v_var.center_slicing

# <markdowncell>

# (Don't be scared, you do not need the sgrid object to get the variables.  This just shows that there is a one-to-one mapping from the sgrid object to the netCDF4 object.)

# <codecell>

u_velocity = nc.variables[u_var.variable]
v_velocity = nc.variables[v_var.variable]

# <markdowncell>

# ### ... but we need a better way to deal with the slice of the slice!

# <codecell>

from datetime import datetime, timedelta
from netCDF4 import date2index

t_var = nc.variables['ocean_time']
start = datetime(2012, 10, 30, 0, 0)
time_idx = date2index(start, t_var, select='nearest')

v_idx = 0

# Slice of the slice!
u_data = u_velocity[time_idx, v_idx, u_var.center_slicing[-2], u_var.center_slicing[-1]]
v_data = v_velocity[time_idx, v_idx, v_var.center_slicing[-2], v_var.center_slicing[-1]]

# <markdowncell>

# ### Some thing for the angle information

# <codecell>

angle = sgrid.angle

angles = nc.variables[angle.variable][angle.center_slicing]

# <markdowncell>

# ### Average velocity vectors to cell centers

# <codecell>

from pysgrid.processing_2d import avg_to_cell_center

u_avg = avg_to_cell_center(u_data, u_var.center_axis)
v_avg = avg_to_cell_center(v_data, v_var.center_axis)

# <markdowncell>

# ### Rotate vectors by angles

# <codecell>

from pysgrid.processing_2d import rotate_vectors

u_rot, v_rot = rotate_vectors(u_avg, v_avg, angles)

# <markdowncell>

# ### Speed

# <codecell>

from pysgrid.processing_2d import vector_sum

uv_vector_sum = vector_sum(u_rot, v_rot)

# <markdowncell>

# ### Lon, lat of the center grid
# 
# (This is kind of clunky... or maybe I just do not get the sgrid concept beyond the ROMS world.)

# <codecell>

grid_cell_centers = sgrid.centers  # Array of lon, lat pairs.

lon_var_name, lat_var_name = sgrid.face_coordinates

sg_lon = getattr(sgrid, lon_var_name)
sg_lat = getattr(sgrid, lat_var_name)

lon_data = grid_cell_centers[..., 0][sg_lon.center_slicing]
lat_data = grid_cell_centers[..., 1][sg_lat.center_slicing]

# <markdowncell>

# ### Plotting

# <codecell>

%matplotlib inline

import numpy as np
import matplotlib.pyplot as plt

import cartopy.crs as ccrs
from cartopy.io import shapereader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER


def make_map(projection=ccrs.PlateCarree(), figsize=(9, 9)):
    fig, ax = plt.subplots(figsize=figsize,
                           subplot_kw=dict(projection=projection))
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    return fig, ax

# <codecell>

sub = 5
scale = 0.06

fig, ax = make_map()

kw = dict(scale=1.0/scale, pivot='middle', width=0.003, color='black')
q = plt.quiver(lon_data[::sub, ::sub], lat_data[::sub, ::sub],
               u_rot[::sub, ::sub], v_rot[::sub, ::sub], zorder=2, **kw)

cs = plt.pcolormesh(lon_data[::sub, ::sub],
                    lat_data[::sub, ::sub],
                    uv_vector_sum[::sub, ::sub], zorder=1, cmap=plt.cm.rainbow)

_ = ax.coastlines('10m')

# <codecell>


