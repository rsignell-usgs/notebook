
# coding: utf-8

# In[1]:

import iris
from iris.unit import Unit
from iris.cube import CubeList
from iris.exceptions import CoordinateNotFoundError, CoordinateMultiDimError

iris.FUTURE.netcdf_promote = True
iris.FUTURE.cell_datetime_objects = True


def time_coord(cube):
    """Return the variable attached to time axis and rename it to time."""
    try:
        cube.coord(axis='T').rename('time')
    except CoordinateNotFoundError:
        pass
    timevar = cube.coord('time')
    return timevar


def z_coord(cube):
    """Heuristic way to return the
    dimensionless vertical coordinate."""
    try:
        z = cube.coord(axis='Z')
    except CoordinateNotFoundError:
        z = cube.coords(axis='Z')
        for coord in cube.coords(axis='Z'):
            if coord.ndim == 1:
                z = coord
    return z


def time_near(cube, datetime):
    """Return the nearest index to a `datetime`."""
    timevar = time_coord(cube)
    try:
        time = timevar.units.date2num(datetime)
        idx = timevar.nearest_neighbour_index(time)
    except IndexError:
        idx = -1
    return idx


def time_slice(cube, start, stop=None):
    """TODO: Re-write to use `iris.FUTURE.cell_datetime_objects`."""
    istart = time_near(cube, start)
    if stop:
        istop = time_near(cube, stop)
        if istart == istop:
            raise ValueError('istart must be different from istop!'
                             'Got istart {!r} and '
                             ' istop {!r}'.format(istart, istop))
        return cube[istart:istop, ...]
    else:
        return cube[istart, ...]


def bbox_extract_2Dcoords(cube, bbox):
    """Extract a sub-set of a cube inside a lon, lat bounding box
    bbox=[lon_min lon_max lat_min lat_max].
    NOTE: This is a work around too subset an iris cube that has
    2D lon, lat coords."""
    lons = cube.coord('longitude').points
    lats = cube.coord('latitude').points

    def minmax(v):
        return np.min(v), np.max(v)

    inregion = np.logical_and(np.logical_and(lons > bbox[0],
                                             lons < bbox[2]),
                              np.logical_and(lats > bbox[1],
                                             lats < bbox[3]))
    region_inds = np.where(inregion)
    imin, imax = minmax(region_inds[0])
    jmin, jmax = minmax(region_inds[1])
    return cube[..., imin:imax+1, jmin:jmax+1]


def intersection(cube, bbox):
    """Sub sets cube with 1D or 2D lon, lat coords.
    Using `intersection` instead of `extract` we deal with 0-360
    longitudes automagically."""
    try:
        method = "Using iris `cube.intersection`"
        cube = cube.intersection(longitude=(bbox[0], bbox[2]),
                                 latitude=(bbox[1], bbox[3]))
    except CoordinateMultiDimError:
        method = "Using iris `bbox_extract_2Dcoords`"
        cube = bbox_extract_2Dcoords(cube, bbox)
    print(method)
    return cube


def get_cube(url, name_list=None, bbox=None, time=None, units=None):
    cubes = iris.load_raw(url)
    if name_list:
        in_list = lambda cube: cube.standard_name in name_list
        cubes = CubeList([cube for cube in cubes if in_list(cube)])
        if not cubes:
            raise ValueError('Cube does not contain {!r}'.format(name_list))
        else:
            cube = cubes.merge_cube()
    if bbox:
        cube = intersection(cube, bbox)
    if time:
        if isinstance(time, datetime):
            start, stop = time, None
        elif isinstance(time, tuple):
            start, stop = time[0], time[1]
        else:
            raise ValueError('Time must be start or (start, stop).'
                             '  Got {!r}'.format(time))
        cube = time_slice(cube, start, stop)
    if units:
        if not cube.units == units:
            cube.convert_units(units)
    return cube


# In[2]:

import time
import contextlib


@contextlib.contextmanager
def timeit(log=None):
    t = time.time()
    yield
    elapsed = time.strftime("%H:%M:%S", time.gmtime(time.time()-t))
    if log:
        log.info(elapsed)
    else:
        print(elapsed)


# In[3]:

get_ipython().magic('matplotlib inline')
import numpy as np
import numpy.ma as ma
import iris.quickplot as qplt
import matplotlib.pyplot as plt


def plot_surface(cube, model=''):
    z = z_coord(cube)
    positive = z.attributes.get('positive', None)
    if positive == 'up':
        idx = np.argmax(z.points)
    else:
        idx = np.argmin(z.points)

    c = cube[idx, ...]
    c.data = ma.masked_invalid(c.data)
    t = time_coord(cube)
    t = t.units.num2date(t.points)[0]
    qplt.pcolormesh(c)
    plt.title('{}: {}\nVariable: {} level: {}'.format(model, t, c.name(), idx))


# In[4]:

print(iris.__version__)
print(iris.__file__)


# In[5]:

from datetime import datetime, timedelta

start = datetime.utcnow() - timedelta(days=7)
stop = datetime.utcnow()

name_list = ['sea_water_potential_temperature', 'sea_water_temperature']

bbox = [-76.4751, 38.3890, -71.7432, 42.9397]

units = Unit('Kelvin')


# In[6]:

model = 'MARACOOS/ESPRESSO'
url = 'http://tds.marine.rutgers.edu/thredds/dodsC/roms/espresso/2009_da/his'

with timeit():
    cube = get_cube(url, name_list=name_list, bbox=bbox,
                    time=start, units=units)
    plot_surface(cube, model)


# In[7]:

model = 'USGS/COAWST'
url = 'http://geoport.whoi.edu/thredds/dodsC/coawst_4/use/fmrc/'
url += 'coawst_4_use_best.ncd'

with timeit():
    cube = get_cube(url, name_list=name_list, bbox=bbox,
                    time=start, units=units)
    plot_surface(cube, model)


# In[8]:

model = 'HYCOM'
url = 'http://ecowatch.ncddc.noaa.gov/thredds/dodsC/hycom/hycom_reg1_agg/'
url += 'HYCOM_Region_1_Aggregation_best.ncd'

with timeit():
    cube = get_cube(url, name_list=name_list, bbox=bbox,
                    time=start, units=units)
    plot_surface(cube, model)


# In[9]:

model = 'NYHOP'
url = 'http://colossus.dl.stevens-tech.edu/thredds/dodsC/fmrc/NYBight/'
url += 'NYHOPS_Forecast_Collection_for_the_New_York_Bight_best.ncd'

with timeit():
    cube = get_cube(url, name_list=name_list, bbox=bbox,
                    time=start, units=units)
    plot_surface(cube, model)


# In[10]:

model = 'RUTGERS/NWA'
url = 'http://oceanus.esm.rutgers.edu:8090/thredds/dodsC/ROMS/NWA/Run03/Output'

with timeit():
    cube = get_cube(url, name_list=name_list, bbox=bbox,
                    time=start, units=units)
    plot_surface(cube, model)

