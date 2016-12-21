# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

#
# test_FVCOM.py
#
# purpose:  Test FVCOM with iris
# author:   Filipe P. A. Fernandes
# e-mail:   ocefpaf@gmail
# web:      http://ocefpaf.github.io/
# created:  14-Jan-2015
# modified: Wed 14 Jan 2015 08:41:07 PM BRT
#
# obs:
#

import pytz
from datetime import datetime, timedelta

import iris
from iris.cube import CubeList

# <codecell>

!conda list iris

# <codecell>

iris.__version__

# <codecell>

def time_coord(cube):
    """Return the variable attached to time axis and rename it to time."""
    try:
        cube.coord(axis='T').rename('time')
    except CoordinateNotFoundError:
        pass
    timevar = cube.coord('time')
    return timevar

# <codecell>

def time_near(cube, datetime):
    """Return the nearest index to a `datetime`."""
    timevar = time_coord(cube)
    try:
        time = timevar.units.date2num(datetime)
        idx = timevar.nearest_neighbour_index(time)
    except IndexError:
        idx = -1
    return idx

# <codecell>

stop = datetime(2014, 7, 7, 12)
stop = stop.replace(tzinfo=pytz.utc)
start = stop - timedelta(days=7)

bbox = [-87.40, 24.25, -74.70, 36.70]

units = iris.unit.Unit('celsius')

name_list = ['sea_water_temperature',
             'sea_surface_temperature',
             'sea_water_potential_temperature',
             'equivalent_potential_temperature',
             'sea_water_conservative_temperature',
             'pseudo_equivalent_potential_temperature']

url = "http://crow.marine.usf.edu:8080/thredds/dodsC/FVCOM-Nowcast-Agg.nc"
cubes = iris.load_raw(url)

in_list = lambda cube: cube.standard_name in name_list
cubes = CubeList([cube for cube in cubes if in_list(cube)])
cube = cubes.merge_cube()

lat = iris.Constraint(latitude=lambda cell: bbox[1] <= cell < bbox[3])
lon = iris.Constraint(longitude=lambda cell: bbox[0] <= cell <= bbox[2])
cube = cube.extract(lon & lat)

istart = time_near(cube, start)
istop = time_near(cube, stop)
cube = cube[istart:istop, ...]

# <codecell>

print cube

# <codecell>


