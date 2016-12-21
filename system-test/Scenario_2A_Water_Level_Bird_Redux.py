# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# ># IOOS System Test: [Extreme Events Theme:](https://github.com/ioos/system-test/wiki/Development-of-Test-Themes#theme-2-extreme-events) Inundation

# <markdowncell>

# ### Can we estimate the return period of a water level by comparing modeled and/or observed water levels with NOAA exceedance probability plots?

# <markdowncell>

# Methodology:
# 
# * Define temporal and spatial bounds of interest, as well as parameters of interest
# * Search for availavle service endpoints in the NGDC CSW catalog, then inform the user of the DAP (model) and SOS (observation) services endpoints available
# * Obtain the stations in the spatial boundaries, and processed to obtain observation data for temporal contraints, identifying the yearly max
# * Plot observation stations on a map and indicate to the user if the minimum number of years has been met for extreme value analysis (red marker if condition is false)
# * Using DAP (model) endpoints find all available models data sets that fall in the area of interest, for the specified time range, and extract a model grid cell closest to all the given station locations (<b>Still in Development</b>)
# * Plot the extracted model grid cell from each available model on to the map
# * Plot the annual max for each station as a timeseries plot
# * Perform extreme value analysis for a selected station identifying the return period and compare to NOAA tides and currents plot for one of the same stations
# 
# Esimated Time To Process Notebook: --.--

# <headingcell level=4>

# import required libraries

# <codecell>

import matplotlib.pyplot as plt
from pylab import *
import sys
import csv
import json
from scipy.stats import genextreme
import scipy.stats as ss
import numpy as np

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import random
import netCDF4
import pandas as pd
import datetime as dt
from pyoos.collectors.coops.coops_sos import CoopsSos
import cStringIO
import iris
import urllib2
import parser
from lxml import etree       #TODO suggest using bs4 instead for ease of access to XML objects

#generated for csw interface
#from fes_date_filter_formatter import fes_date_filter  #date formatter (R.Signell)
import requests              #required for the processing of requests
from utilities import * 

from IPython.display import HTML, Image
from shapely.geometry import Polygon,Point,LineString  #used for lat lon points
import folium #required for leaflet mapping
from pydap.client import open_url #pypdap

import datetime as dt
from datetime import datetime
from datetime import timedelta
%matplotlib inline  

# <markdowncell>

# some functions from [Rich Signell Notebook](http://nbviewer.ipython.org/github/rsignell-usgs/notebook/blob/fef9438303b49a923024892db1ef3115e34d8271/CSW/IOOS_inundation.ipynb)

# <headingcell level=4>

# Speficy Temporal and Spatial conditions

# <codecell>

#bounding box of interest,[bottom right[lat,lon], top left[lat,lon]]
bounding_box_type = "box" 
bounding_box = [[-75.94,38.67],[-66.94,41.5]]

#temporal range
start_date = dt.datetime(1980,5,1).strftime('%Y-%m-%d %H:00')
end_date = dt.datetime(2014,5,1).strftime('%Y-%m-%d %H:00')
time_date_range = [start_date,end_date]  #start_date_end_date

print start_date,'to',end_date

#number of years required for analysis, obs and model data
num_years_required = 30

# <codecell>

name_list=['water_surface_height_above_reference_datum',
    'sea_surface_height_above_geoid','sea_surface_elevation',
    'sea_surface_height_above_reference_ellipsoid','sea_surface_height_above_sea_level',
    'sea_surface_height','water level']

sos_name = 'water_surface_height_above_reference_datum'

# <codecell>

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw' # NGDC Geoportal
csw = CatalogueServiceWeb(endpoint,timeout=60)

for oper in csw.operations:
    if oper.name == 'GetRecords':
        print '\nISO Queryables:\n',oper.constraints['SupportedISOQueryables']['values']
        #pass
        
#put the names in a dict for ease of access 
data_dict = {}
data_dict["water"] = {"names":['water_surface_height_above_reference_datum',
    'sea_surface_height_above_geoid','sea_surface_elevation',
    'sea_surface_height_above_reference_ellipsoid','sea_surface_height_above_sea_level',
    'sea_surface_height','water level'], "sos_name":['water_surface_height_above_reference_datum']}      

# <codecell>

def fes_date_filter(start_date='1900-01-01',stop_date='2100-01-01',constraint='overlaps'):
    if constraint == 'overlaps':
        start = fes.PropertyIsLessThanOrEqualTo(propertyname='apiso:TempExtent_begin', literal=stop_date)
        stop = fes.PropertyIsGreaterThanOrEqualTo(propertyname='apiso:TempExtent_end', literal=start_date)
    elif constraint == 'within':
        start = fes.PropertyIsGreaterThanOrEqualTo(propertyname='apiso:TempExtent_begin', literal=start_date)
        stop = fes.PropertyIsLessThanOrEqualTo(propertyname='apiso:TempExtent_end', literal=stop_date)
    return start,stop

# <codecell>

# convert User Input into FES filters
start,stop = fes_date_filter(start_date,end_date)
box = []
box.append(bounding_box[0][0])
box.append(bounding_box[0][1])
box.append(bounding_box[1][0])
box.append(bounding_box[1][1])
bbox = fes.BBox(box)

or_filt = fes.Or([fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                    escapeChar='\\',wildCard='*',singleChar='?') for val in name_list])
val = 'Averages'
not_filt = fes.Not([fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')])

# <codecell>

filter_list = [fes.And([ bbox, start, stop, or_filt, not_filt]) ]
# connect to CSW, explore it's properties
# try request using multiple filters "and" syntax: [[filter1,filter2]]
csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')

# <codecell>

def service_urls(records,service_string='urn:x-esri:specification:ServiceType:odp:url'):
    """
    extract service_urls of a specific type (DAP, SOS) from records
    """
    urls=[]
    for key,rec in records.iteritems():
        #create a generator object, and iterate through it until the match is found
        #if not found, gets the default value (here "none")
        url = next((d['url'] for d in rec.references if d['scheme'] == service_string), None)
        if url is not None:
            urls.append(url)
    return urls

# <codecell>

#print records that are available
print "number of datasets available: ",len(csw.records.keys())

# <markdowncell>

# Print all the records (should you want too)

# <codecell>

#print "\n".join(csw.records)

# <markdowncell>

# Dap URLS

# <codecell>

dap_urls = service_urls(csw.records,service_string='urn:x-esri:specification:ServiceType:odp:url')
#remove duplicates and organize
dap_urls = sorted(set(dap_urls))
print "Total DAP:",len(dap_urls)
#print the first 5...
print "\n".join(dap_urls[:])

# <markdowncell>

# SOS URLs

# <codecell>

sos_urls = service_urls(csw.records,service_string='urn:x-esri:specification:ServiceType:sos:url')
#remove duplicates and organize
sos_urls = sorted(set(sos_urls))
print "Total SOS:",len(sos_urls)
print "\n".join(sos_urls)

# <markdowncell>

# ### SOS Requirements
# #### Use Pyoos SOS collector to obtain Observation data from COOPS

# <codecell>

#use the get caps to get station start and get time

# <codecell>

start_time = dt.datetime.strptime(start_date,'%Y-%m-%d %H:%M')
end_time = dt.datetime.strptime(end_date,'%Y-%m-%d %H:%M')

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

print "Date: ",iso_start," to ", iso_end
box_str=','.join(str(e) for e in box)
print "Lat/Lon Box: ",box_str
#grab the sos url and use it for the service
url=(sos_urls[0].split("?")[0]+'?'
     'service=SOS&request=GetObservation&version=1.0.0&'
     'observedProperty=%s&offering=urn:ioos:network:NOAA.NOS.CO-OPS:WaterLevelActive&'
     'featureOfInterest=BBOX:%s&responseFormat=text/tab-separated-values&eventTime=%s') % (sos_name,box_str,iso_end)

r = requests.get(url)
data = r.text
#get the headers for the cols
data = data.split("\n")
headers =  data[0]
station_list_dict = dict()
#parse the headers so i can create a dict
c = 0
for h in headers.split("\t"):
    field = h.split(":")[0].split(" ")[0]
    station_list_dict[field] = {"id":c}
    c+=1

# <codecell>

def get_coops_longName(sta):
    """
    get longName for specific station from COOPS SOS using DescribeSensor request
    """
    url=(sos_urls[0].split("?")[0]+'?service=SOS&'
        'request=DescribeSensor&version=1.0.0&outputFormat=text/xml;subtype="sensorML/1.0.1"&'
        'procedure=%s') % sta
    tree = etree.parse(urllib2.urlopen(url))
    root = tree.getroot()
    longName=root.xpath("//sml:identifier[@name='longName']/sml:Term/sml:value/text()", namespaces={'sml':"http://www.opengis.net/sensorML/1.0.1"})
    return longName

# <codecell>

#finds the max value given a json object
def findMaxVal(data):
    dates_array = []
    vals_array = []
    for x in data:
        dates_array.append(str(x["t"]))
        vals_array.append(x["v"])
    
    p = np.array(vals_array,dtype=np.float)
    x = np.arange(len(p))
    max_val = np.amax(p)
    max_idx = np.argmax(p)
    return (max_val,len(p),dates_array[max_idx])

# <markdowncell>

# #### Extract the Observation Data from the collector

# <codecell>

def coops2data(collector,station_id,sos_name):
    collector.features = [station_id]
    collector.variables = [sos_name]
    station_data = dict()
    #loop through the years and get the data needed
    for year_station in range(int(collector.start_time.year),collector.end_time.year+1):      
        link = "http://tidesandcurrents.noaa.gov/api/datagetter?product="+sos_name+"&application=NOS.COOPS.TAC.WL&"
        date1 = "begin_date="+str(year_station)+"0101"
        date2 = "&end_date="+str(year_station)+"1231"
        datum = "&datum=MHHW"
        units = "&units=metric"
        station_request = "&station="+station_id+"&time_zone=GMT&units=english&format=json"
        http_request = link+date1+date2+units+datum+station_request
        #print http_request
        d_r = requests.get(http_request,timeout=20)
        if "Great Lake station" in d_r.text:
            pass
        else:
            key_list =  d_r.json().keys()
            if "data" in key_list:
                data = d_r.json()['data']
                max_value,num_samples,date_string = findMaxVal(data)
                station_data[str(year_station)] =  {"max":max_value,"num_samples":num_samples,"date_string":date_string,"raw":data}
                #print "\tyear:",year_station," MaxValue:",max_value
    return station_data

# <codecell>

#create dict of stations
station_list = []
for i in range(1,len(data)):
    station_info = data[i].split("\t")
    station = dict()
    for field in station_list_dict.keys():        
        col = station_list_dict[field]["id"]
        if col < len(station_info):
            station[field] = station_info[col]
    station["type"] = "obs"        
    station_list.append(station)        

# <codecell>

def add_invalid_marker(map,s,popup_string):
    map.circle_marker(location=[s["latitude"],s["longitude"]], popup=popup_string, fill_color='#ff0000', radius=10000, line_color='#ff0000')

# <markdowncell>

# TODO: Add check before extracting the data to see if the required number of years will be met, i.e use SOS GetCaps and begin and end time

# <codecell>

def does_station_have_enough_times():
    return True

# <codecell>

#Embeds the HTML source of the map directly into the IPython notebook.
def inline_map(map):   
    map._build_map()
    return HTML('<iframe srcdoc="{srcdoc}" style="width: 100%; height: 500px; border: none"></iframe>'.format(srcdoc=map.HTML.replace('"', '&quot;')))


#print bounding_box[0]
map = folium.Map(location=[bounding_box[0][1], bounding_box[0][0]], zoom_start=6)

station_yearly_max = []
for s in station_list:
    if s["type"] is "obs": #if its an obs station
        #get the long name
        s["long_name"] =get_coops_longName(s['station_id'])
        s["station_num"] = str(s['station_id']).split(':')[-1]
        #this is different than sos name, hourly height is hourly water level
        s["data"] = coops2data(collector,s["station_num"],"high_low")    
        #verifies that there is the required amount of data at the station
        if "latitude" in s:
            if len(s["data"].keys()) >= num_years_required:                        
                popup_string = '<b>Station:</b><br>'+str(s['station_id']) + "<br><b>Long Name:</b><br>"+str(s["long_name"])
                map.simple_marker([s["latitude"],s["longitude"]],popup=popup_string)
            else:
                popup_string = '<b>Not Enough Station Data for number of years requested</b><br><br>Num requested:'+str(num_years_required)+'<br>Num Available:'+str(len(s["data"].keys()))+'<br><b>Station:</b><br>'+str(s['station_id']) + "<br><b>Long Name:</b><br>"+str(s["long_name"])
                add_invalid_marker(map,s,popup_string)
    else: #if its a model station
        if "latitude" in s:        
            popup_string = '<b>Station:</b><br>'+str(s['station_id']) + "<br><b>Long Name:</b><br>"+str(s["long_name"])
            map.simple_marker([s["latitude"],s["longitude"]],popup=popup_string)
   
# Create the map and add the bounding box line
map.line(get_coordinates(bounding_box,bounding_box_type), line_color='#FF0000', line_weight=5)
#show map of results
inline_map(map)

# <markdowncell>

# ### Creates a time series plot only showing those stations that have enough data

# <codecell>

import prettyplotlib as ppl

# Set the random seed for consistency
np.random.seed(12)

fig, ax = plt.subplots(1)

# Show the whole color range
for s in station_list:
    if "data" in s:
        years = s["data"].keys()
        #only show the stations with enough data
        if len(s["data"].keys()) >= num_years_required:  
            xx = []
            yx = []
            for y in years:    
                xx.append(int(y))
                val = s["data"][y]["max"]
                yx.append(val)  
            
            ax.scatter(xx,yx,marker='o')
            ppl.scatter(ax, xx, yx, alpha=0.8, edgecolor='black', linewidth=0.15, label=str(s["station_num"]))
            #ax.scatter(xx, yx, label=str(s["station_num"]))
    
            ppl.legend(ax, loc='right', ncol=1)
            #legend = ax.legend(loc='best')
            
            # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
            #frame  = legend.get_frame()
            
            title = s["long_name"][0] + ' water level'           
            ax.set_xlabel('Year')
            ax.set_ylabel('water level (m)')
ax.set_title("Stations exceeding "+str(num_years_required)+ " years worth of water level data (MHHW)")
fig.set_size_inches(14,8)

# <markdowncell>

# ### Number of stations available by number of years

# <codecell>

fig, ax = plt.subplots(1)
year_list_map = []
for s in station_list:
    if "data" in s:
        years = s["data"].keys()        
        year_list_map.append(len(years))
        
ppl.hist(ax,np.array(year_list_map), grid='y')
plt.plot([num_years_required, num_years_required], [0, 8], 'r-', lw=2)
ax.set_ylabel("Number of Stations")
ax.set_xlabel("Number of Years Available")
ax.set_title("Number of available stations vs available years\n(for bounding box) - red is minimum requested years")
#

# <markdowncell>

# ### Get Model Data, uses the netcdf4 library to get the model data (<b>Still in Development</b>)
# #### Obtains the model data from a given dap url, for a given location
# #### TODO: Temporal extraction based on temporal contraints

# <codecell>

#### IJ GRID READER
#use the simple grid to find the data requested
#lat_var,lon_var are pointers to the data
def find_closest_pts_ij(lat_var,lon_var,f_lat,f_lon):    
    x = lat_var[:]
    y = lon_var[:]
    dist = -1
    xidx = -1
    yidx = -1
    
    for i in range(0,len(x)):
        for j in range(0,len(y)):
            distance = Point(x[i],y[j]).distance(Point(f_lat,f_lon))
            if dist == -1:
                dist = distance
                xidx = i
                yidx = j
            elif distance < dist:
                dist = distance
                xidx = i
                yidx = j

    lat = x[xidx]
    lon = y[yidx]
    #lat lon index of point
    vals = [lat,lon,xidx,yidx]
    return vals
#### NCELL GRID READER
#use the simple grid to find the data requested
#lat_var,lon_var are pointers to the data
def find_closest_pts_ncell(map1,lat_var,lon_var,f_lat,f_lon,spacing):
    x = lat_var[::spacing]
    y = lon_var[::spacing]
    idx = get_dist(x,y,f_lat,f_lon,'#666699','#666699',map1,False)
    #find the idx that is closest        
    print spacing," :index: ",idx
    idx = idx[0]*spacing
    st_idx = idx-(2*spacing)
    ed_idx = idx+(2*spacing)
    
    x = lat_var[st_idx:ed_idx]
    y = lon_var[st_idx:ed_idx]
    ret = get_dist(x,y,f_lat,f_lon,'#00FFFF','#33CCFF',map1,False)
    lat = x[ret[0]]
    lon = y[ret[0]]
    #lat lon index of point distance between points
    vals = [lat,lon,ret[0],ret[1]]
    return vals
def get_dist(x,y,f_lat,f_lon,color1,color2,map1,show_pts):
    dist = -1
    idx = -1
    for i in range(0,len(x)):
        distance = Point(x[i],y[i]).distance(Point(f_lat,f_lon))
        if dist == -1:
            dist = distance
            idx = i
        elif distance < dist:
            dist = distance
            idx = i
        if show_pts:
            map1.circle_marker(location=[x[i], y[i]], radius=500,popup="idx:"+str(i), line_color=color2,fill_color=color1, fill_opacity=0.3)
            
      
    return [idx,dist]
#### VERIFIES THAT THE GRID IS VALID
def check_grid_is_valid(time_var,lat_var,lon_var,interest_var):
    grid_type = None
    
    # there is data with the fields of interest, now lets check the fields for validity
    valid_grid = False
    #they are both the same length
    if len(lon_var.shape) == len(lat_var.shape):
        if lon_var.shape[0] == lat_var.shape[0]:
            #both the same size
            #print "gridded data..."
            valid_grid = True
        else:
            #both different, possibly meaning i,j grid field
            #print "gridded data..."
            valid_grid = True
    else:
        print "shapes are different?...moving on..."
        valid_grid = False
        
    if valid_grid:
        #find out what the grid is structured
        if (len(interest_var.dimensions) == 2) and (interest_var.dimensions[0] == "time") and (interest_var.dimensions[1] == "node"):
            #ncell
            grid_type = "ncell"
            pass
        elif (len(interest_var.dimensions) == 3) and (interest_var.dimensions[0] == "time") and (interest_var.dimensions[1] == "lat") and (interest_var.dimensions[2] == "lon"):
            #ij 
            grid_type = "ij"
            pass
        else:
            #make sure it stays none
            grid_type =  None
        
        if grid_type is not None:
            #can be used to print some info
            #print "dims: ",interest_var.dimensions
            #print "lat: ", lat_var.shape
            #print "lon: ", lon_var.shape
            pass
            
    return grid_type    
def is_model_in_time_range(time_var):
    return True
# use only data where the standard deviation of the time series exceeds 0.01 m (1 cm)
# this eliminates flat line model time series that come from land points that 
# should have had missing values.
# min_var_value = 0.01
def data_min_value_met(min_var_value,data):
    std_value = np.std(data)
    
    if np.isinf(std_value):
        print "... value is inf"
        return False
    if np.isnan(std_value):
        print "... value is nan"
        return False
    
    if np.amax(data) < min_var_value:
        print "...max value to low"
        return False
    if np.amax(data) >999:
        print "...max value to high"
        return False
    if std_value > min_var_value:
        return True 
    else:
        print "...std value to low"
        return False
    
    return False
def get_model_data(map1,dap_urls,st_lat,st_lon,start_dt,end_dt,name_list):
    # use only data within 0.04 degrees (about 4 km)
    max_dist=0.04 
    
    min_var_value = 0.01
    
    # set the lat,lon and time fields
    lon_list =["degrees_east"]
    lat_list = ["degrees_north"]
    time_list = ["time"]
    
    model_data_store = []
    
    for url in dap_urls:
        try:
            #open the url
            nc = netCDF4.Dataset(url, 'r')

            #get the list of variables
            lon_var = None
            lat_var = None
            time_var = None
            interest_var = None
            #get the var
            var_list = nc.variables.keys()
            for var in var_list:
                v = nc.variables[var]                    
                try:                    
                    #lon
                    if (v.units in lon_list or v.long_name in lon_list) and "zonal" not in v.long_name:             
                        lon_var = v
                    #lat
                    elif (v.units in lat_list or v.long_name in lat_list) and "zonal" not in v.long_name:    
                        lat_var = v 
                    #make sure there is time in there    
                    elif v.long_name in time_list or v.standard_name in time_list:    
                        time_var = v                                             
                    #get the data of interest
                    elif v.long_name in name_list or v.standard_name in name_list:            
                        interest_var = v
                    #it was something else i dont know or care about
                    else:
                        pass
                except Exception, e:
                    #print "\t", e
                    pass
            
            #is time in range?
            if is_model_in_time_range(time_var):
                #all the variables should be set
                if (lon_var is None) and (lat_var is None) and (time_var is None) and (interest_var is None):
                    pass
                else:    
                    #check the grid is valid and of a type
                    grid_type = check_grid_is_valid(time_var,lat_var,lon_var,interest_var)
                    try:
                        if grid_type == "ncell":
                            #
                            #usually ncell grids are massive so lets slice the grid
                            #
                            print "processing the grid..."                                                        
                            spacing = 10
                            '''
                            the distance is the Euclidean Distance 
                            or Linear distance between two points on a plane 
                            and not the Great-circle distance between two points on a sphere
                            TODO convert dist to m 
                            see (http://gis.stackexchange.com/questions/80881/what-is-the-unit-the-shapely-length-attribute)
                            '''
                            # vals = lat lon index of point distance between points
                            vals = find_closest_pts_ncell(map1,lat_var,lon_var,st_lat,st_lon,spacing) 
                            
                            if vals[3] < 1:                        
                                #if the dist to the cell is small enough
                                time_vals = time_var[:]
                                data = interest_var[:,vals[2]]
                                data = np.array(data)
                                bool_a = data_min_value_met(min_var_value,data)  
                                print bool_a    
                                if bool_a: 
                                    #add a marker
                                    map1.circle_marker(location=[vals[0], vals[1]], radius=500,popup="dist:"+str(vals[3]), line_color='#33CC33',fill_color='#00FF00', fill_opacity=0.6)                                
                                    print vals
                                    print url
                                    print "distance To Station:",vals[3]
                                    print "num time values:",len(time_vals)
                                    print "units: ",interest_var.units
                                    x = np.arange(len(time_vals))                                    
                                    plt.figure()
                                    plt.plot(x, data)
                                    plt.title('Water Level');
                                    plt.xlabel('time index')
                                    plt.ylabel(interest_var.units)
                                    #set maxs
                                    plt.ylim([np.amin(data),np.amax(data)])
                                    plt.show()
                                    print "---------------------"
                                    
                            pass
                        
                        
                        
                        elif grid_type == "ij":
                            #
                            # IJ 
                            #
                            pass
                    except Exception, e:
                        print e
            else:
                print "model not in time range..."
                
                
                
        #something went wrong trying to access the grids        
        except RuntimeError, e:
            print "possible connection error for url"
            pass
        except:
            pass
        
def inline_map(map1):   
    map1._build_map()
    return HTML('<iframe srcdoc="{srcdoc}" style="width: 95%; height: 550px; border: none"></iframe>'.format(srcdoc=map1.HTML.replace('"', '&quot;')))

pt_lat = 41.501
pt_lon = -71

map1 = folium.Map(location=[pt_lat, pt_lon], zoom_start=9)

map1.simple_marker([pt_lat, pt_lon],popup="")
#EXAMPLE get model data for a station
start_time = dt.datetime(2008, 9, 10, 5, 1, 1)
end_time = dt.datetime(2008, 9, 11, 5, 1, 1)
sample_data = get_model_data(map1,dap_urls,pt_lat,pt_lon,start_time,end_time,data_dict["water"]["names"])

# <markdowncell>

# #### Show model results on a map

# <codecell>

inline_map(map1)

# <headingcell level=3>

# Extreme Value Analysis:

# <codecell>

# Show the whole color range
for s in station_list:
    if "data" in s:
        years = s["data"].keys()
        #only show the stations with enough data
        if len(s["data"].keys()) >= num_years_required:  
            xx = []
            yx = []
            for y in years:    
                xx.append(int(y))
                val = s["data"][y]["max"]
                yx.append(val)  
            
            break

# <codecell>

annual_max_levels = yx

# <headingcell level=4>

# Fit data to GEV distribution

# <codecell>

def sea_levels_gev_pdf(x):
    return genextreme.pdf(x, xi, loc=mu, scale=sigma)

# <codecell>

mle = genextreme.fit(sorted(annual_max_levels), 0)
mu = mle[1]
sigma = mle[2]
xi = mle[0]
print "The mean, sigma, and shape parameters are %s, %s, and %s, resp." % (mu, sigma, xi)

# <headingcell level=4>

# Probability Density Plot

# <codecell>

min_x = min(annual_max_levels)-0.5
max_x = max(annual_max_levels)+0.5
x = np.linspace(min_x, max_x, num=100)
y = [sea_levels_gev_pdf(z) for z in x]

fig = plt.figure(figsize=(12,6))
axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
xlabel = (s["long_name"][0] + " - Annual max water level (m)")
axes.set_title("Probability Density & Normalized Histogram")
axes.set_xlabel(xlabel)
axes.plot(x, y, color='Red')
axes.hist(annual_max_levels, bins=arange(min_x, max_x, abs((max_x-min_x)/10)), normed=1, color='Yellow')
#

# <headingcell level=4>

# Return Value Plot

# <markdowncell>

# This plot should match NOAA's [Annual Exceedance Probability Curves for station 8449130](http://tidesandcurrents.noaa.gov/est/curves.shtml?stnid=8449130)

# <codecell>

noaa_station_id = 8449130
Image(url='http://tidesandcurrents.noaa.gov/est/curves/high/'+str(noaa_station_id)+'.png')

# <codecell>

Image(url='http://tidesandcurrents.noaa.gov/est/images/color_legend.png')

# <markdowncell>

# <script type="text/javascript">
#     $('div.input').show();       
# </script>

# <codecell>

fig = plt.figure(figsize=(20,6))
axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
T=np.r_[1:250]
sT = genextreme.isf(1./T, 0, mu, sigma)
axes.semilogx(T, sT, 'r'), hold
N=np.r_[1:len(annual_max_levels)+1]; 
Nmax=max(N);
axes.plot(Nmax/N, sorted(annual_max_levels)[::-1], 'bo')
title = s["long_name"][0] 
axes.set_title(title)
axes.set_xlabel('Return Period (yrs)')
axes.set_ylabel('Meters above MHHW') 
axes.set_xticklabels([0,1,10,100,1000])
axes.set_xlim([0,260])
axes.set_ylim([0,1.8])
axes.grid(True)

# <markdowncell>

# This plot does not match exactly. NOAA's curves were calculated using the Extremes Toolkit software package in R whereas this notebook uses scipy. There is a python package based on the Extremes Toolkit called pywafo but this is experimental and isn't building properly on Mac OS X

