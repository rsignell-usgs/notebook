# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

%matplotlib inline

import time
import contextlib
from datetime import datetime, timedelta

import numpy as np
import numpy.ma as ma
import matplotlib.tri as tri
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay

import iris
from iris.unit import Unit
from iris.exceptions import CoordinateNotFoundError

import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature, COLORS
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

LAND = NaturalEarthFeature('physical', 'land', '10m', edgecolor='face',
                           facecolor=COLORS['land'])

iris.FUTURE.netcdf_promote = True
iris.FUTURE.cell_datetime_objects = True  # <- TODO!


def time_coord(cube):
    """Return the variable attached to time axis and rename it to time."""
    try:
        cube.coord(axis='T').rename('time')
    except CoordinateNotFoundError:
        pass
    timevar = cube.coord('time')
    return timevar


def z_coord(cube):
    """Heuristic way to return the dimensionless vertical coordinate."""
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


def plot_surface(cube, model='', unstructure=False, **kw):
    projection = kw.pop('projection', ccrs.PlateCarree())
    figsize = kw.pop('figsize', (8, 6))
    cmap = kw.pop('cmap', plt.cm.rainbow)

    fig, ax = plt.subplots(figsize=figsize,
                           subplot_kw=dict(projection=projection))
    ax.set_extent(get_bbox(cube))
    ax.add_feature(LAND)
    ax.coastlines(resolution='10m')
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER

    z = z_coord(cube)
    if z:
        positive = z.attributes.get('positive', None)
        if positive == 'up':
            idx = np.unique(z.points.argmax(axis=0))[0]
        else:
            idx = np.unique(z.points.argmin(axis=0))[0]
        c = cube[idx, ...].copy()
    else:
        idx = None
        c = cube.copy()
    c.data = ma.masked_invalid(c.data)
    t = time_coord(cube)
    t = t.units.num2date(t.points)[0]
    if unstructure:
        # The following lines would work if the cube is note bbox-sliced.
        # lon = cube.mesh.nodes[:, 0]
        # lat = cube.mesh.nodes[:, 1]
        # nv = cube.mesh.faces
        lon = cube.coord(axis='X').points
        lat = cube.coord(axis='Y').points
        nv = Delaunay(np.c_[lon, lat]).vertices
        triang = tri.Triangulation(lon, lat, triangles=nv)
        # http://matplotlib.org/examples/pylab_examples/ tricontour_smooth_delaunay.html
        if False:  # TODO: Test this.
            subdiv = 3
            min_circle_ratio = 0.01
            mask = tri.TriAnalyzer(triang).get_flat_tri_mask(min_circle_ratio)
            triang.set_mask(mask)
            refiner = tri.UniformTriRefiner(triang)
            tri_ref, data_ref = refiner.refine_field(cube.data, subdiv=subdiv)
        cs = ax.tricontourf(triang, c.data, cmap=cmap, **kw)
    else:
        cs = ax.pcolormesh(c.coord(axis='X').points,
                           c.coord(axis='Y').points,
                           c.data, cmap=cmap, **kw)
    title = (model, t, c.name(), idx)
    ax.set_title('{}: {}\nVariable: {} level: {}'.format(*title))
    return fig, ax, cs


def get_bbox(cube):
    xmin = cube.coord(axis='X').points.min()
    xmax = cube.coord(axis='X').points.max()
    ymin = cube.coord(axis='Y').points.min()
    ymax = cube.coord(axis='Y').points.max()
    return [xmin, xmax, ymin, ymax]


@contextlib.contextmanager
def timeit(log=None):
    t = time.time()
    yield
    elapsed = time.strftime("%H:%M:%S", time.gmtime(time.time()-t))
    if log:
        log.info(elapsed)
    else:
        print(elapsed)

# <codecell>

model = 'NECOFS_FVCOM'

start = datetime.utcnow() - timedelta(days=7)

bbox = [-70.8, 41.4, -69.9, 42.3]

units = Unit('Kelvin')

# <markdowncell>

# #### No horizontal subset works fine.

# <codecell>

with timeit():
    url = "http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/"
    url += "Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc"

    cube = iris.load_cube(url, 'sea_water_potential_temperature')
    cube = time_slice(cube, start, None)
    cube.convert_units(units)
    print(cube)
    
fig, ax, cs = plot_surface(cube, model, unstructure=True)
cbar = fig.colorbar(cs, extend='both', shrink=0.75)
t = cbar.ax.set_title(cube.units)

# <markdowncell>

# #### If forcing the `X` and `Y` the subset works.

# <codecell>

with timeit():
    url = "http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/"
    url += "Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc"

    cube = iris.load_cube(url, 'sea_water_potential_temperature')
    cube = time_slice(cube, start, None)
    cube.convert_units(units)
    print(cube.coord(axis='Y'))
    print(cube.coord(axis='X'))
    print(cube.coord(axis='Z'))
    print("\n")
    cube = cube.intersection(longitude=(bbox[0], bbox[2]),
                             latitude=(bbox[1], bbox[3]))
    print(cube)
    
fig, ax, cs = plot_surface(cube, model, unstructure=True)
cbar = fig.colorbar(cs, extend='both', shrink=0.75)
t = cbar.ax.set_title(cube.units)

# <markdowncell>

# #### Trying to subset directly takes forever...

# <codecell>

with timeit():
    url = "http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/"
    url += "Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc"

    cube = iris.load_cube(url, 'sea_water_potential_temperature')
    cube = time_slice(cube, start, None)
    cube.convert_units(units)
    cube = cube.intersection(longitude=(bbox[0], bbox[2]),
                             latitude=(bbox[1], bbox[3]))
    print(cube)
    
fig, ax, cs = plot_surface(cube, model, unstructure=True)
cbar = fig.colorbar(cs, extend='both', shrink=0.75)
t = cbar.ax.set_title(cube.units)

