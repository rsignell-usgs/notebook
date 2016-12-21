# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# ># IOOS System Test: [Extreme Events Theme:](https://github.com/ioos/system-test/wiki/Development-of-Test-Themes#theme-2-extreme-events) Coastal Inundation

# <markdowncell>

# ### Can we compare observed and modeled current speeds at stations located within a bounding box? 
# This notebook is based on [IOOS System Test: Inundation](http://nbviewer.ipython.org/github/ioos/system-test/blob/master/Theme_2_Extreme_Events/Scenario_2A_Coastal_Inundation/Scenario_2A_Water_Level_Signell.ipynb)
# 
# Methodology:
# * Define temporal and spatial bounds of interest, as well as parameters of interest
# * Search for available service endpoints in the NGDC CSW catalog meeting search criteria
# * Extract OPeNDAP data endpoints from model datasets and SOS endpoints from observational datasets
# * Obtain observation data sets from stations within the spatial boundaries
# * Using DAP (model) endpoints find all available models data sets that fall in the area of interest, for the specified time range, and extract a model grid cell closest to all the given station locations
# * Plot observation stations on a map (red marker for model grid points)
# * Plot modelled and observed time series current data on same axes for comparison
# 

# <headingcell level=4>

# import required libraries

# <codecell>

import datetime as dt
from warnings import warn

import folium
from IPython.display import HTML
import iris
from iris.exceptions import CoordinateNotFoundError, ConstraintMismatchError
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from owslib.csw import CatalogueServiceWeb
from owslib import fes
import pandas as pd
from pyoos.collectors.coops.coops_sos import CoopsSos
import requests

from utilities import (fes_date_filter, coops2df, find_timevar, find_ij, nearxy, service_urls, mod_df, 
                       get_coordinates, inline_map, get_Coops_longName)

# <headingcell level=4>

# Speficy Temporal and Spatial conditions

# <codecell>

bounding_box_type = "box" 

# Bounding Box [lon_min, lat_min, lon_max, lat_max]
area = {'Hawaii': [-160.0, 18.0, -154., 23.0],
        'Gulf of Maine': [-72.0, 41.0, -69.0, 43.0],
        'New York harbor region': [-75., 39., -71., 41.5],
        'Puerto Rico': [-75, 12, -55, 26],
        'East Coast': [-77, 36, -73, 38],
        'North West': [-130, 38, -121, 50]}

bounding_box = area['East Coast']

#temporal range
jd_now = dt.datetime.utcnow()
jd_start,  jd_stop = jd_now - dt.timedelta(days=4), jd_now #+ dt.timedelta(days=3)

start_date = jd_start.strftime('%Y-%m-%d %H:00')
stop_date = jd_stop.strftime('%Y-%m-%d %H:00')

jd_start = dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
jd_stop = dt.datetime.strptime(stop_date, '%Y-%m-%d %H:%M')
print start_date,'to',stop_date

# <headingcell level=4>

# Specify data names of interest

# <codecell>

#put the names in a dict for ease of access 
data_dict = {}
sos_name = 'Currents'
data_dict['currents'] = {
 "u_names":['eastward_sea_water_velocity_assuming_no_tide','surface_eastward_sea_water_velocity','*surface_eastward_sea_water_velocity*', 'eastward_sea_water_velocity'], 
 "v_names":['northward_sea_water_velocity_assuming_no_tide','surface_northward_sea_water_velocity','*surface_northward_sea_water_velocity*', 'northward_sea_water_velocity'],
 "sos_name":['currents']}  

# <headingcell level=3>

# Search CSW for datasets of interest

# <codecell>

# endpoint = 'http://geo.gov.ckan.org/csw'            # data.gov
# endpoint = 'https://data.noaa.gov/csw'              # data.noaa.gov
# endpoint = 'http://www.nodc.noaa.gov/geoportal/csw' # nodc
endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw' # NGDC Geoportal

csw = CatalogueServiceWeb(endpoint,timeout=60)

for oper in csw.operations:
    if oper.name == 'GetRecords':
        cnstr = oper.constraints['SupportedISOQueryables']['values']
        print('\nISO Queryables:%s\n' % '\n'.join(cnstr))

# <codecell>

# convert User Input into FES filters
start,stop = fes_date_filter(start_date,stop_date)
bbox = fes.BBox(bounding_box)

#use the search name to create search filter
or_filt = fes.Or([fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                    escapeChar='\\',wildCard='*',singleChar='?') for val in data_dict['currents']['u_names']])

val = 'Averages'
not_filt = fes.Not([fes.PropertyIsLike(propertyname='apiso:AnyText',
                                       literal=('*%s*' % val),
                                       escapeChar='\\',
                                       wildCard='*',
                                       singleChar='?')])
filter_list = [fes.And([ bbox, start, stop, or_filt, not_filt]) ]
# connect to CSW, explore it's properties
# try request using multiple filters "and" syntax: [[filter1,filter2]]
csw.getrecords2(constraints=filter_list, maxrecords=1000, esn='full')
print str(len(csw.records)) + " csw records found"
for rec, item in csw.records.items():
    print(item.title)

# <markdowncell>

# Dap URLS

# <codecell>

dap_urls = service_urls(csw.records)
#remove duplicates and organize
dap_urls = sorted(set(dap_urls))
print "\n".join(dap_urls)

# <markdowncell>

# SOS URLs

# <codecell>

sos_urls = service_urls(csw.records,service='sos:url')
#Add known NDBC SOS
sos_urls.append("http://sdf.ndbc.noaa.gov/sos/server.php")  #?request=GetCapabilities&service=SOS

sos_urls = sorted(set(sos_urls))
print "Total SOS:",len(sos_urls)
print "\n".join(sos_urls)

# <markdowncell>

# ### SOS Requirements

# <codecell>

start_time = dt.datetime.strptime(start_date,'%Y-%m-%d %H:%M')
end_time = dt.datetime.strptime(stop_date,'%Y-%m-%d %H:%M')
iso_start = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
iso_end = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

# <codecell>

collector = CoopsSos()
collector.start_time = start_time
collector.end_time = end_time
collector.variables = data_dict["currents"]["sos_name"]
collector.server.identification.title
print collector.start_time,":", collector.end_time
ofrs = collector.server.offerings

# <markdowncell>

# ###Find all SOS stations within the bounding box and time extent

# <codecell>

print "Date: ",iso_start," to ", iso_end
box_str=','.join(str(e) for e in bounding_box)
print "Lat/Lon Box: ",box_str

url = (('http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?'
       'service=SOS&request=GetObservation&version=1.0.0&'
       'observedProperty=%s&bin=1&'
       'offering=urn:ioos:network:NOAA.NOS.CO-OPS:CurrentsActive&'
       'featureOfInterest=BBOX:%s&responseFormat=text/csv') % (sos_name, box_str))

print url
obs_loc_df = pd.read_csv(url)

# <codecell>

obs_loc_df = obs_loc_df.loc[obs_loc_df['bin (count)']==1,:]
obs_loc_df.head()

# <codecell>

# Index the data frame to filter repeats by bin #
stations = [sta.split(':')[-1] for sta in obs_loc_df['station_id']]

obs_lon = [sta for sta in obs_loc_df['longitude (degree)']]
obs_lat = [sta for sta in obs_loc_df['latitude (degree)']]

# <headingcell level=3>

# Request CSV response from collector and convert to Pandas DataFrames

# <codecell>

obs_df = []
current_speed_df = []
sta_names = []
sta_failed = []
for sta in stations:
    try:
        df = coops2df(collector, sta, sos_name, iso_start, iso_end)
    except Exception as e:
        print "Error" + str(e)
        continue

    name = df.name
    sta_names.append(name)
#     if df.empty:
#         sta_failed.append(name)
#         df = DataFrame(np.arange(len(ts)) * np.NaN, index=ts.index, columns=['Observed Data'])
#         df.name = name
    obs_df.append(df)
    obs_df[-1].name = name
    
    # Create a separate dataframe for only sea water speed
    current_speed_df.append(pd.DataFrame(df['sea_water_speed (cm/s)']))
    current_speed_df[-1].name = name

# <markdowncell>

# ### Plot current speeds as a function of time and distance from sensor

# <codecell>

for df in obs_df:
    num_bins = df['number_of_bins'][0]
    depth = df['bin_distance (m)'].values[0:num_bins]
    time = df.loc[df['bin (count)']==(1)].index.values
    xdates = [dt.datetime.strptime(str(date).split('.')[0],'%Y-%m-%dT%H:%M:%S') for date in time]
    dates = mdates.date2num(xdates)
    
    # Extract data from each depth bin to create a 2D matrix of current speeds (depth x time)
    data = np.zeros((num_bins, len(df.index)/num_bins))
    for n in range(num_bins):
        data[n,:] = df.loc[df['bin (count)']==(n+1),'sea_water_speed (cm/s)'].values

    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    im = ax.pcolor(dates, depth, data, vmin=abs(data).min(), vmax=abs(data).max())
    cb = fig.colorbar(im, ax=ax)
    ax.set_ylabel = 'bin_distance (m)'
    ax.set_title = df.name

# <markdowncell>

# ### Plot current speeds as a time series

# <codecell>

# break the current speed data frame into data frames by bin
for df in obs_df:
    fig, axes = plt.subplots(1, 1, figsize=(20,6))
    
    # Only plot the first bin
    axes = df.loc[df['bin (count)']==(1),'sea_water_speed (cm/s)'].plot(title=df.name, legend=False, color='b')
    plt.setp(axes.lines[0], linewidth=1.0, zorder=1)
    axes.set_ylabel('Current Speed (cm/s)')
    for tl in axes.get_yticklabels():
        tl.set_color('b')
    axes.yaxis.label.set_color('blue')
        
    ax2 = axes.twinx()
    axes2 = df.loc[df['bin (count)']==(1),'direction_of_sea_water_velocity (degree)'].plot(title=df.name, legend=False, ax=ax2, color='g')
    plt.setp(axes.lines[0], linewidth=1.0, zorder=1)
    axes2.set_ylabel('Current Direction (degrees)')
    for tl in ax2.get_yticklabels():
        tl.set_color('g')
    axes2.yaxis.label.set_color('green')

# <markdowncell>

# ### Plot Sea Water Temperature for each station (just because...)

# <codecell>

# break the current speed data frame into data frames by bin
for df in obs_df:
    figure()
    # Only plot the first bin
    ax = df.loc[df['bin (count)']==(1),'sea_water_temperature (C)'].plot(figsize=(14, 6), title=df.name, legend=False)
    plt.setp(ax.lines[0], linewidth=1.0, zorder=1)
    ax.legend()
    ax.set_ylabel('sea_water_temperature (C)')

# <markdowncell>

# ###Get model output from OPeNDAP URLS
# Try to open all the OPeNDAP URLS using Iris from the British Met Office. If we can open in Iris, we know it's a model result.

# <codecell>

name_in_list = lambda cube: cube.standard_name in data_dict['currents']['u_names']
u_constraint = iris.Constraint(cube_func=name_in_list)

name_in_list = lambda cube: cube.standard_name in data_dict['currents']['v_names']
v_constraint = iris.Constraint(cube_func=name_in_list)
 

# <codecell>

# # Create time index for model DataFrame
ts_rng = pd.date_range(start=jd_start, end=jd_stop, freq='6Min')
ts = pd.DataFrame(index=ts_rng)

# Create list of model DataFrames for each station
model_df = []
for df in obs_df:
    model_df.append(pd.DataFrame(index=ts.index))
    model_df[-1].name = df.name

model_lat = []
model_lon = []
# Use only data within 1 degrees.
max_dist = 1

# Use only data where the standard deviation of the time series exceeds 0.01 m (1 cm).
# This eliminates flat line model time series that come from land points that should have had missing values.
min_var = 0.01

for url in dap_urls:
    if 'hfrnet' in url:
        print 'Skipping HF Radar Obs Data'
        continue
    
    if 'NECOFS' in url:
        try:
            print 'Attemping to load {0}'.format(url)
            u = iris.load_cube(url, u_constraint)
            v = iris.load_cube(url, v_constraint)

            # take first 20 chars for model name
            mod_name = u.attributes['title'][0:20]
            r = u.shape
            timevar = find_timevar(u)
            lat = u.coord(axis='Y').points
            lon = u.coord(axis='X').points
            jd = timevar.units.num2date(timevar.points)
            start = timevar.units.date2num(jd_start)
            istart = timevar.nearest_neighbour_index(start)
            stop = timevar.units.date2num(jd_stop)
            istop = timevar.nearest_neighbour_index(stop)

            # Only proceed if we have data in the range requested.
            if istart != istop:
                nsta = len(stations)
                if len(r) == 4:
                    #HYCOM and ROMS
                    # Dimensions are time, elevation, lat, lon
                    d = u[0, 0:1, :, :].data
                    # Find the closest non-land point from a structured grid model.
                    if len(lon.shape) == 1:
                        lon, lat = np.meshgrid(lon, lat)
                    j, i, dd = find_ij(lon, lat, d, obs_lon, obs_lat)
                
                    for n in range(nsta):
                        # Only use if model cell is within max_dist of station
                        if dd[n] <= max_dist:
                            u_arr = u[istart:istop, 0:1, j[n], i[n]].data
                            v_arr = v[istart:istop, 0:1, j[n], i[n]].data
                            arr = np.sqrt(u_arr**2 + v_arr**2)
                            if u_arr.std() >= min_var:
                                c = mod_df(arr, timevar, istart, istop,
                                           mod_name, ts)
                                name = obs_df[n].name
                                model_df[n] = pd.concat([model_df[n], c], axis=1)
                                model_df[n].name = name
                            else:
                                print 'min_var error'
                        else:
                            print 'Max dist error'
                if len(r) == 3:
                    #NECOFS
                    print('[Structured grid model]:', url)
                    d = u[0, 0:1, :].data
                    # Find the closest non-land point from a structured grid model.
                    index, dd = nearxy(lon.flatten(), lat.flatten(),
                                       obs_lon, obs_lat)
                    
                    # Keep the lat lon of the grid point
                    model_lat = lat[index].tolist()
                    model_lon = lon[index].tolist()
                    
                    for n in range(nsta):
                        # Only use if model cell is within max_dist of station
                        if dd[n] <= max_dist:
                            u_arr = u[istart:istop, 0:1, index[n]].data
                            v_arr = v[istart:istop, 0:1, index[n]].data
                            # Model data is in m/s so convert to cm/s
                            arr = np.sqrt((u_arr*100.0)**2 + (v_arr*100.0)**2)
                            if u_arr.std() >= min_var:
                                c = mod_df(arr, timevar, istart, istop,
                                           mod_name, ts)
                                name = obs_df[n].name
                                model_df[n] = pd.concat([model_df[n], c], axis=1)
                                model_df[n].name = name
                            else:
                                print 'min_var error'
                        else:
                            print 'Max dist error'

                elif len(r) == 2:
                    print('[Unstructured grid model]:', url)
                    # Find the closest point from an unstructured grid model.
                    index, dd = nearxy(lon.flatten(), lat.flatten(),
                                       obs_lon, obs_lat)
                    for n in range(nsta):
                        # Only use if model cell is within max_dist of station
                        if dd[n] <= max_dist:
                            arr = u[istart:istop, index[n]].data
                            print arr
                            if arr.std() >= min_var:
                                c = mod_df(arr, timevar, istart, istop,
                                           mod_name, ts)
                                name = obs_df[n].name
                                model_df[n] = pd.concat([model_df[n], c], axis=1)
                                model_df[n].name = name
                            else:
                                print 'min_var error'
                        else:
                            print 'Max dist error'
                elif len(r) == 1:
                    print('[Data]:', url)

            else:
                print 'No data in range'
        except (ValueError, RuntimeError, CoordinateNotFoundError,
                ConstraintMismatchError) as e:
            warn("\n%s\n" % e)
            pass

# <markdowncell>

# ### Plot the Observation Stations and Model Points on same Map

# <codecell>

#find center of bounding box
lat_center = abs(bounding_box[3] - bounding_box[1])/2 + bounding_box[1]
lon_center = abs(bounding_box[0]-bounding_box[2])/2 + bounding_box[0]
m = folium.Map(location=[lat_center, lon_center], zoom_start=7)

for n in range(len(stations)):
    #get the station data from the sos end point
    name = stations[n]
    longname = obs_df[n].name
    lat = obs_lat[n]
    lon = obs_lon[n]
    popup_string = ('<b>Station:</b><br>'+ longname)
    m.simple_marker([lat, lon], popup=popup_string)
    
    popup_string = ('<b>Model Grid Point</b>')
    m.circle_marker([model_lat[n], model_lon[n]], popup=popup_string, fill_color='#ff0000', radius=5000, line_color='#ff0000')

m.line(get_coordinates(bounding_box, bounding_box_type), line_color='#FF0000', line_weight=5)

inline_map(m)

# <markdowncell>

# #### Plot Modeled vs Obs Currents

# <codecell>

# for df in model_df:
for n in range(len(obs_df)):
    ax = model_df[n].plot(figsize=(14, 6), title=model_df[n].name, legend=False)
    plt.setp(ax.lines[0], linewidth=3, color='0.7', zorder=1)
    ax.legend()
#     ax.set_ylabel('Current speed m/s')

    # Overlay the obs data plot the first bin
    ax = obs_df[n].loc[obs_df[n]['bin (count)']==(1),'sea_water_speed (cm/s)'].plot(figsize=(14, 6), legend=False)
    plt.setp(ax.lines[1], linewidth=1.0, zorder=1)
    ax.legend()
    ax.set_ylabel('Current Speed (cm/s)')
    plt.show()

