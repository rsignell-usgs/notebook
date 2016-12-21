# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# ># IOOS System Test: [Extreme Events Theme:](https://github.com/ioos/system-test/wiki/Development-of-Test-Themes#theme-2-extreme-events) Inundation

# <markdowncell>

# ### Can we estimate the return period of a water level by comparing modeled and/or observed water levels with NOAA Annual Exceedance Probability Curves?

# <markdowncell>

# Methodology:
# 
# * Define temporal and spatial bounds of interest, as well as parameters of interest
# * Search for available service endpoints in the NGDC CSW catalog, then inform the user of the DAP (model) and SOS (observation) services endpoints available
# * Obtain the stations in the spatial boundaries, and processed to obtain observation data for temporal constraints, identifying the yearly max
# * Plot observation stations on a map and indicate to the user if the minimum number of years has been met for extreme value analysis (red marker if condition is false)
# * Using DAP (model) endpoints find all available models data sets that fall in the area of interest, for the specified time range, and extract a model grid cell closest all the given station locations
# * Plot the annual max for each station as a timeseries plot
# * Plot the annual exceedance probability curve for the Nantucket Island, Ma station and compare to NOAA Tides and Currents plot
# * The annual exceedance probability curve can be used to estimate the return period of a particular water level, whether it be modeled or observed data.

# <headingcell level=4>

# import required libraries

# <codecell>

from datetime import datetime, timedelta
import requests
from warnings import warn

import folium
from IPython.display import Image
import iris
from iris.exceptions import CoordinateNotFoundError, ConstraintMismatchError
import matplotlib.pyplot as plt
import numpy as np
from owslib import fes
# from shapely.geometry import Point  # For lat lon points.
from owslib.csw import CatalogueServiceWeb
import pandas as pd
import prettyplotlib as ppl
from pyoos.collectors.coops.coops_sos import CoopsSos
import scipy.stats as stats

from utilities import (get_Coops_longName, fes_date_filter, get_coordinates, service_urls, inline_map, coops2data, find_timevar, 
                        find_ij, nearxy, mod_df)
 

# <headingcell level=4>

# Specify Temporal and Spatial conditions.

# <codecell>

# Bounding box of interest,[bottom right[lat,lon], top left[lat,lon]].
bounding_box_type = "box"
# Build a bounding box around Long Island Sound
bounding_box = [[-75.94, 39.67],
                [-66.94, 41.5]]

# Temporal range. Get 30+ yrs obs data for extremal analysis and recent modeled data to compare
start_date = datetime(1980, 5, 1).strftime('%Y-%m-%d %H:00')
end_date = datetime(2014, 5, 1).strftime('%Y-%m-%d %H:00')
time_date_range = [start_date, end_date]

jd_now = datetime.utcnow()
jd_start,  jd_stop = jd_now - timedelta(days=3), jd_now + timedelta(days=3)

jd_start = datetime.strptime(jd_start.strftime('%Y-%m-%d %H:00'), '%Y-%m-%d %H:%M')
jd_stop = datetime.strptime(jd_stop.strftime('%Y-%m-%d %H:00'), '%Y-%m-%d %H:%M')

print('%s to %s' % (start_date, end_date))

# <markdowncell>

# #### Specify a list of standard names to search for

# <codecell>

name_list = ['water level',
             'sea_surface_height',
             'sea_surface_elevation',
             'sea_surface_height_above_geoid',
             'sea_surface_height_above_sea_level',
             'water_surface_height_above_reference_datum',
             'sea_surface_height_above_reference_ellipsoid',
             'sea_surface_height_above_reference_level']

sos_name = 'water_surface_height_above_reference_datum'

# <markdowncell>

# #### Define the CSW geoportal endpoint 

# <codecell>

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw'  # NGDC Geoportal.
csw = CatalogueServiceWeb(endpoint, timeout=60)

for oper in csw.operations:
    if oper.name == 'GetRecords':
        print('\nISO Queryables:\n%s' %
              '\n'.join(oper.constraints['SupportedISOQueryables']['values']))

# Put the names in a dict for ease of access.
data_dict = {}
data_dict["water"] = {"names": name_list,
                      "sos_name": sos_name}

# <markdowncell>

# #### Convert User Input into FES filters.

# <codecell>

start, stop = fes_date_filter(start_date, end_date)
box = []
box.append(bounding_box[0][0])
box.append(bounding_box[0][1])
box.append(bounding_box[1][0])
box.append(bounding_box[1][1])
bbox = fes.BBox(box)

or_filt = fes.Or([fes.PropertyIsLike(propertyname='apiso:AnyText',
                                     literal=('*%s*' % val),
                                     escapeChar='\\',
                                     wildCard='*',
                                     singleChar='?') for val in name_list])
val = 'Averages'
not_filt = fes.Not([fes.PropertyIsLike(propertyname='apiso:AnyText',
                                       literal=('*%s*' % val),
                                       escapeChar='\\',
                                       wildCard='*',
                                       singleChar='?')])

# <codecell>

filter_list = [fes.And([bbox, start, stop, or_filt, not_filt])]
# connect to CSW, explore it's properties
# try request using multiple filters "and" syntax: [[filter1,filter2]]
csw.getrecords2(constraints=filter_list,
                maxrecords=1000,
                esn='full')

# <codecell>

# Print records that are available:
print("number of datasets available: %s" % len(csw.records.keys()))

# <markdowncell>

# Print all the records (should you want too).

# <codecell>

# print("\n".join(csw.records))

# <markdowncell>

# #### DAP URLs:

# <codecell>

dap_urls = service_urls(csw.records, service='odp:url')

# Remove duplicates and organize.
dap_urls = sorted(set(dap_urls))
print("Total DAP: %s" % len(dap_urls))

# print the dap urls...
print("\n".join(dap_urls))

# <markdowncell>

# #### SOS URLs:

# <codecell>

sos_urls = service_urls(csw.records, service='sos:url')

# Remove duplicates and organize.
sos_urls = sorted(set(sos_urls))
print("Total SOS: %s" % len(sos_urls))
print("\n".join(sos_urls))

# <markdowncell>

# ### SOS Requirements
# #### Use Pyoos SOS collector to obtain Observation data from COOPS.

# <codecell>

start_time = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
end_time = datetime.strptime(end_date, '%Y-%m-%d %H:%M')

# <codecell>

iso_start = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
iso_end = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

collector = CoopsSos()
collector.set_datum('NAVD')
collector.server.identification.title
collector.start_time = start_time
collector.end_time = end_time
collector.variables = [data_dict["water"]["sos_name"]]

# <codecell>

print("Date: %s to %s" % (iso_start, iso_end))
box_str = ','.join(str(e) for e in box)
print("Lat/Lon Box: %s" % box_str)

# <codecell>

# Grab the sos url and use it for the service.
url = (sos_urls[0].split("?")[0] + '?'
       'service=SOS&request=GetObservation&version=1.0.0&'
       'observedProperty=%s&'
       'offering=urn:ioos:network:NOAA.NOS.CO-OPS:WaterLevelActive&'
       'featureOfInterest=BBOX:%s&responseFormat=text/tab-separated-values&'
       'eventTime=%s') % (sos_name, box_str, iso_end)

r = requests.get(url)
data = r.text
# Get the headers for the col.
data = data.split("\n")
headers = data[0]
station_list_dict = dict()
# Parse the headers so I can create a dict.
c = 0
for h in headers.split("\t"):
    field = h.split(":")[0].split(" ")[0]
    station_list_dict[field] = {"id": c}
    c += 1

# <codecell>

# Create dict of stations.
station_list = []
for i in range(1, len(data)):
    station_info = data[i].split("\t")
    station = dict()
    for field in station_list_dict.keys():
        col = station_list_dict[field]["id"]
        if col < len(station_info):
            station[field] = station_info[col]
    station["type"] = "obs"
    if "latitude" not in station:
        continue
    station_list.append(station)

# <markdowncell>

# #### Go through stations and parse data

# <codecell>

station_yearly_max = []
for s in station_list:
    if s["type"] is "obs" and s['station_id']:  # If its an obs station.
        # Get the long name.
        sta = s['station_id'].split(':')[-1]
        s["long_name"] = get_Coops_longName(sta)
        s["station_num"] = str(s['station_id']).split(':')[-1]
        # This is different than sos name, hourly height is hourly water level.
        s["data"] = coops2data(collector, s["station_num"], "high_low")

# <codecell>

# Store data in a pandas DataFrame
col = 'water_surface_height_above_reference_datum (m)'

obs_df = []
for s in station_list:
    years = s["data"].keys()
    xx = []
    yx = []
    for y in years:
        xx.append(int(y))
        val = s["data"][y]["max"]
        yx.append(val)
    col = 'Observed Data'
    df = pd.DataFrame(np.array(yx),columns=[col],index=years)
    df.name = s["long_name"]
    obs_df.append(df)
    obs_df[-1].name = df.name

# <markdowncell>

# ### Plot stations on an interactive map

# <codecell>

def add_invalid_marker(m, s, popup_string):
    m.circle_marker(location=[s["latitude"], s["longitude"]],
                    popup=popup_string, fill_color='#ff0000',
                    radius=10000, line_color='#ff0000')

# <codecell>

# Number of years required for analysis
num_years_required = 30

#find center of bounding box
lat_center = abs(bounding_box[1][1] - bounding_box[0][1])/2 + bounding_box[0][1]
lon_center = abs(bounding_box[0][0]-bounding_box[1][0])/2 + bounding_box[0][0]
m = folium.Map(location=[lat_center, lon_center], zoom_start=6)

for s in station_list:
    if "latitude" in s:
        if len(s["data"].keys()) >= num_years_required:
            popup_string = ('<b>Station:</b><br>' + str(s['station_id']) +
                            "<br><b>Long Name:</b><br>" +
                            str(s["long_name"]))
            m.simple_marker(location=[s["latitude"], s["longitude"]],
                            popup=popup_string)
        else:
            popup_string = ('<b>Not Enough Station Data for Num of years'
                            'requested</b><br><br>Num requested:' +
                            str(num_years_required) +
                            '<br>Num Available:' +
                            str(len(s["data"].keys())) +
                            '<br><b>Station:</b><br>' +
                            str(s['station_id']) +
                            "<br><b>Long Name:</b><br>" +
                            str(s["long_name"]))
            add_invalid_marker(m, s, popup_string)

m.line(get_coordinates(bounding_box,bounding_box_type), line_color='#FF0000', line_weight=5)

inline_map(m)

# <markdowncell>

# ### Creates a time series plot with stations that have enough data

# <codecell>

# Set the random seed for consistency
np.random.seed(12)

fig, ax = plt.subplots()

# Show the whole color range
for s in station_list:
    if "data" in s:
        years = s["data"].keys()
        # Only show the stations with enough data.
        if len(s["data"].keys()) >= num_years_required:
            xx = []
            yx = []
            for y in years:
                xx.append(int(y))
                val = s["data"][y]["max"]
                yx.append(val)

            ax.scatter(xx, yx, marker='o')
            ppl.scatter(ax, xx, yx, alpha=0.8, edgecolor='black',
                        linewidth=0.15, label=str(s["station_num"]))
            ppl.legend(ax, loc='right', ncol=1)
            ax.set_xlabel('Year')
            ax.set_ylabel('water level (m)')

ax.set_title("Stations exceeding " +
             str(num_years_required) +
             " years worth of water level data (MHHW)")
fig.set_size_inches(14, 8)

# <markdowncell>

# ### Number of stations available by number of years

# <codecell>

fig, ax = plt.subplots(1)
year_list_map = []
for s in station_list:
    if "data" in s:
        years = s["data"].keys()
        year_list_map.append(len(years))

ppl.hist(ax, np.array(year_list_map), grid='y')
plt.plot([num_years_required, num_years_required], [0, 8], 'r-', lw=2)
ax.set_ylabel("Number of Stations")
ax.set_xlabel("Number of Years Available")
ax.set_title('Number of available stations vs available years\n'
             '(for bounding box) - red is minimum requested years')

# <markdowncell>

# ## Get model output from OPeNDAP URLS
# ### Try to open all the OPeNDAP URLS using Iris from the British Met Office. If we can open in Iris, we know it's a model result.
# 
# #### Construct an Iris contraint to load only cubes that match the standard names:

# <codecell>

print data_dict['water']['names']
name_in_list = lambda cube: cube.standard_name in data_dict['water']['names']
constraint = iris.Constraint(cube_func=name_in_list)

# station_list[0]

# <codecell>

# Create time index for model DataFrame
ts_rng = pd.date_range(start=jd_start, end=jd_stop, freq='6Min')
ts = pd.DataFrame(index=ts_rng)

#Get the station lat/lon into lists and create list of model DataFrames for each station
obs_lon = []
obs_lat = []
model_df = []
for sta in station_list:
    obs_lon.append(float(sta['longitude']))
    obs_lat.append(float(sta['latitude']))
    model_df.append(pd.DataFrame(index=ts.index))
    model_df[-1].name = sta['long_name']

# Use only data within 0.04 degrees (about 4 km).
max_dist = 0.04
# Use only data where the standard deviation of the time series exceeds 0.01 m (1 cm).
# This eliminates flat line model time series that come from land points that should have had missing values.
min_var = 0.01
for url in dap_urls:
    try:
        print 'Attemping to load {0}'.format(url)
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
            nsta = len(station_list)
            if len(r) == 3:
                print('[Structured grid model]:', url)
                d = a[0, :, :].data
                # Find the closest non-land point from a structured grid model.
                if len(lon.shape) == 1:
                    lon, lat = np.meshgrid(lon, lat)
                j, i, dd = find_ij(lon, lat, d, obs_lon, obs_lat)
                for n in range(nsta):
                    # Only use if model cell is within 0.01 degree of requested
                    # location.
                    if dd[n] <= max_dist:
                        arr = a[istart:istop, j[n], i[n]].data
                        if arr.std() >= min_var:
                            c = mod_df(arr, timevar, istart, istop,
                                       mod_name, ts)
                            name = station_list[n]['long_name']
                            model_df[n] = pd.concat([model_df[n], c], axis=1)
                            model_df[n].name = name
                            
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
                            name = station_list[n]['long_name']
                            model_df[n] = pd.concat([model_df[n], c], axis=1)
                            model_df[n].name = name
            elif len(r) == 1:
                print('[Data]:', url)
    except (ValueError, RuntimeError, CoordinateNotFoundError,
            ConstraintMismatchError) as e:
        warn("\n%s\n" % e)
        pass

# <markdowncell>

# ### Plot all the model Time Series data near each obs station

# <codecell>

for df in model_df:
    if not df.empty:
        ax = df.plot(figsize=(14, 6), title=df.name, legend=False)
        plt.setp(ax.lines[0], linewidth=4.0, color='0.7', zorder=1)
        ax.legend()
        ax.set_ylabel('m')

# <markdowncell>

# ## Extreme Value Analysis:
# #### Plot return periods for the observed data at the Nantucket Island, Ma station

# <codecell>

# Get the annual maximums from the DataFrame
for df in obs_df:
    if 'Nantucket Island, MA' in df.name:
        annual_max_levels = df["Observed Data"].values
        name = df.name

# <headingcell level=4>

# Fit data to GEV distribution

# <codecell>

def sea_levels_gev_pdf(x):
    return stats.genextreme.pdf(x, xi, loc=mu, scale=sigma)

# <codecell>

mle = stats.genextreme.fit(sorted(annual_max_levels), 0)
mu = mle[1]
sigma = mle[2]
xi = mle[0]
print("The mean, sigma, and shape parameters are %s, %s, and %s, resp." %
      (mu, sigma, xi))

# <headingcell level=4>

# Probability Density Plot

# <codecell>

min_x = min(annual_max_levels) - 0.5
max_x = max(annual_max_levels) + 0.5
x = np.linspace(min_x, max_x, num=100)
y = [sea_levels_gev_pdf(z) for z in x]

fig = plt.figure(figsize=(12, 6))
axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
xlabel = (name + " - Annual max water level (m)")
axes.set_title("Probability Density & Normalized Histogram")
axes.set_xlabel(xlabel)
axes.plot(x, y, color='Red')
axes.hist(annual_max_levels,
          bins=np.arange(min_x, max_x, abs((max_x-min_x)/10)),
          normed=1, color='Yellow')

# <headingcell level=4>

# Return Value Plot

# <markdowncell>

# This plot should match NOAA's [Annual Exceedance Probability Curves for station 8449130](http://tidesandcurrents.noaa.gov/est/curves.shtml?stnid=8449130).

# <codecell>

noaa_station_id = 8449130
Image(url='http://tidesandcurrents.noaa.gov/est/curves/high/' +
      str(noaa_station_id)+'.png')

# <codecell>

Image(url='http://tidesandcurrents.noaa.gov/est/images/color_legend.png')

# <markdowncell>

# <script type="text/javascript">
#     $('div.input').show();       
# </script>

# <codecell>

fig = plt.figure(figsize=(20, 6))
axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
T = np.r_[1:250]
sT = stats.genextreme.isf(1./T, 0, mu, sigma)
axes.semilogx(T, sT, 'r')
N = np.r_[1:len(annual_max_levels)+1]
Nmax = max(N)
axes.plot(Nmax/N, sorted(annual_max_levels)[::-1], 'bo')
title = name
axes.set_title(title)
axes.set_xlabel('Return Period (yrs)')
axes.set_ylabel('Meters above MHHW')
axes.set_xticklabels([0, 1, 10, 100, 1000])
axes.set_xlim([0, 260])
axes.set_ylim([0, 1.8])
axes.grid(True)

# <markdowncell>

# This plot does not match exactly.  NOAA's curves were calculated using the
# Extremes Toolkit software package in R whereas this notebook uses scipy.
# There is a python package based on the Extremes Toolkit called pywafo but
# this is experimental and isn't building properly on Mac OS X.

