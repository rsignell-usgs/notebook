# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# # IOOS System Test: [Extreme Events Theme]
# (https://github.com/ioos/system-test/wiki/Development-of-Test-Themes#
# wiki-theme-2-extreme-events):  Inundation
# 
# ### Compare modeled water levels with observations for a specified bounding box
# and time period using IOOS recommended service standards for catalog search
# (CSW) and data retrieval (OPeNDAP & SOS).
# 
# * Query CSW to find datasets that match criteria
# * Extract OPeNDAP data endpoints from model datasets and SOS endpoints from
#   observational datasets
# * OPeNDAP model datasets will be granules
# * SOS endpoints may be datasets (from ncSOS) or collections of datasets (from
#   NDBC, CO-OPS SOS servers)
# * Filter SOS services to obtain datasets
# * Extract data from SOS datasets
# * Extract data from model datasets at locations of observations
# * Compare time series data on same vertical datum

# <codecell>

# Standard Library.
from warnings import warn
from datetime import datetime, timedelta

# Scientific stack.
import iris
iris.FUTURE.netcdf_promote = True

import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy
from cartopy.io.img_tiles import MapQuestOpenAerial
from pandas import DataFrame, date_range, read_csv, concat

from iris.exceptions import CoordinateNotFoundError, ConstraintMismatchError

# Custom IOOS/ASA modules (available at PyPI).
from owslib import fes
from owslib.csw import CatalogueServiceWeb
from pyoos.collectors.coops.coops_sos import CoopsSos

# Local imports
from utilities import name_list, sos_name
from utilities import (fes_date_filter, coops2df, find_timevar, find_ij, nearxy,
                       service_urls, mod_df)

# <markdowncell>

# ### Specify a time range and bounding box of interest:

# <codecell>

dates = {'Hurricane sandy':
         [datetime(2012, 10, 26), datetime(2012, 11, 2)],
         '2014 Feb 10-15 Storm':
         [datetime(2014, 2, 10), datetime(2014, 2, 15)],
         '2014 Recent': [datetime(2014, 3, 8), datetime(2014, 3, 11)],
         '2011': [datetime(2013, 4, 20), datetime(2013, 4, 24)]}

jd_now = datetime.utcnow()
jd_start,  jd_stop = jd_now - timedelta(days=3), jd_now + timedelta(days=3)

start_date = jd_start.strftime('%Y-%m-%d %H:00')
stop_date = jd_stop.strftime('%Y-%m-%d %H:00')

jd_start = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
jd_stop = datetime.strptime(stop_date, '%Y-%m-%d %H:%M')

print('%s to %s' % (start_date, stop_date))

# <codecell>

# Bounding Box [lon_min, lat_min, lon_max, lat_max]
area = {'Hawaii': [-160.0, 18.0, -154., 23.0],
        'Gulf of Maine': [-72.0, 41.0, -69.0, 43.0],
        'New York harbor region': [-75., 39., -71., 41.5]}

box = area['New York harbor region']

# <markdowncell>

# ### Search CSW for datasets of interest

# <codecell>

if False:
    from IPython.core.display import HTML
    url = 'http://www.ngdc.noaa.gov/geoportal/'
    HTML('<iframe src=%s width=950 height=400></iframe>' % url)

# <codecell>

# Connect to CSW, explore it's properties.
CSW = {'NGDC Geoportal':
       'http://www.ngdc.noaa.gov/geoportal/csw',
       'USGS WHSC Geoportal':
       'http://geoport.whoi.edu/geoportal/csw',
       'NODC Geoportal: granule level':
       'http://www.nodc.noaa.gov/geoportal/csw',
       'NODC Geoportal: collection level':
       'http://data.nodc.noaa.gov/geoportal/csw',
       'NRCAN CUSTOM':
       'http://geodiscover.cgdi.ca/wes/serviceManagerCSW/csw',
       'USGS Woods Hole GI_CAT':
       'http://geoport.whoi.edu/gi-cat/services/cswiso',
       'USGS CIDA Geonetwork':
       'http://cida.usgs.gov/gdp/geonetwork/srv/en/csw',
       'USGS Coastal and Marine Program':
       'http://cmgds.marine.usgs.gov/geonetwork/srv/en/csw',
       'USGS Woods Hole Geoportal':
       'http://geoport.whoi.edu/geoportal/csw',
       'CKAN testing site for new Data.gov':
       'http://geo.gov.ckan.org/csw',
       'EPA':
       'https://edg.epa.gov/metadata/csw',
       'CWIC':
       'http://cwic.csiss.gmu.edu/cwicv1/discovery'}

endpoint = CSW['NGDC Geoportal']
csw = CatalogueServiceWeb(endpoint, timeout=60)
csw.version

# <codecell>

csw.get_operation_by_name('GetRecords').constraints

# <markdowncell>

# ### Convert User Input into FES filters.

# <codecell>

start, stop = fes_date_filter(start_date, stop_date)
bbox = fes.BBox(box)

# <codecell>

or_filt = fes.Or([fes.PropertyIsLike(propertyname='apiso:AnyText',
                                     literal=('*%s*' % val),
                                     escapeChar='\\',
                                     wildCard='*',
                                     singleChar='?') for val in name_list])

# <markdowncell>

# ROMS model output often has Averages and History files.  The Averages files are usually averaged over a tidal cycle or more, while the History files are snapshots at that time instant.  We are not interested in averaged data for this test, so in the cell below we remove any Averages files here by removing any datasets that have the term "Averages" in the metadata text.  A better approach would be to look at the `cell_methods` attributes propagated through to some term in the ISO metadata, but this is not implemented yet, as far as I know

# <codecell>

val = 'Averages'
not_filt = fes.Not([fes.PropertyIsLike(propertyname='apiso:AnyText',
                                       literal=('*%s*' % val),
                                       escapeChar='\\',
                                       wildCard='*',
                                       singleChar='?')])

filter_list = [fes.And([bbox, start, stop, or_filt, not_filt])]

# <markdowncell>

# Try request using multiple filters "and" syntax: [[filter1,filter2]].

# <codecell>

csw.getrecords2(constraints=filter_list, maxrecords=1000, esn='full')
print(len(csw.records.keys()))

# <markdowncell>

# Now print out some titles

# <codecell>

for rec, item in csw.records.items():
    print(item.title)

# <markdowncell>

# Print out all the OPeNDAP Data URL endpoints

# <codecell>

dap_urls = service_urls(csw.records,
                        service='odp:url')
print("\n".join(dap_urls))

# <markdowncell>

# Print out all the SOS Data URL endpoints

# <codecell>

sos_urls = service_urls(csw.records,
                        service='sos:url')
print("\n".join(sos_urls))

# <markdowncell>

# ## 1. Get observations from SOS
# Here we are using a custom class from pyoos to read the CO-OPS SOS.  This is definitely unsavory, as the whole point of using a standard is avoid the need for custom classes for each service.  Need to examine the consequences of removing this and just going with straight SOS service using OWSLib. 

# <codecell>

collector = CoopsSos()

collector.set_datum('NAVD')  # MSL
collector.server.identification.title
collector.start_time = jd_start
collector.end_time = jd_stop
collector.variables = [sos_name]

# <codecell>

ofrs = collector.server.offerings
print(len(ofrs))
for p in ofrs[700:710]:
    print(p)

# <markdowncell>

# ### Find the SOS stations within our bounding box and time extent
# We would like to just use a filter on a collection to get a new collection, but PYOOS doesn't do that yet. So we do a GetObservation request for a collection, including a bounding box, and asking for one value at the start of the time period of interest.   We use that to do a bounding box filter on the SOS server, which returns 1 point for each station found.  So for 3 stations, we get back 3 records, in CSV format.  We can strip the station ids from the CSV, and then we have a list of stations we can use with pyoos.  The template for the GetObservation query for the bounding box filtered collection was generated using the GUI at http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/

# <codecell>

iso_start = jd_start.strftime('%Y-%m-%dT%H:%M:%SZ')
print(iso_start)
box_str = ','.join(str(e) for e in box)
print(box_str)

# <codecell>

url = ('http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?'
       'service=SOS&request=GetObservation&version=1.0.0&'
       'observedProperty=%s&offering=urn:ioos:network:NOAA.NOS.CO-OPS:'
       'WaterLevelActive&featureOfInterest=BBOX:%s&responseFormat='
       'text/csv&eventTime=%s' % (sos_name, box_str, iso_start))

print(url)
obs_loc_df = read_csv(url)

# <codecell>

obs_loc_df.head()

# <codecell>

stations = [sta.split(':')[-1] for sta in obs_loc_df['station_id']]
obs_lon = [sta for sta in obs_loc_df['longitude (degree)']]
obs_lat = [sta for sta in obs_loc_df['latitude (degree)']]
print(stations)

# <markdowncell>

# Generate a uniform 6-min time base for model/data comparison:

# <codecell>

ts_rng = date_range(start=jd_start, end=jd_stop, freq='6Min')
ts = DataFrame(index=ts_rng)
print(jd_start, jd_stop)
print(len(ts))

# <markdowncell>

# Create a list of obs dataframes, one for each station:

# <codecell>

obs_df = []
sta_names = []
sta_failed = []
for sta in stations:
    b = coops2df(collector, sta, sos_name)
    name = b.name
    sta_names.append(name)
    print(name)
    if b.empty:
        sta_failed.append(name)
        b = DataFrame(np.arange(len(ts)) * np.NaN, index=ts.index, columns=['Observed Data'])
        b.name = name
    # Limit interpolation to 10 points (10 @ 6min = 1 hour).
    col = 'Observed Data'
    concatenated = concat([b, ts], axis=1).interpolate(limit=10)[col]
    obs_df.append(DataFrame(concatenated))
    obs_df[-1].name = b.name

# <codecell>

geodetic = ccrs.Geodetic(globe=ccrs.Globe(datum='WGS84'))
tiler = MapQuestOpenAerial()
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection=tiler.crs))
# Open Source Imagery from MapQuest (max zoom = 16?)
zoom = 8
extent = [box[0], box[2], box[1], box[3]]
ax.set_extent(extent, geodetic)
ax.add_image(tiler, zoom)

ax.scatter(obs_lon, obs_lat, marker='o', s=30,
           color='cyan', transform=ccrs.PlateCarree())
geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
text_transform = offset_copy(geodetic_transform, units='dots', x=-7, y=+7)

for x, y, label in zip(obs_lon, obs_lat, sta_names):
    ax.text(x, y, label, horizontalalignment='left',
            transform=text_transform, color='white')
gl = ax.gridlines(draw_labels=True)
gl.xlabels_top = gl.ylabels_right = False
ax.set_title('Water Level Gauge Locations')

# <markdowncell>

# ### Get model output from OPeNDAP URLS
# Try to open all the OPeNDAP URLS using Iris from the British Met Office.  If 1D, assume dataset is data, if 2D assume dataset is an unstructured grid model, and if 3D, assume it's a structured grid model.

# <markdowncell>

# Construct an Iris contraint to load only cubes that match the std_name_list:

# <codecell>

print('\n'.join(name_list))
name_in_list = lambda cube: cube.standard_name in name_list
constraint = iris.Constraint(cube_func=name_in_list)

# <markdowncell>

# Use only data within 0.04 degrees (about 4 km).

# <codecell>

max_dist = 0.04

# <markdowncell>

# Use only data where the standard deviation of the time series exceeds 0.01 m
# (1 cm) this eliminates flat line model time series that come from land
# points that should have had missing values.

# <codecell>

min_var = 0.01

# <codecell>

for url in dap_urls:
    try:
        a = iris.load_cube(url, constraint)
        # convert to units of meters
        # a.convert_units('m')     # this isn't working for unstructured data
        # take first 20 chars for model name
        mod_name = a.attributes['title'][0:20]
        r = a.shape
        timevar = find_timevar(a)
        lat = a.coord(axis='Y').points
        lon = a.coord(axis='X').points
        jd = timevar.units.num2date(timevar.points)
        start = timevar.units.date2num(jd_start)
        istart = timevar.nearest_neighbour_index(start)
        stop = timevar.units.date2num(jd_stop)
        istop = timevar.nearest_neighbour_index(stop)

        # Only proceed if we have data in the range requested.
        if istart != istop:
            nsta = len(obs_lon)
            if len(r) == 3:
                print('[Structured grid model]:', url)
                d = a[0, :, :].data
                # Find the closest non-land point from a structured grid model.
                if len(lon.shape) == 1:
                    lon, lat = np.meshgrid(lon, lat)
                j, i, dd = find_ij(lon, lat, d, obs_lon, obs_lat)
                for n in range(nsta):
                    # Only use if model cell is within 0.1 degree of requested
                    # location.
                    if dd[n] <= max_dist:
                        arr = a[istart:istop, j[n], i[n]].data
                        if arr.std() >= min_var:
                            c = mod_df(arr, timevar, istart, istop,
                                       mod_name, ts)
                            name = obs_df[n].name
                            obs_df[n] = concat([obs_df[n], c], axis=1)
                            obs_df[n].name = name
            elif len(r) == 2:
                print('[Unstructured grid model]:', url)
                # Find the closest point from an unstructured grid model.
                index, dd = nearxy(lon.flatten(), lat.flatten(),
                                   obs_lon, obs_lat)
                for n in range(nsta):
                    # Only use if model cell is within 0.1 degree of requested
                    # location.
                    if dd[n] <= max_dist:
                        arr = a[istart:istop, index[n]].data
                        if arr.std() >= min_var:
                            c = mod_df(arr, timevar, istart, istop,
                                       mod_name, ts)
                            name = obs_df[n].name
                            obs_df[n] = concat([obs_df[n], c], axis=1)
                            obs_df[n].name = name
            elif len(r) == 1:
                print('[Data]:', url)
    except (ValueError, RuntimeError, CoordinateNotFoundError,
            ConstraintMismatchError) as e:
        warn("\n%s\n" % e)
        pass

# <codecell>

for df in obs_df:
    ax = df.plot(figsize=(14, 6), title=df.name, legend=False)
    plt.setp(ax.lines[0], linewidth=4.0, color='0.7', zorder=1)
    ax.legend()
    ax.set_ylabel('m')

# <markdowncell>

# Plot again, but now remove the mean offset (relative to data) from all plots.

# <codecell>

for df in obs_df:
    amean = df[jd_start:jd_now].mean()
    name = df.name
    df = df - amean + amean.ix[0]
    df.name = name
    ax = df.plot(figsize=(14, 6), title=df.name, legend=False)
    plt.setp(ax.lines[0], linewidth=4.0, color='0.7', zorder=1)
    ax.legend()
    ax.set_ylabel('m')
    print(amean.ix[0] - amean)

