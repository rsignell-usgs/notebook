# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# ># IOOS System Test: [Extreme Events Theme:](https://github.com/ioos/system-test/wiki/Development-of-Test-Themes#theme-2-extreme-events) Inundation

# <markdowncell>

# ### Can we estimate the return period of a wave height by obtaining long term wave height records from observed and modeled datasets?
# ####Methodology:
# 
# * Define temporal and spatial bounds of interest
# * Define standard names of variable of interest to search for in data sets
# * Search for available service endpoints in the NGDC CSW catalog meeting search criteria
# * Extract OPeNDAP data endpoints from model datasets and SOS endpoints from station observation datasets
# * Obtain long term observation data sets from a station within bounding box (10+ years)
# * Define a new temporal range to search for a particular event (Hurricane Sandy)
# * Using DAP (model) endpoints find all available model data sets in the bounding box, for the specified time range, and extract a model grid cell closest to the observation station
# * Show observation stations and model grid points on a map (red marker for model grid points) 
# * Find the maximum wave height during the event.
# * Perform return period analysis on the long time series observation data and see where the modeled data falls
# * Extract the annual maximum wave heights from the nearest WIS hindcast location (Over 20 Years!)
# * Perform return period analysis on the long time series WIS hindcast

# <markdowncell>

# ### import required libraries

# <codecell>

import matplotlib.pyplot as plt
from warnings import warn
from io import BytesIO
import sys
import csv
import json
import time
from scipy.stats import genextreme
import scipy.stats as ss
import numpy as np

from owslib.csw import CatalogueServiceWeb
from owslib import fes
from IPython.display import HTML
import folium #required for leaflet mapping
import random
import netCDF4
from netCDF4 import num2date
import pandas as pd
import datetime as dt
from pyoos.collectors.ndbc.ndbc_sos import NdbcSos
import iris
from collections import OrderedDict
#generated for csw interface
#from date_range_formatter import dateRange  #date formatter (R.Signell)
import requests              #required for the processing of requests
from utilities import (fes_date_filter, get_station_data, find_timevar, find_ij, nearxy, service_urls, mod_df, 
                       get_coordinates, inline_map, get_station_longName, css_styles)
css_styles()

# <markdowncell>

# ### Define temporal and spatial bounds of interest

# <codecell>

bounding_box_type = "box" 

# Bounding Box [lon_min, lat_min, lon_max, lat_max]
area = {'Hawaii': [-160.0, 18.0, -154., 23.0],
        'Gulf of Maine': [-72.0, 41.0, -69.0, 43.0],
        'New York harbor region': [-75., 39., -71., 41.5],
        'Puerto Rico': [-75, 12, -55, 26],
        'East Coast': [-77, 36, -73, 38],
        'North West': [-130, 38, -121, 50],
        'Gulf of Mexico': [-92, 28, -84, 31],
        'Arctic': [-179, 63, -140, 80],
        'North East': [-74, 40, -69, 42],
        'Virginia Beach': [-76, 34, -74, 38]}

bounding_box = area['Virginia Beach']

#temporal range
start_date = dt.datetime(1994,8,1).strftime('%Y-%m-%d %H:00')
end_date = dt.datetime(2014,8,1).strftime('%Y-%m-%d %H:00')

print start_date,'to',end_date

# <markdowncell>

# ### Define standard names of variable of interest to search for in data sets

# <codecell>

# put the names in a dict for ease of access 
data_dict = {}
sos_name = 'waves'
data_dict["waves"] = {"names":['sea_surface_wave_significant_height',
                               'significant_wave_height',
                               'significant_height_of_wave',
                               'sea_surface_wave_significant_height(m)',
                               'sea_surface_wave_significant_height (m)',
                               'water_surface_height'], 
                      "sos_name":["waves"]} 

# <markdowncell>

# ### Search for available service endpoints in the NGDC CSW catalog meeting search criteria

# <codecell>

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw' # NGDC Geoportal
csw = CatalogueServiceWeb(endpoint,timeout=60)

# convert User Input into FES filters
start,stop = fes_date_filter(start_date, end_date)
bbox = fes.BBox(bounding_box)

#use the search name to create search filter
or_filt = fes.Or([fes.PropertyIsLike(propertyname='apiso:AnyText',literal='*%s*' % val,
                    escapeChar='\\',wildCard='*',singleChar='?') for val in data_dict['waves']['names']])

filter_list = [fes.And([ bbox, start, stop, or_filt]) ]
# connect to CSW, explore it's properties
# try request using multiple filters "and" syntax: [[filter1,filter2]]
try:
    csw.getrecords2(constraints=filter_list, maxrecords=1000, esn='full')
except Exception as e:
    print 'ERROR - ' + str(e)
else:
    print str(len(csw.records)) + " csw records found"

# <markdowncell>

# #### Dap URLS

# <codecell>

dap_urls = service_urls(csw.records)

#remove duplicates and sort
dap_urls = sorted(set(dap_urls))
print "Total DAP:",len(dap_urls)
#print the first 10...
print "\n".join(dap_urls[1:10])

# <markdowncell>

# #### SOS URLs

# <codecell>

sos_urls = service_urls(csw.records,service='sos:url')

#remove duplicates and sort
sos_urls = sorted(set(sos_urls))
print "Total SOS:",len(sos_urls)
print "\n".join(sos_urls[1:10])

# <markdowncell>

# #### SOS - Get most recent observations from all stations in bounding box

# <codecell>

start_time = dt.datetime.strptime(start_date,'%Y-%m-%d %H:%M')
end_time = dt.datetime.strptime(end_date,'%Y-%m-%d %H:%M')

iso_start = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
iso_end = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

print "Date: ",iso_start," to ", iso_end
box_str=','.join(str(e) for e in bounding_box)

collector = NdbcSos()
collector.variables = data_dict["waves"]["sos_name"]
collector.server.identification.title  

# Don't specify start and end date in the filter and the most recent observation will be returned
collector.filter(bbox=bounding_box,
                 variables=data_dict["waves"]["sos_name"])

response = collector.raw(responseFormat="text/csv")
obs_loc_df = pd.read_csv(BytesIO(response.encode('utf-8')),
                         parse_dates=True,
                         index_col='date_time')

# <codecell>

obs_loc_df.head()

# <markdowncell>

# #### Parse the data frame for station names

# <codecell>

stations = [sta.split(':')[-1] for sta in obs_loc_df['station_id']]
obs_lon = [sta for sta in obs_loc_df['longitude (degree)']]
obs_lat = [sta for sta in obs_loc_df['latitude (degree)']]

# <markdowncell>

# ## Obtain long term observation data sets from a station within bounding box (10+ years)
# ### For simplicity let's pick a station and get all the data

# <markdowncell>

# <div class="error"><strong>Lack of long time series wave data at NDBC</strong> - NDBC SOS doesn't serve all of the historical data sets. See issue [here] (https://github.com/ioos/system-test/issues/137) </div>

# <codecell>

# Let's pick one station for simplicity - Virginia Beach (44014)

# Time cell execution
tic = time.time()

station = ['44014']
station_id = station[0]

station_lon = obs_loc_df.loc[obs_loc_df['station_id']==('urn:ioos:station:wmo:44014')]['longitude (degree)'].values
station_lat = obs_loc_df.loc[obs_loc_df['station_id']==('urn:ioos:station:wmo:44014')]['latitude (degree)'].values

sos_name = 'waves'
collector = NdbcSos()
collector.start_time = start_time
collector.end_time = end_time
field_of_interest = "sea_surface_wave_significant_height (m)"

# Get all of the data into a list of yearly dataframes
yearly_df = get_station_data(collector, station_id, sos_name, field_of_interest)

toc = time.time()
sos_elapsed = toc-tic

# <codecell>

print 'Execution time through SOS - %0.2f mins' % (sos_elapsed/60)

# <markdowncell>

# <div class="error"><strong>SOS server is REALLY slow and sometimes times out! </strong> Let's just go straight to the DAP endpoint instead. It's faster and has all of the data</div>

# <markdowncell>

# ### Get the data directly from the DAP endpoint

# <markdowncell>

# <div class="info"><strong></strong>Data can be retrieved directly from http://dods.ndbc.noaa.gov/thredds/dodsC/data/stdmet/44014/</div>

# <codecell>

tic = time.time()
years = range(1990,2013)
yearly_df = []
for year in years:
    # Build URL
    url = 'http://dods.ndbc.noaa.gov/thredds/dodsC/data/stdmet/{0}/{1}h{2}.nc'.format(station_id, station_id, year)
    nc = netCDF4.Dataset(url, 'r')
    nc_time = nc.variables['time']
    hs = nc.variables['wave_height']
    hs_data = np.array(nc.variables['wave_height'][:,0,0])
    # Replace fill values with NaN
    hs_data[hs_data==hs._FillValue] = np.nan
    
    dates = num2date(nc_time[:],units=nc_time.units,calendar='gregorian')
    timestamp = np.array(dates)

    data = {}
    data['Wave Height (m)'] = hs_data
    df = pd.DataFrame(data, index=timestamp)
    yearly_df.append(df)

toc = time.time()
dap_elapsed = toc-tic
print 'Execution time through DAP - %0.2f mins' % (dap_elapsed/60)

# <markdowncell>

# ### Get the observed annual maximums into a dictionary

# <codecell>

annual_max_dict = OrderedDict()
for df in yearly_df:
    year = pd.to_datetime(df['Wave Height (m)'].argmax()).date().year
    annual_max_dict[str(year)] = df['Wave Height (m)'].max()

# <markdowncell>

# ## Get WIS Hindcast data

# <markdowncell>

# ### All of the [WIS](http://wis.usace.army.mil/) stations annual maximum data was downloaded and saved to a json file (WIS_extremes.txt)

# <markdowncell>

# The Wave Information Studies (WIS) is a US Army Corps of Engineers (USACE)   sponsored project that generates consistent, hourly, long-term (20+ years) wave climatologies along all US coastlines, including the Great Lakes and US island territories.  The WIS program originated in the Great Lakes in the mid 1970’s and migrated to the Atlantic, Gulf of Mexico and Pacific Oceans. 

# <markdowncell>

# #### Get the closest WIS station and extract all of the annual max wave height data as another source of long term wave heights to compare

# <codecell>

with open("./WIS_stations.txt") as json_file:
    location_data = json.load(json_file)
    
wis_lats = []
wis_lons = []
wis_stations = []
for station in location_data:
    wis_lats.append(location_data[station]['lat'])
    wis_lons.append(location_data[station]['lon'])
    wis_stations.append(station)
    
# Get index of closest WIS station to obs station
ind, dd = nearxy(wis_lons, wis_lats, station_lon, station_lat)

# Now get read the wis data
with open("./WIS_extremes.txt") as extremes_file:
    wis_extremes = json.load(extremes_file)

# Get the extremes from the closest station
wis_station_id = wis_stations[ind]
wis_lat = wis_lats[ind]
wis_lon = wis_lons[ind]

wis_maximums = []
for year in wis_extremes[wis_station_id].keys():
    wis_maximums.append(wis_extremes[wis_station_id][year]['height_max'])

# <markdowncell>

# ## Extreme Value Analysis: Perform on both the observed and WIS hindcast data

# <codecell>

annual_max = list(annual_max_dict.values()) 

# <markdowncell>

# ### Fit observation data to GEV distribution

# <codecell>

def gev_pdf(x):
    return genextreme.pdf(x, xi, loc=mu, scale=sigma)

# <codecell>

mle = genextreme.fit(sorted(annual_max), 0)
mu = mle[1]
sigma = mle[2]
xi = mle[0]
print "The mean, sigma, and shape parameters are %s, %s, and %s, resp." % (mu, sigma, xi)

# <markdowncell>

# ### Probability Density Plot

# <codecell>

min_x = min(annual_max)-0.5
max_x = max(annual_max)+0.5
x = np.linspace(min_x, max_x, num=100)
y = [gev_pdf(z) for z in x]

fig = plt.figure(figsize=(12,6))
axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
station_longName = get_station_longName(station_id)
xlabel = (station_longName + " - Annual max Wave Height (m)")
axes.set_title("Probability Density & Normalized Histogram")
axes.set_xlabel(xlabel)
axes.plot(x, y, color='Red')
axes.hist(annual_max, bins=arange(min_x, max_x, abs((max_x-min_x)/10)), normed=1, color='Yellow')

# <markdowncell>

# ### Fit WIS data to GEV distribution

# <codecell>

mle_wis = genextreme.fit(sorted(wis_maximums), 0)
mu_wis = mle_wis[1]
sigma_wis = mle_wis[2]
xi_wis = mle_wis[0]
print "The mean, sigma, and shape parameters are %s, %s, and %s, resp." % (mu_wis, sigma_wis, xi_wis)

# <markdowncell>

# ### Return Value Plot

# <codecell>

fig, axes = plt.subplots(2, 1, figsize=(20,12))
# fig = plt.figure()
# axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
T=np.r_[1:500]
sT = genextreme.isf(1./T, 0, mu, sigma)
axes[0].semilogx(T, sT, 'r'), hold
N=np.r_[1:len(annual_max)+1]; 
Nmax=max(N);
axes[0].plot(Nmax/N, sorted(annual_max)[::-1], 'bo')
title = station_longName
axes[0].set_title(title)
axes[0].set_xlabel('Return Period (yrs)')
axes[0].set_ylabel('Significant Wave Height (m)') 
axes[0].grid(True)

sT_wis = genextreme.isf(1./T, 0, mu_wis, sigma_wis)
axes[1].semilogx(T, sT_wis, 'r'), hold
N=np.r_[1:len(wis_maximums)+1]; 
Nmax=max(N);
axes[1].plot(Nmax/N, sorted(wis_maximums)[::-1], 'bo')
title = 'WIS ' + wis_station_id
axes[1].set_title(title)
axes[1].set_xlabel('Return Period (yrs)')
axes[1].set_ylabel('Significant Wave Height (m)') 
axes[1].grid(True)

ymax = max(list(sT_wis)+list(sT))
axes[0].set_ylim([0, ymax+0.5])
axes[1].set_ylim([0, ymax+0.5])
# Now plot the max height from the event onto this plot
# event = np.ones(len(T))*model_max
# axes.plot(T, event, 'g--')

# <markdowncell>

# ## Get some modeled wave data for an event to estimate it's characteristic return period

# <markdowncell>

# ### Define a new temporal range to search for a particular event (Hurricane Sandy) and get available DAP endpoints

# <codecell>

#temporal range (Hurricane Sandy Oct 25 2014 - Nov 2 2014)
start_date = dt.datetime(2012,10,25).strftime('%Y-%m-%d %H:00')
end_date = dt.datetime(2012,11,2).strftime('%Y-%m-%d %H:00')

jd_start = dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
jd_stop = dt.datetime.strptime(end_date, '%Y-%m-%d %H:%M')

# convert User Input into FES filters
start, stop = fes_date_filter(start_date, end_date)

filter_list = [fes.And([ bbox, start, stop, or_filt])]
# connect to CSW, explore it's properties
# try request using multiple filters "and" syntax: [[filter1,filter2]]
try:
    csw.getrecords2(constraints=filter_list, maxrecords=1000, esn='full')
except Exception as e:
    print 'ERROR - ' + str(e)
    
dap_urls = service_urls(csw.records)

#remove duplicates and sort
dap_urls = sorted(set(dap_urls))
print "Total DAP:",len(dap_urls)
#print the first 5...
print "\n".join(dap_urls[10:15])

# <codecell>

name_in_list = lambda cube: cube.standard_name in data_dict['waves']['names']
constraint = iris.Constraint(cube_func=name_in_list)

# <codecell>

# Create time index for model DataFrame
ts_rng = pd.date_range(start=jd_start, end=jd_stop, freq='H')
ts = pd.DataFrame(index=ts_rng)

# Create list of model DataFrames for each station
model_df = pd.DataFrame(index=ts.index)

model_lat = []
model_lon = []

# Use only data within 0.4 degrees.
max_dist = 0.4

# Use only data where the standard deviation of the time series exceeds 0.01 m (1 cm).
# This eliminates flat line model time series that come from land points that should have had missing values.
min_var = 0.01

#Try the WaveWatchIII global model
url = 'http://oos.soest.hawaii.edu/thredds/dodsC/hioos/model/wav/ww3/WaveWatch_III_Global_Wave_Model_best.ncd'
try:
    print 'Attemping to load {0}'.format(url)
    cube = iris.load_cube(url, constraint)

    # take first 20 chars for model name
    mod_name = cube.attributes['title'][0:30]
    r = cube.shape
    timevar = find_timevar(cube)
    lat = cube.coord(axis='Y').points
    lon = cube.coord(axis='X').points
    # Convert longitude to [-180 180]
    if max(lon) > 180:
        lon[lon>180] = lon[lon>180]-360
    jd = timevar.units.num2date(timevar.points)
    start = timevar.units.date2num(jd_start)
    istart = timevar.nearest_neighbour_index(start)
    stop = timevar.units.date2num(jd_stop)
    istop = timevar.nearest_neighbour_index(stop)

    # Only proceed if we have data in the range requested.
    if istart != istop:
        # Wave Watch III uses a 4D grid (time, z, lat, lon)
        d = cube[0, 0, :, :].data
        if len(lon.shape) == 1:
            new_lon, new_lat = np.meshgrid(lon, lat)
        else:
            new_lon, new_lat = lon, lat

        # Find the closest non-land point from a structured grid model.
        j, i, dd = find_ij(new_lon, new_lat, d, station_lon, station_lat)

        # Keep the lat lon of the grid point
        model_lat = lat[j].tolist()
        model_lon = lon[i].tolist()

        # Only use if model cell is within max_dist of station
        if dd <= max_dist:
            arr = cube[istart:istop, 0, j, i].data
            if arr.std() >= min_var:
                c = mod_df(arr, timevar, istart, istop,
                           mod_name, ts)
                model_df = pd.concat([model_df, c], axis=1)
                model_df.name = get_station_longName(str(station_id))
            else:
                print 'Min variance error'
        else:
            print 'Max dist error'
    else:
        print 'No data in range'
except Exception as e:
    warn("\n%s\n" % e)
    pass
        
        

# <markdowncell>

# ### Plot the model data for the event

# <codecell>

model_df.plot(figsize=(14, 6), title=model_df.name, legend=False)
model_max = list(set(model_df.max().values))
print 'Max Value is {0}'.format(model_max)

# <markdowncell>

# ### Plot the Observation Stations and Model Points on Map

# <codecell>

# Find center of bounding box
lat_center = abs(bounding_box[3]-bounding_box[1])/2 + bounding_box[1]
lon_center = abs(bounding_box[0]-bounding_box[2])/2 + bounding_box[0]
m = folium.Map(location=[lat_center, lon_center], zoom_start=8)

# Now loop through stations and plot markers
for n in range(len(stations)):
    # Get the station name
    name = stations[n]
    longname = get_station_longName(str(name))

    # Get obs station lat/lon
    olat = obs_lat[n]
    olon = obs_lon[n]
    popup_string = ('<b>Station:</b><br>'+ longname)
    
    # Create obs station marker|
    if olat != station_lat:
        m.simple_marker([olat, olon], popup=popup_string, marker_color = 'red')
    else:
        m.simple_marker([olat, olon], popup=popup_string)

# Add the model data point
if model_lat:
    # Get model grid points lat/lon
    mlat = model_lat
    mlon = model_lon
    # Plot a line from obs station to corresponding model grid point
    data_1=[station_lat, station_lon]
    data_2=[model_lat, model_lon]
    m.line([data_1,data_2],line_color='#00FF00', line_weight=5)

    # Create model grid point marker
    popup_string = ('<b>WW3 Model Grid Point</b>')
    m.simple_marker([mlat, mlon], popup=popup_string, marker_color='purple')
    
    # Add WIS station
    popup_string = ('<b>WIS station</b>')
    m.simple_marker([wis_lat, wis_lon], popup=popup_string, marker_color='green')

m.line(get_coordinates(bounding_box, bounding_box_type), line_color='#ff0000', line_weight=5)

inline_map(m)

# <markdowncell>

# ### Return value plot with event max overlayed as dashed line

# <codecell>

fig, axes = plt.subplots(2, 1, figsize=(20,12))
# fig = plt.figure()
# axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
T=np.r_[1:500]
sT = genextreme.isf(1./T, 0, mu, sigma)
axes[0].semilogx(T, sT, 'r'), hold
N=np.r_[1:len(annual_max)+1]; 
Nmax=max(N);
axes[0].plot(Nmax/N, sorted(annual_max)[::-1], 'bo')
title = station_longName
axes[0].set_title(title)
axes[0].set_xlabel('Return Period (yrs)')
axes[0].set_ylabel('Significant Wave Height (m)') 
axes[0].grid(True)
# Now plot the max height from the event onto this plot
event = np.ones(len(T))*model_max
axes[0].plot(T, event, 'g--')

sT_wis = genextreme.isf(1./T, 0, mu_wis, sigma_wis)
axes[1].semilogx(T, sT_wis, 'r'), hold
N=np.r_[1:len(wis_maximums)+1]; 
Nmax=max(N);
axes[1].plot(Nmax/N, sorted(wis_maximums)[::-1], 'bo')
title = 'WIS ' + wis_station_id
axes[1].set_title(title)
axes[1].set_xlabel('Return Period (yrs)')
axes[1].set_ylabel('Significant Wave Height (m)') 
axes[1].grid(True)

ymax = max(list(sT_wis)+list(sT))
axes[0].set_ylim([0, ymax+0.5])
axes[1].set_ylim([0, ymax+0.5])

# Now plot the max height from the event onto this plot
axes[1].plot(T, event, 'g--')

