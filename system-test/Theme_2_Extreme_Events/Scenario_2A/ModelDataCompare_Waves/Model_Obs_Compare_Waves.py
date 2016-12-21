# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# ># IOOS System Test: [Extreme Events Theme:](https://github.com/ioos/system-test/wiki/Development-of-Test-Themes#theme-2-extreme-events) Coastal Inundation

# <markdowncell>

# ### Can we compare observed and modeled wave parameters? 
# This notebook is based on [IOOS System Test: Inundation](http://nbviewer.ipython.org/github/ioos/system-test/blob/master/Theme_2_Extreme_Events/Scenario_2A_Coastal_Inundation/Scenario_2A_Water_Level_Signell.ipynb)
# 
# Methodology:
# * Define temporal and spatial bounds of interest, as well as parameters of interest
# * Search for available service endpoints in the NGDC CSW catalog meeting search criteria
# * Extract OPeNDAP data endpoints from model datasets and SOS endpoints from observational datasets
# * Obtain observation data sets from stations within the spatial boundaries
# * Plot observation stations on a map (red marker if not enough data)
# * Using DAP (model) endpoints find all available models data sets that fall in the area of interest, for the specified time range, and extract a model grid cell closest to all the given station locations
# * Plot modelled and observed time series wave data on same axes for comparison
# 

# <headingcell level=4>

# import required libraries

# <codecell>

import datetime as dt
from warnings import warn
from io import BytesIO
import folium
import netCDF4
from IPython.display import HTML
import iris
from iris.exceptions import CoordinateNotFoundError, ConstraintMismatchError
import matplotlib.pyplot as plt
from owslib.csw import CatalogueServiceWeb
from owslib import fes
import pandas as pd
from pyoos.collectors.ndbc.ndbc_sos import NdbcSos
import requests

from utilities import (fes_date_filter, collector2df, find_timevar, find_ij, nearxy, service_urls, mod_df, 
                       get_coordinates, get_station_longName, inline_map)

# <headingcell level=4>

# Speficy Temporal and Spatial conditions

# <codecell>

bounding_box_type = "box" 

# Bounding Box [lon_min, lat_min, lon_max, lat_max]
area = {'Hawaii': [-160.0, 18.0, -154., 23.0],
        'Gulf of Maine': [-72.0, 41.0, -69.0, 43.0],
        'New York harbor region': [-75., 39., -71., 41.5],
        'Puerto Rico': [-75, 12, -55, 26],
        'East Coast': [-77, 34, -70, 40],
        'North West': [-130, 38, -121, 50],
        'Gulf of Mexico': [-92, 28, -84, 31],
        'Arctic': [-179, 63, -140, 80],
        'North East': [-74, 40, -69, 42],
        'Virginia Beach': [-76, 34, -74, 38]}

bounding_box = area['East Coast']

#temporal range - May 1 2014 - May 10 2014
start_date = dt.datetime(2014,5,1,0,50).strftime('%Y-%m-%d %H:%M')
end_date = dt.datetime(2014,5,10).strftime('%Y-%m-%d %H:00')
time_date_range = [start_date,end_date]  #start_date_end_date

jd_start = dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
jd_stop = dt.datetime.strptime(end_date, '%Y-%m-%d %H:%M')

print start_date,'to',end_date

# <headingcell level=4>

# Specify data names of interest

# <codecell>

#put the names in a dict for ease of access 
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

# <headingcell level=3>

# Search CSW for datasets of interest

# <codecell>

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw' # NGDC Geoportal
csw = CatalogueServiceWeb(endpoint,timeout=60)

# <codecell>

# convert User Input into FES filters
start,stop = fes_date_filter(start_date,end_date)
bbox = fes.BBox(bounding_box)

#use the search name to create search filter
or_filt = fes.Or([fes.PropertyIsLike(propertyname='apiso:AnyText',literal='*%s*' % val,
                    escapeChar='\\',wildCard='*',singleChar='?') for val in data_dict["waves"]["names"]])

# try request using multiple filters "and" syntax: [[filter1,filter2]]
filter_list = [fes.And([ bbox, start, stop, or_filt]) ]

csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
print str(len(csw.records)) + " csw records found"

# <markdowncell>

# #### Dap URLs

# <codecell>

dap_urls = service_urls(csw.records)
#remove duplicates and organize
dap_urls = sorted(set(dap_urls))
print "Total DAP:",len(dap_urls)
#print the first 5...
print "\n".join(dap_urls[0:5])

# <markdowncell>

# #### SOS URLs

# <codecell>

sos_urls = service_urls(csw.records,service='sos:url')
#remove duplicates and organize
sos_urls = sorted(set(sos_urls))

print "Total SOS:",len(sos_urls)
print "\n".join(sos_urls)

# <markdowncell>

# ###Get most recent observations from all stations in bounding box

# <codecell>

start_time = dt.datetime.strptime(start_date,'%Y-%m-%d %H:%M')
end_time = dt.datetime.strptime(end_date,'%Y-%m-%d %H:%M')
iso_start = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
iso_end = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

# Define the SOS collector
collector = NdbcSos()
print collector.server.identification.title
collector.variables = data_dict["waves"]["sos_name"]
collector.server.identification.title

# Don't specify start and end date in the filter and the most recent observation will be returned
collector.filter(bbox=bounding_box,
                 variables=data_dict["waves"]["sos_name"])

response = collector.raw(responseFormat="text/csv")
obs_loc_df = pd.read_csv(BytesIO(response.encode('utf-8')),
                         parse_dates=True,
                         index_col='date_time')

# Now let's specify start and end times
collector.start_time = start_time
collector.end_time = end_time

ofrs = collector.server.offerings

# <codecell>

obs_loc_df.head()

# <codecell>

stations = [sta.split(':')[-1] for sta in obs_loc_df['station_id']]
obs_lon = [sta for sta in obs_loc_df['longitude (degree)']]
obs_lat = [sta for sta in obs_loc_df['latitude (degree)']]

# <headingcell level=3>

# Request CSV response from SOS and convert to Pandas DataFrames

# <codecell>

ts_rng = pd.date_range(start=start_date, end=end_date)
ts = pd.DataFrame(index=ts_rng)

# Save all of the observation data into a list of dataframes
obs_df = []
# Create a list of dataframes for just wave heights for comparing with modeled wave heights later
Hs_obs_df = []

for sta in stations:
    raw_df = collector2df(collector, sta, sos_name)
    obs_df.append(pd.DataFrame(pd.concat([raw_df, ts],axis=1)))
    obs_df[-1].name = raw_df.name
    if raw_df.empty:
        Hs_obs_df.append(pd.DataFrame())
    else:
        Hs_obs_df.append(pd.DataFrame(pd.concat([raw_df, ts],axis=1)['sea_surface_wave_significant_height (m)']))

    Hs_obs_df[-1].name = raw_df.name
    

# <markdowncell>

# ### Plot the Observation Stations on Map

# <codecell>

min_data_pts = 20

# Find center of bounding box
lat_center = abs(bounding_box[3]-bounding_box[1])/2 + bounding_box[1]
lon_center = abs(bounding_box[0]-bounding_box[2])/2 + bounding_box[0]
m = folium.Map(location=[lat_center, lon_center], zoom_start=6)

n = 0
for df in obs_df:
    #get the station data from the sos end point
    longname = df.name
    lat = obs_loc_df['latitude (degree)'][n]
    lon = obs_loc_df['longitude (degree)'][n]
    popup_string = ('<b>Station:</b><br>'+ longname)
    if len(df) > min_data_pts:
        m.simple_marker([lat, lon], popup=popup_string)
    else:
        #popup_string += '<br>No Data Available'
        popup_string += '<br>Not enough data available<br>requested pts: ' + str(min_data_pts ) + '<br>Available pts: ' + str(len(Hs_obs_df[n]))
        m.circle_marker([lat, lon], popup=popup_string, fill_color='#ff0000', radius=10000, line_color='#ff0000')
    n += 1
m.line(get_coordinates(bounding_box,bounding_box_type), line_color='#FF0000', line_weight=5)

inline_map(m)

# <codecell>

### Plot Hs and Tp for each station

# <codecell>

for df in obs_df:
    if len(df) > min_data_pts:
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(20,5))
        df['sea_surface_wave_significant_height (m)'].plot(ax=axes[0], color='r')
        axes[0].set_title(df.name)
        axes[0].set_ylabel('Hs (m)')
        df['sea_surface_wave_peak_period (s)'].plot(ax=axes[1])
        axes[1].set_title(df.name)
        axes[1].set_ylabel('Tp (s)')

# <markdowncell>

# ###Get model output from OPeNDAP URLS
# Try to open all the OPeNDAP URLS using Iris from the British Met Office. If we can open in Iris, we know it's a model result.

# <codecell>

name_in_list = lambda cube: cube.standard_name in data_dict['waves']['names']
constraint = iris.Constraint(cube_func=name_in_list)

# <codecell>

# Use only data within 0.04 degrees (about 4 km).
max_dist = 0.04
# Use only data where the standard deviation of the time series exceeds 0.01 m (1 cm).
# This eliminates flat line model time series that come from land points that should have had missing values.
min_var = 0.01
for url in dap_urls:
    if 'cdip' in url:
        # The CDIP buoys are known to be observed data, so let's just skip
        continue
    try:
        a = iris.load_cube(url, constraint)
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
            nsta = len(stations)
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
                            name = Hs_obs_df[n].name
                            Hs_obs_df[n] = pd.concat([Hs_obs_df[n], c], axis=1)
                            Hs_obs_df[n].name = name
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
                            name = Hs_obs_df[n].name
                            Hs_obs_df[n] = pd.concat([Hs_obs_df[n], c], axis=1)
                            Hs_obs_df[n].name = name
            elif len(r) == 1:
                print('[Data]:', url)
    except (ValueError, RuntimeError, CoordinateNotFoundError,
            ConstraintMismatchError) as e:
        warn("\n%s\n" % e)
        pass

# <markdowncell>

# ### Plot Modeled vs Obs Wave Height

# <codecell>

for df in Hs_obs_df:
    # Make sure there is obs data at the station for comparison
    if 'sea_surface_wave_significant_height (m)' in df.columns:
        ax = df.plot(figsize=(14, 6), title=df.name, legend=False)
        plt.setp(ax.lines[0], linewidth=4.0, color='0.7', zorder=1, marker='.')
        ax.legend()
        ax.set_ylabel('m')

