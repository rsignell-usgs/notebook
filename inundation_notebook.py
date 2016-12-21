# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import time


start_time = time.time()

# <codecell>

import pytz
from datetime import datetime, timedelta


# Choose the date range (e.g: stop = datetime(2014, 7, 7, 12)).
stop = datetime(2015, 1, 30, 12)
run_name = '{:%Y-%m-%d}'.format(stop)

stop = stop.replace(tzinfo=pytz.utc)
start = stop - timedelta(days=7)

# NERACOOS Mass Bay Region.
bbox = [-72.0, 41.0, -69.0, 43.0]

# CF-names to look for (Sea Surface Height).
name_list = ['sea_surface_height',
             'sea_surface_elevation',
             'sea_surface_height_above_geoid',
             'sea_surface_height_above_sea_level',
             'water_surface_height_above_reference_datum',
             'sea_surface_height_above_reference_ellipsoid']

# <codecell>

import iris
import pyoos
import owslib

import logging as log
reload(log)

fmt = '{:*^64}'.format
log.captureWarnings(True)
LOG_FILENAME = 'log.txt'
log.basicConfig(filename=LOG_FILENAME,
                filemode='w',
                format='%(asctime)s %(levelname)s: %(message)s',
                datefmt='%I:%M:%S',
                level=log.INFO,
                stream=None)

log.info(fmt(' Run information '))
log.info('Run date: {:%Y-%m-%d %H:%M:%S}'.format(datetime.utcnow()))
log.info('Download start: {:%Y-%m-%d %H:%M:%S}'.format(start))
log.info('Download stop: {:%Y-%m-%d %H:%M:%S}'.format(stop))
log.info('Bounding box: {0:3.2f}, {1:3.2f},'
         '{2:3.2f}, {3:3.2f}'.format(*bbox))
log.info(fmt(' Software version '))
log.info('Iris version: {}'.format(iris.__version__))
log.info('owslib version: {}'.format(owslib.__version__))
log.info('pyoos version: {}'.format(pyoos.__version__))

# <codecell>

def fes_date_filter(start, stop, constraint='overlaps'):
    """Take datetime-like objects and returns a fes filter for date range.
    NOTE: Truncates the minutes!"""
    start = start.strftime('%Y-%m-%d %H:00')
    stop = stop.strftime('%Y-%m-%d %H:00')
    if constraint == 'overlaps':
        propertyname = 'apiso:TempExtent_begin'
        begin = fes.PropertyIsLessThanOrEqualTo(propertyname=propertyname,
                                                literal=stop)
        propertyname = 'apiso:TempExtent_end'
        end = fes.PropertyIsGreaterThanOrEqualTo(propertyname=propertyname,
                                                 literal=start)
    elif constraint == 'within':
        propertyname = 'apiso:TempExtent_begin'
        begin = fes.PropertyIsGreaterThanOrEqualTo(propertyname=propertyname,
                                                   literal=start)
        propertyname = 'apiso:TempExtent_end'
        end = fes.PropertyIsLessThanOrEqualTo(propertyname=propertyname,
                                              literal=stop)
    else:
        raise NameError('Unrecognized constraint {}'.format(constraint))
    return begin, end

# <codecell>

from owslib import fes

kw = dict(wildCard='*',
          escapeChar='\\',
          singleChar='?',
          propertyname='apiso:AnyText')

or_filt = fes.Or([fes.PropertyIsLike(literal=('*%s*' % val), **kw)
                  for val in name_list])

# Exculde ROMS Averages and History files.
not_filt = fes.Not([fes.PropertyIsLike(literal='*Averages*', **kw)])

begin, end = fes_date_filter(start, stop)
filter_list = [fes.And([fes.BBox(bbox), begin, end, or_filt, not_filt])]

# <codecell>

from owslib.csw import CatalogueServiceWeb

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw'
csw = CatalogueServiceWeb(endpoint, timeout=60)
csw.getrecords2(constraints=filter_list, maxrecords=1000, esn='full')

log.info(fmt(' Catalog information '))
log.info("URL: {}".format(endpoint))
log.info("CSW version: {}".format(csw.version))
log.info("Number of datasets available: {}".format(len(csw.records.keys())))

# <codecell>

def service_urls(records, service='odp:url'):
    """Extract service_urls of a specific type (DAP, SOS) from records."""
    service_string = 'urn:x-esri:specification:ServiceType:' + service
    urls = []
    for key, rec in records.items():
        # Create a generator object, and iterate through it until the match is
        # found if not found, gets the default value (here "none").
        url = next((d['url'] for d in rec.references if
                    d['scheme'] == service_string), None)
        if url is not None:
            urls.append(url)
    urls = sorted(set(urls))
    return urls

# <codecell>

dap_urls = service_urls(csw.records, service='odp:url')
sos_urls = service_urls(csw.records, service='sos:url')

log.info(fmt(' CSW '))
for rec, item in csw.records.items():
    log.info('{}'.format(item.title))

log.info(fmt(' DAP '))
for url in dap_urls:
    log.info('{}.html'.format(url))

log.info(fmt(' SOS '))
for url in sos_urls:
    log.info('{}'.format(url))

# <codecell>

from pyoos.collectors.coops.coops_sos import CoopsSos

collector = CoopsSos()
sos_name = 'water_surface_height_above_reference_datum'

datum = 'NAVD'
collector.set_datum(datum)
collector.end_time = stop
collector.start_time = start
collector.variables = [sos_name]

ofrs = collector.server.offerings
title = collector.server.identification.title
log.info(fmt(' Collector offerings '))
log.info('{}: {} offerings'.format(title, len(ofrs)))

# <codecell>

import requests
from urlparse import urlparse


# Web-parsing.
def parse_url(url):
    """This will preserve any given scheme but will add http if none is
    provided."""
    if not urlparse(url).scheme:
        url = "http://{}".format(url)
    return url


def sos_request(url='opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS', **kw):
    url = parse_url(url)
    offering = 'urn:ioos:network:NOAA.NOS.CO-OPS:CurrentsActive'
    params = dict(service='SOS',
                  request='GetObservation',
                  version='1.0.0',
                  offering=offering,
                  responseFormat='text/csv')
    params.update(kw)
    r = requests.get(url, params=params)
    r.raise_for_status()
    content = r.headers['Content-Type']
    if 'excel' in content or 'csv' in content:
        return r.url
    else:
        raise TypeError('Bad url {}'.format(r.url))

# <codecell>

from pandas import read_csv

params = dict(observedProperty=sos_name,
              eventTime=start.strftime('%Y-%m-%dT%H:%M:%SZ'),
              featureOfInterest='BBOX:{0},{1},{2},{3}'.format(*bbox),
              offering='urn:ioos:network:NOAA.NOS.CO-OPS:WaterLevelActive')

uri = 'http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS'
url = sos_request(uri, **params)
observations = read_csv(url)

log.info('SOS URL request: {}'.format(url))

# <markdowncell>

# #### Clean the dataframe (visualization purpose only)

# <codecell>

from lxml import etree
from urllib import urlopen
from IPython.display import HTML


def get_coops_longname(station):
    """Get longName for specific station from COOPS SOS using DescribeSensor
    request."""
    url = ('opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?service=SOS&'
           'request=DescribeSensor&version=1.0.0&'
           'outputFormat=text/xml;subtype="sensorML/1.0.1"&'
           'procedure=urn:ioos:station:NOAA.NOS.CO-OPS:%s') % station
    url = parse_url(url)
    tree = etree.parse(urlopen(url))
    root = tree.getroot()
    path = "//sml:identifier[@name='longName']/sml:Term/sml:value/text()"
    namespaces = dict(sml="http://www.opengis.net/sensorML/1.0.1")
    longName = root.xpath(path, namespaces=namespaces)
    if len(longName) == 0:
        longName = station
    return longName[0]

# <codecell>

columns = {'datum_id': 'datum',
           'sensor_id': 'sensor',
           'station_id': 'station',
           'latitude (degree)': 'lat',
           'longitude (degree)': 'lon',
           'vertical_position (m)': 'height',
           'water_surface_height_above_reference_datum (m)': 'ssh above datum'}

observations.rename(columns=columns, inplace=True)

observations['datum'] = [s.split(':')[-1] for s in observations['datum']]
observations['sensor'] = [s.split(':')[-1] for s in observations['sensor']]
observations['station'] = [s.split(':')[-1] for s in observations['station']]
observations['name'] = [get_coops_longname(s) for s in observations['station']]

observations.set_index('name', inplace=True)

observations.head()

# <markdowncell>

# #### Generate a uniform 6-min time base for model/data comparison

# <codecell>

from io import BytesIO
from iris.pandas import as_cube


def coops2df(collector, coops_id):
    """Request CSV response from SOS and convert to Pandas DataFrames."""
    collector.features = [coops_id]
    long_name = get_coops_longname(coops_id)
    response = collector.raw(responseFormat="text/csv")
    kw = dict(parse_dates=True, index_col='date_time')
    data_df = read_csv(BytesIO(response.encode('utf-8')), **kw)
    data_df.name = long_name
    return data_df


def save_timeseries(df, outfile, standard_name, **kw):
    """http://cfconventions.org/Data/cf-convetions/cf-conventions-1.6/build
    /cf-conventions.html#idp5577536"""
    cube = as_cube(df, calendars={1: iris.unit.CALENDAR_GREGORIAN})
    cube.coord("index").rename("time")
    cube.coord("columns").rename("station name")
    cube.rename(standard_name)

    longitude = kw.get("longitude")
    latitude = kw.get("latitude")
    if longitude is not None:
        longitude = iris.coords.AuxCoord(longitude,
                                         var_name="lon",
                                         standard_name="longitude",
                                         long_name="station longitude",
                                         units=iris.unit.Unit("degrees"))
    cube.add_aux_coord(longitude, data_dims=1)

    if latitude is not None:
        latitude = iris.coords.AuxCoord(latitude,
                                        var_name="lat",
                                        standard_name="latitude",
                                        long_name="station latitude",
                                        units=iris.unit.Unit("degrees"))
        cube.add_aux_coord(latitude, data_dims=1)

    # Work around iris to get String instead of np.array object.
    string_list = cube.coord("station name").points.tolist()
    cube.coord("station name").points = string_list
    cube.coord("station name").var_name = 'station'

    station_attr = kw.get("station_attr")
    if station_attr is not None:
        cube.coord("station name").attributes.update(station_attr)

    cube_attr = kw.get("cube_attr")
    if cube_attr is not None:
        cube.attributes.update(cube_attr)

    iris.save(cube, outfile)

# <codecell>

import iris
from pandas import DataFrame
from owslib.ows import ExceptionReport

iris.FUTURE.netcdf_promote = True

log.info(fmt(' Observations '))
fname = '{:%Y-%m-%d}-OBS_DATA.nc'.format(stop)

log.info(fmt(' Downloading to file {} '.format(fname)))
data = dict()
bad_datum = []
for station in observations.station:
    try:
        df = coops2df(collector, station)
        col = 'water_surface_height_above_reference_datum (m)'
        data.update({station: df[col]})
    except ExceptionReport as e:
        bad_datum.append(station)
        name = get_coops_longname(station)
        log.warning("[{}] {}:\n{}".format(station, name, e))
obs_data = DataFrame.from_dict(data)

# Split good and bad vertical datum stations.
pattern = '|'.join(bad_datum)
if pattern:
    non_navd = observations.station.str.contains(pattern)
    bad_datum = observations[non_navd]
    observations = observations[~non_navd]

comment = "Several stations from http://opendap.co-ops.nos.noaa.gov"
kw = dict(longitude=observations.lon,
          latitude=observations.lat,
          station_attr=dict(cf_role="timeseries_id"),
          cube_attr=dict(featureType='timeSeries',
                         Conventions='CF-1.6',
                         standard_name_vocabulary='CF-1.6',
                         cdm_data_type="Station",
                         comment=comment,
                         datum=datum,
                         url=url))

save_timeseries(obs_data, outfile=fname,
                standard_name=sos_name, **kw)

obs_data.head()

# <markdowncell>

# #### Loop discovered models and save the nearest time-series

# <codecell>

import signal
from contextlib import contextmanager

import numpy as np
from oceans import wrap_lon180

from iris import Constraint
from iris.cube import CubeList
from iris.exceptions import CoordinateMultiDimError

water_level = ['sea_surface_height',
               'sea_surface_elevation',
               'sea_surface_height_above_geoid',
               'sea_surface_height_above_sea_level',
               'water_surface_height_above_reference_datum',
               'sea_surface_height_above_reference_ellipsoid']


class TimeoutException(Exception):
    """
    Example
    -------
    >>> def long_function_call():
    >>>     import time
    >>>     sec = 0
    >>>>    while True:
    >>>         sec += 1
    >>>         print(sec)
    >>>         time.sleep(1)
    >>>
    >>> try:
    >>>     with time_limit(10):
    >>>     long_function_call()
    >>> except TimeoutException as msg:
    >>>     print("Timed out!")
    """
    pass


@contextmanager
def time_limit(seconds=10):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


# Iris.
def z_coord(cube):
    """Heuristic way to return **one** the vertical coordinate."""
    try:
        z = cube.coord(axis='Z')
    except CoordinateNotFoundError:
        z = None
        for coord in cube.coords(axis='Z'):
            if coord.name() not in water_level:
                z = coord
    return z


def get_surface(cube):
    """Work around `iris.cube.Cube.slices` error:
    The requested coordinates are not orthogonal."""
    z = z_coord(cube)
    if z:
        positive = z.attributes.get('positive', None)
        if positive == 'up':
            idx = np.unique(z.points.argmax(axis=0))[0]
        else:
            idx = np.unique(z.points.argmin(axis=0))[0]
        return cube[:, idx, ...]
    else:
        return cube


def time_coord(cube):
    """Return the variable attached to time axis and rename it to time."""
    try:
        cube.coord(axis='T').rename('time')
    except CoordinateNotFoundError:
        pass
    timevar = cube.coord('time')
    return timevar


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
    """Slice time by indexes using a nearest criteria.
    NOTE: Assumes time is the first dimension!"""
    istart = time_near(cube, start)
    if stop:
        istop = time_near(cube, stop)
        if istart == istop:
            raise ValueError('istart must be different from istop! '
                             'Got istart {!r} and '
                             ' istop {!r}'.format(istart, istop))
        return cube[istart:istop, ...]
    else:
        return cube[istart, ...]


def time_constraint(cube, start, stop):
    """Slice time by constraint."""
    begin = lambda cell: cell >= start
    end = lambda cell: cell <= stop
    constraint = Constraint(begin & end)
    return cube.extract(constraint)


def minmax(v):
    return np.min(v), np.max(v)


def bbox_extract_2Dcoords(cube, bbox):
    """Extract a sub-set of a cube inside a lon, lat bounding box
    bbox=[lon_min lon_max lat_min lat_max].
    NOTE: This is a work around too subset an iris cube that has
    2D lon, lat coords."""
    lons = cube.coord('longitude').points
    lats = cube.coord('latitude').points
    lons = wrap_lon180(lons)

    inregion = np.logical_and(np.logical_and(lons > bbox[0],
                                             lons < bbox[2]),
                              np.logical_and(lats > bbox[1],
                                             lats < bbox[3]))
    region_inds = np.where(inregion)
    imin, imax = minmax(region_inds[0])
    jmin, jmax = minmax(region_inds[1])
    return cube[..., imin:imax+1, jmin:jmax+1]


def bbox_extract_1Dcoords(cube, bbox):
    lat = Constraint(latitude=lambda cell: bbox[1] <= cell < bbox[3])
    lon = Constraint(longitude=lambda cell: bbox[0] <= cell <= bbox[2])
    cube = cube.extract(lon & lat)
    return cube


def subset(cube, bbox):
    """Sub sets cube with 1D or 2D lon, lat coords.
    Using `intersection` instead of `extract` we deal with 0--360
    longitudes automagically."""
    if (cube.coord(axis='X').ndim == 1 and cube.coord(axis='Y').ndim == 1):
        # Workaround `cube.intersection` hanging up on FVCOM models.
        title = cube.attributes.get('title', None)
        featureType = cube.attributes.get('featureType', None)
        if (('FVCOM' in title) or ('ESTOFS' in title) or
           featureType == 'timeSeries'):
            cube = bbox_extract_1Dcoords(cube, bbox)
        else:
            cube = cube.intersection(longitude=(bbox[0], bbox[2]),
                                     latitude=(bbox[1], bbox[3]))
    elif (cube.coord(axis='X').ndim == 2 and
          cube.coord(axis='Y').ndim == 2):
        cube = bbox_extract_2Dcoords(cube, bbox)
    else:
        msg = "Cannot deal with X:{!r} and Y:{!r} dimensions."
        raise CoordinateMultiDimError(msg.format(cube.coord(axis='X').ndim),
                                      cube.coord(axis='y').ndim)
    return cube


def get_cube(url, name_list, bbox=None, time=None, units=None, callback=None,
             constraint=None):
    """Only `url` and `name_list` are mandatory.  The kw args are:
    `bbox`, `callback`, `time`, `units`, `constraint`."""

    cubes = iris.load_raw(url, callback=callback)

    in_list = lambda cube: cube.standard_name in name_list
    cubes = CubeList([cube for cube in cubes if in_list(cube)])
    if not cubes:
        raise ValueError('Cube does not contain {!r}'.format(name_list))
    else:
        cube = cubes.merge_cube()

    if constraint:
        cube = cube.extract(constraint)
        if not cube:
            raise ValueError('No cube using {!r}'.format(constraint))
    if bbox:
        cube = subset(cube, bbox)
        if not cube:
            raise ValueError('No cube using {!r}'.format(bbox))
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
        if cube.units != units:
            cube.convert_units(units)
    return cube


def get_model_name(cube, url):
    url = parse_url(url)
    try:
        model_full_name = cube.attributes['title']
    except AttributeError:
        model_full_name = url
    mod_name = model_full_name.split()[0]
    return mod_name, model_full_name

# <codecell>

import warnings
from iris.exceptions import (CoordinateNotFoundError, ConstraintMismatchError,
                             MergeError)


log.info(fmt(' Models '))
cubes = dict()

with warnings.catch_warnings():
    # Suppress iris warnings :
    warnings.simplefilter("ignore")
    for k, url in enumerate(dap_urls):
        log.info('\n[Reading url {}/{}]: {}'.format(k+1, len(dap_urls), url))
        try:
            with time_limit(60*5):
                cube = get_cube(url, name_list=name_list,
                                bbox=bbox, time=(start, stop),
                                units=iris.unit.Unit('meters'))
            # TODO: Need a better way to identify model data and observed data.
            if cube.ndim > 1:
                mod_name, model_full_name = get_model_name(cube, url)
                cubes.update({mod_name: cube})
            else:
                log.warning('url {} is probably a timeSeries!'.format(url))
        except (RuntimeError, ValueError, MergeError, TimeoutException,
                ConstraintMismatchError, CoordinateNotFoundError) as e:
            log.warning('Cannot get cube for: {}\n{}'.format(url, e))

# <codecell>

import numpy.ma as ma
from scipy.spatial import cKDTree as KDTree


def standardize_fill_value(cube):
    """Work around default `fill_value` when obtaining
    `_CubeSignature` (iris) using `lazy_data()` (biggus).
    Warning use only when you DO KNOW that the slices should
    have the same `fill_value`!!!"""
    if ma.isMaskedArray(cube._my_data):
        fill_value = ma.empty(0, dtype=cube._my_data.dtype).fill_value
        cube._my_data.fill_value = fill_value
    return cube


def make_tree(cube):
    """Create KDTree."""
    lon = cube.coord(axis='X').points
    lat = cube.coord(axis='Y').points
    # Structured models with 1D lon, lat.
    if (lon.ndim == 1) and (lat.ndim == 1) and (cube.ndim == 3):
        lon, lat = np.meshgrid(lon, lat)
    # Unstructure are already paired!
    tree = KDTree(zip(lon.ravel(), lat.ravel()))
    return tree, lon, lat


def get_nearest_water(cube, tree, xi, yi, k=10, max_dist=0.04, min_var=0.01):
    """Find `k` nearest model data points from an iris `cube` at station
    lon: `xi`, lat: `yi` up to `max_dist` in degrees.  Must provide a Scipy's
    KDTree `tree`."""
    # TODO: Use rtree instead of KDTree.
    # NOTE: Based on the iris `_nearest_neighbour_indices_ndcoords`.

    distances, indices = tree.query(np.array([xi, yi]).T, k=k)
    if indices.size == 0:
        raise ValueError("No data found.")
    # Get data up to specified distance.
    mask = distances <= max_dist
    distances, indices = distances[mask], indices[mask]
    if distances.size == 0:
        msg = "No data near ({}, {}) max_dist={}.".format
        raise ValueError(msg(xi, yi, max_dist))
    # Unstructured model.
    if (cube.coord(axis='X').ndim == 1) and (cube.ndim == 2):
        i = j = indices
        unstructured = True
    # Structured model.
    else:
        unstructured = False
        if cube.coord(axis='X').ndim == 2:  # CoordinateMultiDim
            i, j = np.unravel_index(indices, cube.coord(axis='X').shape)
        else:
            shape = (cube.coord(axis='Y').shape[0],
                     cube.coord(axis='X').shape[0])
            i, j = np.unravel_index(indices, shape)
    # Use only data where the standard deviation of the time series exceeds
    # 0.01 m (1 cm) this eliminates flat line model time series that come from
    # land points that should have had missing values.
    series, dist, idx = None, None, None
    for dist, idx in zip(distances, zip(i, j)):
        if unstructured:  # NOTE: This would be so elegant in py3k!
            idx = (idx[0],)
        # This weird syntax allow for idx to be len 1 or 2.
        series = cube[(slice(None),)+idx]
        # Accounting for wet-and-dry models.
        arr = ma.masked_invalid(series.data).filled(fill_value=0)
        if arr.std() <= min_var:
            series = None
            break
    return series, dist, idx


def add_station(cube, station):
    """Add a station Auxiliary Coordinate and its name."""
    kw = dict(var_name="station", long_name="station name")
    coord = iris.coords.AuxCoord(station, **kw)
    cube.add_aux_coord(coord)
    return cube


def ensure_timeseries(cube):
    """Ensure that the cube is CF-timeSeries compliant."""
    if not cube.coord('time').shape == cube.shape[0]:
        cube.transpose()
    make_aux_coord(cube, axis='Y')
    make_aux_coord(cube, axis='X')

    cube.attributes.update({'featureType': 'timeSeries'})
    cube.coord("station name").attributes = dict(cf_role='timeseries_id')
    return cube


def make_aux_coord(cube, axis='Y'):
    """Make any given coordinate an Auxiliary Coordinate."""
    coord = cube.coord(axis=axis)
    cube.remove_coord(coord)
    if cube.ndim == 2:
        cube.add_aux_coord(coord, 1)
    else:
        cube.add_aux_coord(coord)
    return cube

# <codecell>

from iris.pandas import as_series


for mod_name, cube in cubes.items():
    fname = '{:%Y-%m-%d}-{}.nc'.format(stop, mod_name)
    log.info(fmt(' Saving to file {} '.format(fname)))
    # NOTE: 2D coords KDtree.  (Iris can only do 1D coords KDtree for now.)
    try:
        tree, lon, lat = make_tree(cube)
    except CoordinateNotFoundError as e:
        log.warning('Cannot create KDTree for: {}'.format(mod_name))
        continue
    # Get model series at observed locations.
    raw_series = dict()
    for station, obs in observations.iterrows():
        try:
            kw = dict(k=10, max_dist=0.04, min_var=0.01)
            args = cube, tree, obs.lon, obs.lat
            series, dist, idx = get_nearest_water(*args, **kw)
        except ValueError as e:
            log.warning(e)
            continue
        if not series:
            status = "Land "
        else:
            raw_series.update({obs['station']: series})
            series = as_series(series)
            status = "Water"

        log.info('[{}] {}'.format(status, obs.name))

    if raw_series:  # Save cube.
        for station, cube in raw_series.items():
            cube = standardize_fill_value(cube)
            cube = add_station(cube, station)
        try:
            cube = iris.cube.CubeList(raw_series.values()).merge_cube()
        except MergeError as e:
            log.warning(e)

        ensure_timeseries(cube)
        iris.save(cube, fname)
        del cube

    log.info('Finished processing [{}]: {}'.format(mod_name, url))

# <markdowncell>

# ### Add extra stations.

# <codecell>

include = dict({'Scituate, MA': dict(lon=-70.7166, lat=42.9259),
                'Wells, ME': dict(lon=-70.583883, lat=43.272411)})

models = dict()
extra_series = dict()
for station, obs in include.items():
    for mod_name, cube in cubes.items():
        mod_name, model_full_name = get_model_name(cube, url)
        try:
            tree, lon, lat = make_tree(cube)
        except CoordinateNotFoundError as e:
            log.warning('Cannot create KDTree for: {}'.format(mod_name))
            continue
        # Get model series at observed locations.
        try:
            kw = dict(k=10, max_dist=0.04, min_var=0.01)
            args = cube, tree, obs['lon'], obs['lat']
            series, dist, idx = get_nearest_water(*args, **kw)
        except ValueError as e:
            log.warning(e)
            continue
        if not series:
            status = "Land "
        else:
            status = "Water"
            models.update({mod_name: series})

        log.info('[{}] {}'.format(status, station))
    extra_series.update({station: models})
    models = dict()

# <markdowncell>

# #### Load saved files and interpolate to the observations time interval

# <codecell>

from iris.pandas import as_data_frame


def nc2df(fname):
    cube = iris.load_cube(fname)
    for coord in cube.coords(dimensions=[0]):
        name = coord.name()
        if name != 'time':
            cube.remove_coord(name)
    for coord in cube.coords(dimensions=[1]):
        name = coord.name()
        if name != 'station name':
            cube.remove_coord(name)
    df = as_data_frame(cube)
    if cube.ndim == 1:  # Horrible work around iris.
        station = cube.coord('station name').points[0]
        df.columns = [station]
    return df

# <codecell>

from glob import glob
from operator import itemgetter

from pandas import Panel

fname = '{}-OBS_DATA.nc'.format(run_name)
OBS_DATA = nc2df(fname)
OBS_DATA.index = OBS_DATA.index.tz_localize(start.tzinfo)

from pandas import date_range
index = date_range(start=start, end=stop, freq='6min', tz=start.tzinfo)

dfs = dict(OBS_DATA=OBS_DATA)
for fname in glob("*.nc"):
    if 'OBS_DATA' in fname:
        continue
    else:
        model = fname.split('.')[0].split('-')[-1]
        df = nc2df(fname)
        if len(df.index.values) != len(np.unique(df.index.values)):
            # FIXME: Horrible work around duplicate times.
            opts = dict(cols='index', take_last=True)
            df = df.reset_index().drop_duplicates(**opts).set_index('index')
        df.index = df.index.tz_localize(start.tzinfo)
        if False:  # if True interpolates to 6 min series.
            kw = dict(method='time', limit=30)
            df = df.reindex(index).interpolate(**kw).ix[index]
        dfs.update({model: df})

dfs = Panel.fromDict(dfs).swapaxes(0, 2)

# <markdowncell>

# ### Bias

# <codecell>

from pandas import DataFrame

panel = dfs.copy()
means = dict()
for station, df in panel.iteritems():
    df.dropna(axis=1, how='all', inplace=True)
    mean = df.mean()
    df = df - mean + mean['OBS_DATA']
    means.update({station: mean.drop('OBS_DATA') - mean['OBS_DATA']})

bias = DataFrame.from_dict(means).dropna(axis=1, how='all')
bias = bias.applymap('{:.2f}'.format).replace('nan', '--')

columns = dict()
[columns.update({station: get_coops_longname(station)}) for
 station in bias.columns.values]

bias.rename(columns=columns, inplace=True)

bias.T

# <markdowncell>

# ### Model skill

# <codecell>

def both_valid(x, y):
    """Returns a mask where both series are valid."""
    mask_x = np.isnan(x)
    mask_y = np.isnan(y)
    return np.logical_and(~mask_x, ~mask_y)

# <codecell>

from scipy.stats.stats import pearsonr


skills = dict()
for station, df in panel.iteritems():
    obs = df['OBS_DATA']
    skill = dict()
    for model, y in df.iteritems():
        if 'OBS_DATA' not in model:
            mask = both_valid(obs, y)
            r, p = pearsonr(obs[mask]-obs.mean(), y[mask]-y.mean())
            skill.update({model: r})
    skills.update({station: skill})

df = DataFrame.from_dict(skills)

columns = dict()
[columns.update({station: get_coops_longname(station)}) for
 station in df.columns.values]

df.rename(columns=columns, inplace=True)

# <codecell>

fname = 'skill.html'

df_skill = df.applymap('{:.2f}'.format).replace('nan', '--')

df_skill.T

# <markdowncell>

# ### Map

# <codecell>

from folium.folium import Map
import matplotlib.pyplot as plt
from IPython.display import IFrame


def get_coordinates(bbox):
    """Create bounding box coordinates for the map.  It takes flat or
    nested list/numpy.array and returns 4 points for the map corners."""
    bbox = np.asanyarray(bbox).ravel()
    if bbox.size == 4:
        bbox = bbox.reshape(2, 2)
        coordinates = []
        coordinates.append([bbox[0][1], bbox[0][0]])
        coordinates.append([bbox[0][1], bbox[1][0]])
        coordinates.append([bbox[1][1], bbox[1][0]])
        coordinates.append([bbox[1][1], bbox[0][0]])
        coordinates.append([bbox[0][1], bbox[0][0]])
    else:
        raise ValueError('Wrong number corners.'
                         '  Expected 4 got {}'.format(bbox.size))
    return coordinates


def inline_map(m):
    """Takes a folium instance or a html path and load into an iframe."""
    if isinstance(m, Map):
        m._build_map()
        srcdoc = m.HTML.replace('"', '&quot;')
        embed = HTML('<iframe srcdoc="{srcdoc}" '
                     'style="width: 100%; height: 500px; '
                     'border: none"></iframe>'.format(srcdoc=srcdoc))
    elif isinstance(m, str):
        embed = IFrame(m, width=750, height=500)
    return embed


def make_map(bbox, **kw):
    """Creates a folium map instance."""
    line = kw.pop('line', True)
    zoom_start = kw.pop('zoom_start', 7)

    lon, lat = np.array(bbox).reshape(2, 2).mean(axis=0)
    m = Map(width=750, height=500,
            location=[lat, lon], zoom_start=zoom_start)
    if line:
        # Create the map and add the bounding box line.
        kw = dict(line_color='#FF0000', line_weight=2)
        m.line(get_coordinates(bbox), **kw)
    return m


def plot_series():
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_ylabel('Sea surface height (m)')
    ax.set_ylim(-2.5, 2.5)
    ax.grid(True)
    return fig, ax

# <codecell>

# Clusters.
big_list = []
for fname in glob("*.nc"):
    if 'OBS_DATA' in fname:
        continue
    nc = iris.load_cube(fname)
    model = fname.split('-')[-1].split('.')[0]
    lons = nc.coord(axis='X').points
    lats = nc.coord(axis='Y').points
    stations = nc.coord('station name').points
    models = [model]*lons.size
    lista = zip(models, lons.tolist(), lats.tolist(), stations.tolist())
    big_list.extend(lista)

big_list.sort(key=itemgetter(3))
df = DataFrame(big_list, columns=['name', 'lon', 'lat', 'station'])
df.set_index('station', drop=True, inplace=True)
groups = df.groupby(df.index)

# <codecell>

from mpld3 import save_html
from mpld3.plugins import LineLabelTooltip, connect

mapa = make_map(bbox, line=True, states=False)

# Clusters.
for station, info in groups:
    station = get_coops_longname(station)
    for lat, lon, name in zip(info.lat, info.lon, info.name):
        location = lat, lon
        popup = '<b>{}</b>\n{}'.format(station, name)
        mapa.simple_marker(location=location, popup=popup,
                           clustered_marker=True)

# Model and observations.
resolution, width, height = 75, 7, 3
for station in dfs:
    sta_name = get_coops_longname(station)
    # This will eliminate all NaNs columns.
    df = dfs[station].dropna(axis=1, how='all')

    fig, ax = plot_series()
    labels = []
    for col in df.columns:
        # This restore the series to its original "index."
        # Not needed if interpolating the series.
        serie = df[col].dropna()
        lines = ax.plot(serie.index, serie, label=col,
                        linewidth=2.5, alpha=0.5)
        if 'OBS_DATA' not in col:
            text0 = col
            text1 = bias[sta_name][col]
            text2 = df_skill[sta_name][col]
            tooltip = '{}:\nbias {}\nskill: {}'.format
            labels.append(tooltip(text0, text1, text2))
        else:
            labels.append('OBS_DATA')

    kw = dict(loc='upper center', bbox_to_anchor=(0.5, 1.05), numpoints=1,
              ncol=2, framealpha=0)
    l = ax.legend(**kw)
    l.set_title("")  # Workaround str(None).

    [connect(fig, LineLabelTooltip(line, name))
     for line, name in zip(ax.lines, labels)]

    html = 'station_{}.html'.format(station)
    save_html(fig, '{}'.format(html))

    popup = "<div align='center'> {} <br><iframe src='{}' alt='image'"
    popup += "width='{}px' height='{}px' frameBorder='0'></div>"
    popup = popup.format('{}'.format(sta_name), html,
                         (width*resolution)+75, (height*resolution)+50)
    kw = dict(popup=popup, width=(width*resolution)+75)

    if (df.columns == 'OBS_DATA').all():
        kw.update(dict(marker_color="blue", marker_icon="ok"))
    else:
        kw.update(dict(marker_color="green", marker_icon="ok-sign"))
    obs = observations[observations['station'] == station].squeeze()
    mapa.simple_marker(location=[obs['lat'], obs['lon']], **kw)

# Bad datum.
if isinstance(bad_datum, DataFrame):
    for station, obs in bad_datum.iterrows():
        popup = '<b>Station:</b> {}<br><b>Datum:</b> {}<br>'
        popup = popup.format(station, obs['datum'])
        kw = dict(popup=popup, marker_color="red", marker_icon="question-sign")
        mapa.simple_marker(location=[obs['lat'], obs['lon']], **kw)

# <codecell>

for station in include.keys():
    models = extra_series[station]
    if models:
        fig, ax = plot_series()
        labels = []
        for model, cube in models.items():
            t = time_coord(cube)
            t = t.units.num2date(t.points)
            lines = ax.plot(t, cube.data, linewidth=2.5, alpha=0.5,
                            label=model)
            labels.append(model)

        kw = dict(loc='upper center', bbox_to_anchor=(0.5, 1.05), numpoints=1,
                  ncol=2, framealpha=0)
        l = ax.legend(**kw)
        l.set_title("")  # Workaround str(None).

        [connect(fig, LineLabelTooltip(line, name))
         for line, name in zip(ax.lines, labels)]

        html = 'station_{}.html'.format
        html = html(station.lower().replace(' ', '_').replace(',', ''))
        save_html(fig, '{}'.format(html))

        popup = "<div align='center'> {} <br><iframe src='{}' alt='image'"
        popup += "width='{}px' height='{}px' frameBorder='0'></div>"
        popup = popup.format('{}'.format(sta_name), html,
                             (width*resolution)+75, (height*resolution)+50)
        kw = dict(popup=popup, width=(width*resolution)+75)

        kw.update(dict(marker_color="green", marker_icon="ok"))
        obs = observations[observations['station'] == station].squeeze()
        mapa.simple_marker(location=[include[station]['lat'],
                                     include[station]['lon']], **kw)

# <codecell>

mapa.create_map(path='mapa.html')
inline_map('mapa.html')

# <codecell>

elapsed = time.time() - start_time
log.info('{:.2f} minutes'.format(elapsed/60.))
log.info('EOF')

# <codecell>

with open('log.txt') as f:
    print(f.read())

