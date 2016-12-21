# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# ># IOOS System Test: [Extreme Events Theme:](https://github.com/ioos/system-test/wiki/Development-of-Test-Themes#theme-2-extreme-events) Coastal Inundation

# <markdowncell>

# ### Can we compare observed and modeled wind speeds at stations located within a bounding box? 
# This notebook is based on [IOOS System Test: Inundation](http://nbviewer.ipython.org/github/ioos/system-test/blob/master/Theme_2_Extreme_Events/Scenario_2A_Coastal_Inundation/Scenario_2A_Water_Level_Signell.ipynb)
# 
# Methodology:
# * Define temporal and spatial bounds of interest, as well as parameters of interest
# * Search for available service endpoints in the NGDC CSW catalog meeting search criteria
# * Extract OPeNDAP data endpoints from model datasets and SOS endpoints from observational datasets
# * Obtain observation data sets from stations within the spatial boundaries
# * Using DAP (model) endpoints find all available models data sets that fall in the area of interest, for the specified time range, and extract a model grid cell closest to all the given station locations
# * Plot observation stations on a map (red marker for model grid points) and draw a line between each station and the model grid point used for comparison
# * Plot modeled and observed time series wind speed on same axes for comparison
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
from owslib.csw import CatalogueServiceWeb
from owslib import fes
import pandas as pd
from pyoos.collectors.coops.coops_sos import CoopsSos
import requests

from utilities import (fes_date_filter, coops2df, find_timevar, find_ij, nearxy, service_urls, mod_df, 
                       get_coordinates, inline_map, get_Coops_longName, css_styles)
css_styles()

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
        'North West': [-130, 38, -121, 50],
        'Gulf of Mexico': [-92, 28, -84, 31],
        'Arctic': [-179, 63, -140, 80]}

bounding_box = area['Gulf of Mexico']

#temporal range
jd_now = dt.datetime.utcnow()
jd_start,  jd_stop = jd_now - dt.timedelta(days=11), jd_now + dt.timedelta(days=3)

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
sos_name = 'Winds'
data_dict['winds'] = {
 "u_names":['eastward_wind', 'u-component_of_wind', 'u_component_of_wind', 'u_component_of_wind_height_above_ground', 'u-component_of_wind_height_above_ground', 'ugrd10m', 'wind'], 
 "v_names":['northward_wind', 'v-component_of_wind', 'v-component_of_wind_height_above_ground', 'vgrd10m', 'wind'],
 "sos_name":['winds']}  

# <headingcell level=3>

# Check CSW for bounding box filter capabilities

# <codecell>

endpoints = ['http://www.nodc.noaa.gov/geoportal/csw',
             'http://www.ngdc.noaa.gov/geoportal/csw',
             'http://catalog.data.gov/csw-all',
             'http://geoport.whoi.edu/geoportal/csw',
             'https://edg.epa.gov/metadata/csw',
             'http://cmgds.marine.usgs.gov/geonetwork/srv/en/csw',
             'http://cida.usgs.gov/gdp/geonetwork/srv/en/csw',
             'http://geodiscover.cgdi.ca/wes/serviceManagerCSW/csw', 
             'http://geoport.whoi.edu/gi-cat/services/cswiso']
bbox_endpoints = []
for url in endpoints:
#     queryables = []
    try:
        csw = CatalogueServiceWeb(url, timeout=20)
    except BaseException:
        print "Failure - %s - Timed out" % url
    if "BBOX" in csw.filters.spatial_operators:
        print "Success - %s - BBOX Query supported" % url
        bbox_endpoints.append(url)    
    else:
        print "Failure - %s - BBOX Query NOT supported" % url


# <markdowncell>

# ### Check the CSW endpoints for wind data in the date range specified

# <markdowncell>

# <div class="warning"><strong>Data discovery is limited</strong> - Most of the CSW endpoints don't have recent wind data available.</div>

# <codecell>

for endpoint in bbox_endpoints:
    print endpoint
    
    csw = CatalogueServiceWeb(endpoint,timeout=60)

    # convert User Input into FES filters
    start,stop = fes_date_filter(start_date,stop_date)
    bbox = fes.BBox(bounding_box)

    #use the search name to create search filter
    or_filt = fes.Or([fes.PropertyIsLike(propertyname='apiso:AnyText',literal='*%s*' % val,
                        escapeChar='\\',wildCard='*',singleChar='?') for val in data_dict['winds']['u_names']])

    filter_list = [fes.And([ bbox, start, stop, or_filt]) ]
#     filter_list = [fes.And([ bbox, or_filt]) ]
    # connect to CSW, explore it's properties
    # try request using multiple filters "and" syntax: [[filter1,filter2]]
    try:
        csw.getrecords2(constraints=filter_list, maxrecords=1000, esn='full')
    except Exception as e:
        print 'ERROR - ' + str(e)
    else:
        print str(len(csw.records)) + " csw records found"
        
        # Print titles
        for rec, item in csw.records.items():
            print(item.title)
        
    print '\n'

# <markdowncell>

# ### Use NGDC CSW

# <codecell>

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw' # NGDC Geoportal
csw = CatalogueServiceWeb(endpoint,timeout=60)

# convert User Input into FES filters
start,stop = fes_date_filter(start_date,stop_date)
bbox = fes.BBox(bounding_box)

#use the search name to create search filter
or_filt = fes.Or([fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                    escapeChar='\\',wildCard='*',singleChar='?') for val in data_dict['winds']['u_names']])

filter_list = [fes.And([ bbox, start, stop, or_filt]) ]
# connect to CSW, explore it's properties
# try request using multiple filters "and" syntax: [[filter1,filter2]]
try:
    csw.getrecords2(constraints=filter_list, maxrecords=1000, esn='full')
except Exception as e:
    print 'ERROR - ' + str(e)
    

# <markdowncell>

# DAP URLS

# <codecell>

# Now print the DAP endpoints
dap_urls = service_urls(csw.records)
#remove duplicates and organize
dap_urls = sorted(set(dap_urls))
print "\n".join(dap_urls)

# <markdowncell>

# SOS URLs

# <markdowncell>

# <div class="error"><strong>CDIP buoys shouldn't be appearing</strong> - The CDIP buoys are located in the Pacific but are coming up in the Gulf of Mexico bounding box searches. See [issue](https://github.com/ioos/system-test/issues/133).</div>

# <codecell>

sos_urls = service_urls(csw.records,service='sos:url')
#Add known NDBC SOS
# sos_urls.append("http://sdf.ndbc.noaa.gov/sos/server.php")  #?request=GetCapabilities&service=SOS

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
collector.variables = data_dict["winds"]["sos_name"]
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
       'observedProperty=%s&'
       'offering=urn:ioos:network:NOAA.NOS.CO-OPS:MetActive&'
       'featureOfInterest=BBOX:%s&responseFormat=text/csv') % (sos_name, box_str))

# url = (('http://sdf.ndbc.noaa.gov/sos/server.php?request=GetObservation&service=SOS&version=1.0.0&offering=urn:ioos:network:noaa.nws.ndbc:all'
#         '&featureofinterest=BBOX:%s&observedproperty=%s&responseformat=text/csv') % (box_str, sos_name))
print url
obs_loc_df = pd.read_csv(url)

# <codecell>

obs_loc_df.head()

# <codecell>

# Index the data frame to filter repeats by bin #
stations = [sta.split(':')[-1] for sta in obs_loc_df['station_id']]

obs_lon = [sta for sta in obs_loc_df['longitude (degree)']]
obs_lat = [sta for sta in obs_loc_df['latitude (degree)']]

# <headingcell level=3>

# Request CSV response from collector and convert to Pandas DataFrames

# <codecell>

ts_rng = pd.date_range(start=jd_start, end=jd_stop, freq='6Min')
ts = pd.DataFrame(index=ts_rng)

obs_df = []
wind_speed_df = []
sta_names = []
sta_failed = []
for sta in stations:
    try:
        df = coops2df(collector, sta, sos_name)
    except Exception as e:
        print "Error" + str(e)
        continue

    name = df.name
    sta_names.append(name)
    if df.empty:
        sta_failed.append(name)
        df = pd.DataFrame(np.arange(len(ts)) * np.NaN, index=ts.index, columns=['Observed Data'])
        df.name = name
    # Limit interpolation to 10 points (10 @ 6min = 1 hour).
#     col = 'Observed Data'
#     concatenated = pd.concat([df, ts], axis=1).interpolate(limit=10)[col]
#     obs_df.append(pd.DataFrame(concatenated))
    
    obs_df.append(df)
    obs_df[-1].name = name

# <markdowncell>

# ### Plot wind speeds and gusts as a time series

# <codecell>

for df in obs_df:
    fig, axes = plt.subplots(1, 1, figsize=(20,6))
    
    axes = df['wind_speed (m/s)'].plot(title=df.name, legend=True, color='b')
    axes.set_ylabel('Wind Speed (m/s)')
    for tl in axes.get_yticklabels():
        tl.set_color('b')
    axes.yaxis.label.set_color('blue')
        
    axes = df['wind_speed_of_gust (m/s)'].plot(title=df.name, legend=True, color='g')
    plt.setp(axes.lines[0], linewidth=1.0, zorder=1)

# <markdowncell>

# ### Plot wind direction

# <codecell>

for df in obs_df:
    figure()
    # Only plot the first bin
    ax = df['wind_from_direction (degree)'].plot(figsize=(14, 6), title=df.name, legend=False)
    plt.setp(ax.lines[0], linewidth=1.0, zorder=1)
    ax.legend()
    ax.set_ylabel('Wind Direction (degree)')

# <markdowncell>

# ###Get model output from OPeNDAP URLS
# Try to open all the OPeNDAP URLS using Iris from the British Met Office. If we can open in Iris, we know it's a model result.

# <codecell>

name_in_list = lambda cube: cube.standard_name in data_dict['winds']['u_names']
u_constraint = iris.Constraint(cube_func=name_in_list)

name_in_list = lambda cube: cube.standard_name in data_dict['winds']['v_names']
v_constraint = iris.Constraint(cube_func=name_in_list)
 

# <codecell>

# # Create time index for model DataFrame
ts_rng = pd.date_range(start=jd_start, end=jd_stop, freq='H')
ts = pd.DataFrame(index=ts_rng)

# Create list of model DataFrames for each station
model_df = []
for df in obs_df:
    model_df.append(pd.DataFrame(index=ts.index))
    model_df[-1].name = df.name

model_lat = []
model_lon = []

# Use only data within 0.4 degrees.
max_dist = 0.4

# Use only data where the standard deviation of the time series exceeds 0.01 m (1 cm).
# This eliminates flat line model time series that come from land points that should have had missing values.
min_var = 0.01

# print dap_urls
for url in dap_urls:
#     model_df, model_lat, model_lon = get_model_data(url, model_df, max_dist, min_var)
    try:
        print 'Attemping to load {0}'.format(url)
        u = iris.load_cube(url, u_constraint)
        v = iris.load_cube(url, v_constraint)

        # take first 20 chars for model name
        mod_name = u.attributes['title'][0:30]
        r = u.shape
        timevar = find_timevar(u)
        lat = u.coord(axis='Y').points
        lon = u.coord(axis='X').points
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
            nsta = len(stations)
            
            if len(r) == 3:
                print('[Structured grid model]:', url)
                d = u[0, :, :].data
                    
                if len(lon.shape) == 1:
                    new_lon, new_lat = np.meshgrid(lon, lat)
                else:
                    new_lon, new_lat = lon, lat
                
                # Find the closest non-land point from a structured grid model.
                j, i, dd = find_ij(new_lon, new_lat, d, obs_lon, obs_lat)

                # Keep the lat lon of the grid point
                model_lat = lat[j].tolist()
                model_lon = lon[i].tolist()
 
                for n in range(nsta):
                    # Only use if model cell is within max_dist of station
                    if dd[n] <= max_dist:
                        u_arr = u[istart:istop, j[n], i[n]].data
                        v_arr = v[istart:istop, j[n], i[n]].data
                        # Model data is in m/s so convert to cm/s
                        arr = np.sqrt((u_arr)**2 + (v_arr)**2)
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
            else:
                print 'Grid has {0} dimensions'.format(str(len(r)))
        else:
            print 'No data in range'
    except Exception as e:
        warn("\n%s\n" % e)
        pass
        

# <markdowncell>

# ### Plot the Observation Stations and Model Points on same Map

# <codecell>

# Find center of bounding box
lat_center = abs(bounding_box[3] - bounding_box[1])/2 + bounding_box[1]
lon_center = abs(bounding_box[0]-bounding_box[2])/2 + bounding_box[0]
m = folium.Map(location=[lat_center, lon_center], zoom_start=6)

# Now loop through stations and plot markers
for n in range(len(stations)):
    # Get the station name
    name = stations[n]
    longname = obs_df[n].name
    
    # Get obs station lat/lon
    olat = obs_lat[n]
    olon = obs_lon[n]
    
    # Create obs station marker
    popup_string = ('<b>Station:</b><br>'+ longname)
    m.simple_marker([olat, olon], popup=popup_string)
    
    # Only plot if there is model data
    if model_lat:
        # Get model grid points lat/lon
        mlat = model_lat[n]
        mlon = model_lon[n]
        # Plot a line from obs station to corresponding model grid point
        data_1=[olat,olon]
        data_2=[model_lat[n],model_lon[n]]
        m.line([data_1,data_2],line_color='#00FF00', line_weight=5)

        # Create model grid point marker
        popup_string = ('<b>Model Grid Point</b>')
    #     m.simple_marker([model_lat[n], model_lon[n]], popup=popup_string, marker_color='red', marker_icon='download',clustered_marker=False)
        m.circle_marker([mlat, mlon], popup=popup_string, fill_color='#ff0000', radius=5000, line_color='#ff0000')

m.line(get_coordinates(bounding_box, bounding_box_type), line_color='#FF0000', line_weight=5)

inline_map(m)

# <markdowncell>

# #### Plot Modeled vs Obs Winds

# <codecell>

for n in range(len(obs_df)):
    # First plot the model data
    if not model_df[n].empty and not obs_df[n].empty:
        ax = model_df[n].plot(figsize=(14, 6), title=model_df[n].name, legend=False)
        plt.setp(ax.lines[0], linewidth=3, color='0.7', zorder=1)
        ax.legend()

        # Overlay the obs data (resample to hourly instead of 6 mins!)
        ax = obs_df[n]['wind_speed (m/s)'].resample('H', how='mean').plot(title=obs_df[n].name, legend=False, color='b')
        plt.setp(ax.lines[1], linewidth=1.0, zorder=1)
        ax.legend()
        ax.set_ylabel('Wind Speed (m/s)')
        plt.show()

# <codecell>


