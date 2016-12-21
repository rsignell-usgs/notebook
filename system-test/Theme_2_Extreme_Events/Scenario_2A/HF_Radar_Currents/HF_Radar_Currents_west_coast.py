# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# ># IOOS System Test: [HF Radar](https://github.com/ioos/system-test/wiki/Development-of-Test-Themes) Coastal Inundation

# <markdowncell>

# ### Can we obtain HF radar current data at stations located within a bounding box?
# This notebook is based on IOOS System Test: Inundation

# <markdowncell>

# Methodology:
# 
# * Define temporal and spatial bounds of interest, as well as parameters of interest
# * Search for available OPeNDAP data endpoints
# * Obtain observation data sets from stations within the spatial boundaries from DAP endpoints
# * Extract time series for locations
# * Plot time series data, current rose, annual max values per station
# * Plot observation stations on a map 

# <codecell>

import datetime as dt
from warnings import warn

import os
import os.path

import iris
from iris.exceptions import CoordinateNotFoundError, ConstraintMismatchError

import netCDF4
from netCDF4 import num2date, date2num

import uuid
import folium
from IPython.display import HTML, Javascript, display

import matplotlib.pyplot as plt
from owslib.csw import CatalogueServiceWeb
from owslib import fes


from shapely.geometry import Point
import numpy as np
import pandas as pd
from pyoos.collectors.ndbc.ndbc_sos import NdbcSos
from pyoos.collectors.coops.coops_sos import CoopsSos
import requests

from utilities import (date_range, coops2df, coops2data, find_timevar, find_ij, nearxy, service_urls, mod_df, 
                       get_coordinates, get_Coops_longName, inline_map, get_coops_sensor_name,css_styles)

import cStringIO
from lxml import etree
import urllib2
import time as ttime
from io import BytesIO

from shapely.geometry import LineString
from shapely.geometry import Point


css_styles()

# <markdowncell>

# <div class="warning"><strong>Temporal Bounds</strong> - Anything longer than one year kills the CO-OPS service</div>

# <codecell>

bounding_box_type = "box" 

# Bounding Box [lon_min, lat_min, lon_max, lat_max]
area = {'Hawaii': [-160.0, 18.0, -154., 23.0],
        'Gulf of Maine': [-72.0, 41.0, -69.0, 43.0],
        'New York harbor region': [-75., 39., -71., 41.5],
        'Puerto Rico': [-71, 14, -60, 24],
        'East Coast': [-77, 34, -70, 40],
        'North West': [-130, 38, -121, 50],
        'West': [-132, 30, -105, 47]
        }

bounding_box = area['West']

#temporal range
jd_now = dt.datetime.utcnow()
jd_start,  jd_stop = jd_now - dt.timedelta(days=(7)), jd_now

start_date = jd_start.strftime('%Y-%m-%d %H:00')
stop_date = jd_stop.strftime('%Y-%m-%d %H:00')

jd_start = dt.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
jd_stop = dt.datetime.strptime(stop_date, '%Y-%m-%d %H:%M')
print start_date,'to',stop_date

# <codecell>

#put the names in a dict for ease of access 
data_dict = {}
sos_name = 'Currents'
data_dict['currents'] = {"names":['currents',
                                  'surface_eastward_sea_water_velocity',
                                  '*surface_eastward_sea_water_velocity*'], 
                         "sos_name":['currents']}  

# <codecell>

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw' # NGDC Geoportal
csw = CatalogueServiceWeb(endpoint,timeout=60)

# <codecell>

# convert User Input into FES filters
start,stop = date_range(start_date,stop_date)
bbox = fes.BBox(bounding_box)

#use the search name to create search filter
or_filt = fes.Or([fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                    escapeChar='\\',wildCard='*',singleChar='?') for val in data_dict['currents']['names']])

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

# <codecell>

dap_urls = service_urls(csw.records)
#remove duplicates and organize
dap_urls = sorted(set(dap_urls))
print "Total DAP:",len(dap_urls)
#print the first 5...
print "\n".join(dap_urls[:])

# <codecell>

sos_urls = service_urls(csw.records,service='sos:url')
#remove duplicates and organize
sos_urls = sorted(set(sos_urls))
print "Total SOS:",len(sos_urls)
print "\n".join(sos_urls)

# <codecell>

start_time = dt.datetime.strptime(start_date,'%Y-%m-%d %H:%M')
end_time = dt.datetime.strptime(stop_date,'%Y-%m-%d %H:%M')
iso_start = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
iso_end = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

# <markdowncell>

# ### reset the station list

# <codecell>

st_list = {}

# <codecell>

def processStationInfo(obs_loc_df,st_list,source):
    st_data = obs_loc_df['station_id']
    lat_data = obs_loc_df['latitude (degree)']
    lon_data = obs_loc_df['longitude (degree)']

    for i in range(0,len(st_data)):
        station_name = st_data[i]
        if station_name in st_list:
            pass
        else:
            st_list[station_name] = {}
            st_list[station_name]["lat"] = lat_data[i]
            st_list[station_name]["source"] = source
            st_list[station_name]["lon"] = lon_data[i]
            print station_name

    print "number of stations in bbox",len(st_list.keys())
    return st_list

# <markdowncell>

# #COOPS Station Locations

# <codecell>

coops_collector = CoopsSos()
coops_collector.start_time = start_time
coops_collector.end_time = end_time
coops_collector.variables = data_dict["currents"]["sos_name"]
coops_collector.server.identification.title
print coops_collector.start_time,":", coops_collector.end_time
ofrs = coops_collector.server.offerings
print(len(ofrs))

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

st_list = processStationInfo(obs_loc_df,st_list,"coops")

# <markdowncell>

# #NDBC Station Locations

# <codecell>

ndbc_collector = NdbcSos()
ndbc_collector.start_time = start_time
ndbc_collector.end_time = end_time
ndbc_collector.variables = data_dict["currents"]["sos_name"]
ndbc_collector.server.identification.title
print ndbc_collector.start_time,":", ndbc_collector.end_time
ofrs = ndbc_collector.server.offerings
print(len(ofrs))

# <codecell>

print "Date: ",iso_start," to ", iso_end
box_str=','.join(str(e) for e in bounding_box)
print "Lat/Lon Box: ",box_str

url = (('http://sdf.ndbc.noaa.gov/sos/server.php?'
       'request=GetObservation&service=SOS&'
       'version=1.0.0&'
       'offering=urn:ioos:network:noaa.nws.ndbc:all&'
       'featureofinterest=BBOX:%s&'
       'observedproperty=%s&'
       'responseformat=text/csv&')% (box_str,sos_name))


print url
obs_loc_df = pd.read_csv(url)
st_list = processStationInfo(obs_loc_df,st_list,"ndbc")

# <codecell>

print st_list

# <codecell>

def coopsCurrentRequest(station_id,tides_dt_start,tides_dt_end):
    tides_data_options = "time_zone=gmt&application=ports_screen&format=json"
    tides_url = "http://tidesandcurrents.noaa.gov/api/datagetter?"   
    begin_datetime = "begin_date="+tides_dt_start
    end_datetime = "&end_date="+tides_dt_end
    current_dp = "&station="+station_id
    full_url = tides_url+begin_datetime+end_datetime+current_dp+"&application=web_services&product=currents&units=english&"+tides_data_options
    r = requests.get(full_url)
    try:
        r= r.json()
    except:
        return None
    if 'data' in r:
        r = r['data']
        data_dt = []
        data_spd = []
        data_dir = []
        for row in r:            
            data_spd.append(float(row['s']))
            data_dir.append(float(row['d']))            
            date_time_val = dt.datetime.strptime(row['t'], '%Y-%m-%d %H:%M')
            data_dt.append(date_time_val)
            
        data = {}
        data['sea_water_speed (cm/s)'] = np.array(data_spd)
        data['direction_of_sea_water_velocity (degree)'] = np.array(data_dir)
        time = np.array(data_dt)
        
        df = pd.DataFrame(data=data,index=time,columns = ['sea_water_speed (cm/s)','direction_of_sea_water_velocity (degree)'] )    
        return df
    else:
        return None

# <markdowncell>

# ### DAP does not have the most recent

# <codecell>

def ndbcCurrentRequest(station_id,dt_start,dt_end):
    
    year_max = {}
    
    main_df = pd.DataFrame()
    for year in range(dt_start.year,(dt_end.year+1)):
        try:
            station_name = station_id.split(":")[-1]
            url = 'http://dods.ndbc.noaa.gov/thredds/dodsC/data/adcp/'+station_name+'/'+station_name+'a'+str(year)+'.nc'
            
            nc = netCDF4.Dataset(url, 'r')  
            #zero depth is the shallowist
            depth_dim = nc.variables['depth'][:]
            
            dir_dim = nc.variables['water_dir'][:]
            speed_dim = nc.variables['water_spd'][:]
            time_dim = nc.variables['time']
            
            data_dt = []
            
            data_spd = []
            data_dir = []
            for i in range(0,len(speed_dim)):
                data_spd.append(speed_dim[i][0][0][0])
                data_dir.append(dir_dim[i][0][0][0])
            
            dates = num2date(time_dim[:],units=time_dim.units,calendar='gregorian')
                
            data = {}
            data['sea_water_speed (cm/s)'] = np.array(data_spd)
            data['direction_of_sea_water_velocity (degree)'] = np.array(data_dir)
            time = np.array(dates)

            df = pd.DataFrame(data=data,index=time,columns = ['sea_water_speed (cm/s)','direction_of_sea_water_velocity (degree)'] )    
            main_df = main_df.append(df)            
        except Exception,e:
            print "no data for",station_name,year,"found:",e   
    
    return main_df

# <codecell>

print "Date: ",iso_start," to ", iso_end
date_range_string = iso_start+"/"+iso_end
#i.e date range    2011-03-01T00:00Z/2011-03-02T00:00Z
def ndbcSOSRequest(station,date_range):
    
    url = ('http://sdf.ndbc.noaa.gov/sos/server.php?'
     'request=GetObservation&service=SOS&version=1.0.0'
     '&offering=%s&'
     'observedproperty=Currents&responseformat=text/csv'
     '&eventtime=%s') % (station,date_range)

    obs_loc_df = pd.read_csv(url)
    return obs_loc_df

# <codecell>

divid = str(uuid.uuid4())
pb = HTML(
"""
<div style="border: 1px solid black; width:500px">
  <div id="%s" style="background-color:blue; width:0%%">&nbsp;</div>
</div> 
""" % divid)
display(pb) 

count = 0
for station_index in st_list.keys(): 
        
    st =  station_index.split(":")[-1]
    tides_dt_start = jd_start.strftime('%Y%m%d %H:%M')
    tides_dt_end = jd_stop.strftime('%Y%m%d %H:%M')
    
    if st_list[station_index]['source'] == "coops":
        df = coopsCurrentRequest(st,tides_dt_start,tides_dt_end)
    elif st_list[station_index]['source'] == "ndbc":
        df = ndbcSOSRequest(station_index,date_range_string)
        #DAP request
        #df = ndbcCurrentRequest(st,jd_start,jd_stop)
    
    if (df is not None) and (len(df)>0):
        st_list[station_index]['hasObsData'] = True
    else:
        st_list[station_index]['hasObsData'] = False
    st_list[station_index]['obsData'] = df
    
    
    print station_index, st_list[station_index]['source'],st_list[station_index]['hasObsData']
    
    count+=1
    percent_compelte = (float(count)/float(len(st_list.keys())))*100
    display(Javascript("$('div#%s').width('%i%%')" % (divid, int(percent_compelte))))
    

# <codecell>

#find the closest point, distance in degrees (coordinates of the points in degrees)        
def find_nearest(obs_lat,obs_lon, lats,lons):    
    point1 = Point(obs_lon,obs_lat)
    dist = 999999999
    index_i = -1
    index_j = -1    
    for i in range(0,len(lats)):
        for j in range(0,len(lons)):
            point2 = Point(lons[j], lats[i])
            val = point1.distance(point2)
            if val < dist:
                index_i = i
                index_j = j
                dist = val    
    return [index_i,index_j,dist]

# <codecell>

def uv2ws(u,v):
    return np.sqrt(np.square(u)+np.square(v))
 
def uv2wd(u,v):
    '''
    NOTE: this is direction TOWARDS. u/v are mathematical vectors so direction is where they are pointing
    NOTE: arctan2(u,v) automatically handles the 90 degree rotation so North is zero, arctan2(v,u), mathematical version, has 0 at east
    '''
    wd = np.degrees(np.arctan2(u,v))
    return np.where(wd >= 0, wd, wd+360)
 
def uv2wdws(u,v):
    return zip(uv2wd(u,v),uv2ws(u,v))

# <codecell>

#directly access the dap endpoint to get data
def get_hr_radar_dap_data(dap_urls,st_list,jd_start,  jd_stop):
    # Use only data within 1.00 degrees
    obs_df = []
    obs_or_model = False
    max_dist = 1.0
    # Use only data where the standard deviation of the time series exceeds 0.01 m (1 cm).
    # This eliminates flat line model time series that come from land points that should have had missing values.
    min_var = 0.1
    data_idx = []
    
    df_list = []
    for url in dap_urls:         
        #only look at 6km hf radar
        if 'http://hfrnet.ucsd.edu/thredds/dodsC/HFRNet/USWC/' in url and "6km" in url and "GNOME" in url:                                  
            print url
            #get url
            nc = netCDF4.Dataset(url, 'r')
            lat_dim = nc.variables['lat']  
            lon_dim = nc.variables['lon']  
            time_dim = nc.variables['time']
            u_var = None
            v_var = None
            for key in nc.variables.iterkeys():
                 key_dim = nc.variables[key]  
                 try:
                    if key_dim.standard_name == "surface_eastward_sea_water_velocity":
                        u_var = key_dim 
                    elif key_dim.standard_name == "surface_northward_sea_water_velocity":                        
                        v_var = key_dim                        
                    elif key_dim.standard_name == "time":
                        time = key_dim                        
                 except:
                    #only if the standard name is not available
                    pass
                
            #manage dates            
            dates = num2date(time_dim[:],units=time_dim.units,calendar='gregorian')
            date_idx = []
            date_list = []
            for i, date in enumerate(dates):
                if jd_start < date < jd_stop:
                    date_idx.append(i)                        
                    date_list.append(date)
            #manage location
            for st in st_list:
                station = st_list[st]
                f_lat = station['lat']
                f_lon = station['lon']
                
                ret = find_nearest(f_lat,f_lon, lat_dim[:],lon_dim[:])
                lat_idx = ret[0]
                lon_idx = ret[1]
                dist_deg = ret[2]
                print "lat,lon,dist=",ret
                
                if len(u_var.dimensions) == 3:
                    #3dimensions
                    u = u_var[date_idx,lat_idx,lon_idx]
                    v = v_var[date_idx,lat_idx,lon_idx]
                    pass                
                elif len(u_var.dimensions) == 4:    
                    #4dimensions, usually level
                    u = u_var[date_idx,0,lat_idx,lon_idx]                    
                    v = v_var[date_idx,0,lat_idx,lon_idx]  
                    pass                          
                try:
                    
                    print "\t",type(u)
                    
                    try:
                        #try and get the data using a filled array
                        u_vals = u.filled(np.nan)
                        v_vals = v.filled(np.nan)
                        if u_var.units == "m s-1":                                                    
                            #converts m to cm
                            u_vals = (u_vals)*100.
                            v_vals = (v_vals)*100.
                    except:    
                        pass
                                                            
                    print "units",u_var.units                         
                    

                    #turn vectors in the speed and direction
                    ws = uv2ws(u_vals,v_vals) 
                    wd = uv2wd(u_vals,v_vals) 

                    data_spd = []
                    data_dir = []
                    data = {}
                    data['sea_water_speed (cm/s)'] = np.array(ws)
                    data['direction_of_sea_water_velocity (degree)'] = np.array(wd)
                    time = np.array(date_list)
                
                    df = pd.DataFrame(data=data,index=time,columns = ['sea_water_speed (cm/s)','direction_of_sea_water_velocity (degree)'] )    
                    df_list.append({"name":st,
                                    "data":df,
                                    "lat":lat_dim[lat_idx],
                                    "lon":lon_dim[lon_idx],
                                   "ws_pts":np.count_nonzero(~np.isnan(ws)),
                                   "wd_pts":np.count_nonzero(~np.isnan(wd)),
                                   "dist":dist_deg,
                                   'from':url
                                   })
                except Exception,e:
                    print "\t\terror:",e                       
        else:
            pass
        
    return df_list     

# <codecell>

df_list = get_hr_radar_dap_data(dap_urls,st_list,jd_start,  jd_stop)

# <codecell>

for station_index in st_list.keys():
    df = st_list[station_index]['obsData']  
    if st_list[station_index]['hasObsData']:
        
        fig = plt.figure(figsize=(18, 3))
        plt.plot(df.index, df['sea_water_speed (cm/s)'])
        fig.suptitle('Station:'+station_index, fontsize=14)
        plt.xlabel('Date', fontsize=18)
        plt.ylabel('sea_water_speed (cm/s)', fontsize=16)      
        
# post those stations not already added        
for ent in df_list:  

    if ent['ws_pts'] >4:      
        df = ent['data']   
        fig = plt.figure(figsize=(18, 3))
        plt.plot(df.index, df['sea_water_speed (cm/s)'])
        fig.suptitle('HF Radar:'+ " lat:"+str(ent["lat"])+" lon:"+str(ent["lon"]), fontsize=14)
        plt.xlabel('Date', fontsize=18)
        plt.ylabel('sea_water_speed (cm/s)', fontsize=16)  
        ent['valid'] = True     

# <codecell>

#add map title
htmlContent = ('<p><h4>Station Map: Red circles have no obs data, Green is coops, Dark Blue is ndbc, Purple is HR Radar locations</h4></p>') 
station =  st_list[st_list.keys()[0]]
map = folium.Map(location=[station["lat"], station["lon"]], zoom_start=4)
map.line(get_coordinates(bounding_box, bounding_box_type), line_color='#FF0000', line_weight=5)

#plot the obs station, 
for st in st_list:  
    lat = st_list[st]['lat']
    lon = st_list[st]['lon']
    
    popupString = '<b>Obs Location:</b><br>'+st+'<br><b>Source:</b><br>'+st_list[st]['source']
    
    if st_list[st]['hasObsData'] == False:
        map.circle_marker([lat,lon], popup=popupString, 
                          radius=1000,
                          line_color='#FF0000',
                          fill_color='#FF0000', 
                          fill_opacity=0.2)
        
    elif st_list[st]['source'] == "coops":
        map.simple_marker([lat,lon], popup=popupString,marker_color="green",marker_icon="star")
    elif st_list[st]['source'] == "ndbc":
        map.simple_marker([lat,lon], popup=popupString,marker_color="darkblue",marker_icon="star")

for ent in df_list:
    if 'valid' in ent:
        if ent['valid'] == True:       
            lat = ent['lat']
            lon = ent['lon']
            popupstring = "HF Radar: ["+ str(lat)+":"+str(lon)+"]" + "<br>for<br>" + ent['name']
            map.circle_marker([lat,lon], popup=popupstring, 
                              radius=1000,
                              line_color='#FF00FF',
                              fill_color='#FF00FF', 
                              fill_opacity=0.5)
                          
display(HTML(htmlContent))

## adds the HF radar tile layers
map.add_tile_layer(tile_name='hfradar 6km',
                   tile_url='http://hfradar.ndbc.noaa.gov/tilesavg.php?s=10&e=100&x={x}&y={y}&z={z}&t=2014-8-21 17:00:00&rez=6')
map.add_tile_layer(tile_name='hfradar 2km',
                   tile_url='http://hfradar.ndbc.noaa.gov/tilesavg.php?s=10&e=100&x={x}&y={y}&z={z}&t=2014-8-21 17:00:00&rez=2')
map.add_tile_layer(tile_name='hfradar 1km',
                   tile_url='http://hfradar.ndbc.noaa.gov/tilesavg.php?s=10&e=100&x={x}&y={y}&z={z}&t=2014-8-21 17:00:00&rez=1')
map.add_tile_layer(tile_name='hfradar 500m',
                   tile_url='http://hfradar.ndbc.noaa.gov/tilesavg.php?s=10&e=100&x={x}&y={y}&z={z}&t=2014-8-21 17:00:00&rez=0.5')


map.add_layers_to_map()

inline_map(map)  

# <codecell>


# <codecell>


