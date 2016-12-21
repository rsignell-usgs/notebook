# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import time
start_runtime = time.time()

# <markdowncell>

# ># IOOS System Test: [Extreme Events Theme:](https://github.com/ioos/system-test/wiki/Development-of-Test-Themes#theme-2-extreme-events) Coastal Inundation

# <markdowncell>

# ### Can we obtain observed current data at stations located within a bounding box?
# This notebook is based on IOOS System Test: Inundation

# <markdowncell>

# Methodology:
# * Define temporal and spatial bounds of interest, as well as
#   parameters of interest
# * Search for available service endpoints in the NGDC CSW catalog
#   meeting search criteria
# * Search for available OPeNDAP data endpoints
# * Obtain observation data sets from stations within the spatial
#   boundaries (from CO-OPS and NDBC)
# * Extract time series for identified stations
# * Plot time series data, current rose, annual max values per station
# * Plot observation stations on a map

# <markdowncell>

# #### import required libraries

# <codecell>

import os
import os.path
from datetime import datetime, timedelta

import uuid
import folium

import matplotlib.pyplot as plt
from owslib.csw import CatalogueServiceWeb
from owslib import fes

import numpy as np
from pandas import read_csv
from pyoos.collectors.ndbc.ndbc_sos import NdbcSos
from pyoos.collectors.coops.coops_sos import CoopsSos

from utilities import (fes_date_filter, service_urls, get_coordinates,
                       inline_map, css_styles, processStationInfo,
                       get_ncfiles_catalog, new_axes, set_legend)

css_styles()

# <markdowncell>

# <div class="warning"><strong>Temporal Bounds</strong> -
# Anything longer than one year kills the CO-OPS service</div>

# <codecell>

bounding_box_type = "box"

# Bounding Box [lon_min, lat_min, lon_max, lat_max]
area = {'Hawaii': [-160.0, 18.0, -154., 23.0],
        'Gulf of Maine': [-72.0, 41.0, -69.0, 43.0],
        'New York harbor region': [-75., 39., -71., 41.5],
        'Puerto Rico': [-71, 14, -60, 24],
        'East Coast': [-77, 34, -70, 40],
        'North West': [-130, 38, -121, 50]}

bounding_box = area['North West']

# Temporal range.
jd_now = datetime.utcnow()
jd_start,  jd_stop = jd_now - timedelta(days=(365*10)), jd_now

start_date = jd_start.strftime('%Y-%m-%d %H:00')
stop_date = jd_stop.strftime('%Y-%m-%d %H:00')

jd_start = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
jd_stop = datetime.strptime(stop_date, '%Y-%m-%d %H:%M')

print('%s to %s ' % (start_date, stop_date))

# <codecell>

# Put the names in a dict for ease of access.
data_dict = {}
sos_name = 'Currents'
data_dict['currents'] = {"names": ['currents',
                                   'surface_eastward_sea_water_velocity',
                                   '*surface_eastward_sea_water_velocity*'],
                         "sos_name": ['currents']}

# <markdowncell>

# CSW Search

# <codecell>

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw'  # NGDC Geoportal.
csw = CatalogueServiceWeb(endpoint, timeout=60)

# <markdowncell>

# Search

# <codecell>

# Convert User Input into FES filters.
start, stop = fes_date_filter(start_date, stop_date)
bbox = fes.BBox(bounding_box)

# Use the search name to create search filter.
kw = dict(propertyname='apiso:AnyText', escapeChar='\\',
          wildCard='*', singleChar='?')
or_filt = fes.Or([fes.PropertyIsLike(literal=('*%s*' % val), **kw) for
                  val in data_dict['currents']['names']])

val = 'Averages'
not_filt = fes.Not([fes.PropertyIsLike(literal=('*%s*' % val), **kw)])

filter_list = [fes.And([bbox, start, stop, or_filt, not_filt])]
# Connect to CSW, explore it's properties
# try request using multiple filters "and" syntax: [[filter1, filter2]]
csw.getrecords2(constraints=filter_list, maxrecords=1000, esn='full')
print("%s csw records found" % len(csw.records))
for rec, item in csw.records.items():
    print(item.title)

# <markdowncell>

# DAP

# <codecell>

dap_urls = service_urls(csw.records)
# Remove duplicates and organize.
dap_urls = sorted(set(dap_urls))
print("Total DAP: %s" % len(dap_urls))
# Print the first 5:
print("\n".join(dap_urls[:]))

# <markdowncell>

# Get SOS links, NDBC is not available so add it...

# <codecell>

sos_urls = service_urls(csw.records, service='sos:url')
# Remove duplicates and organize.
sos_urls = sorted(set(sos_urls))
print("Total SOS: %s" % len(sos_urls))
print("\n".join(sos_urls))

# <markdowncell>

# #### Update SOS time-date

# <codecell>

start_time = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
end_time = datetime.strptime(stop_date, '%Y-%m-%d %H:%M')
iso_start = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
iso_end = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

# <markdowncell>

# <div class="success"><strong>Get list of stations</strong>
# - we get a list of the available stations from NOAA and COOPS</div>

# <markdowncell>

# #### Initialize Station Data List

# <codecell>

st_list = {}

# <markdowncell>

# #### Get CO-OPS Station Data

# <codecell>

coops_collector = CoopsSos()
coops_collector.start_time = start_time
coops_collector.end_time = end_time
coops_collector.variables = data_dict["currents"]["sos_name"]
coops_collector.server.identification.title

ofrs = coops_collector.server.offerings

print("%s:%s" % (coops_collector.start_time, coops_collector.end_time))
print(len(ofrs))

# <markdowncell>

# #### gets a list of the active stations from coops

# <codecell>

box_str = ','.join(str(e) for e in bounding_box)

url = (('http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?'
        'service=SOS&request=GetObservation&version=1.0.0&'
        'observedProperty=%s&bin=1&'
        'offering=urn:ioos:network:NOAA.NOS.CO-OPS:CurrentsActive&'
        'featureOfInterest=BBOX:%s&responseFormat=text/csv') %
       (sos_name, box_str))

obs_loc_df = read_csv(url)

print(url)
print("Date: %s to %s" % (iso_start, iso_end))
print("Lat/Lon Box: %s" % box_str)

# <markdowncell>

# #### COOPS Station Information

# <codecell>

st_list = processStationInfo(obs_loc_df, st_list, "coops")

# <codecell>

st_list

# <markdowncell>

# #### Get NDBC Station Data

# <codecell>

ndbc_collector = NdbcSos()
ndbc_collector.start_time = start_time
ndbc_collector.end_time = end_time
ndbc_collector.variables = data_dict["currents"]["sos_name"]
ndbc_collector.server.identification.title
print("%s:%s" % (ndbc_collector.start_time, ndbc_collector.end_time))
ofrs = ndbc_collector.server.offerings
print(len(ofrs))

# <codecell>

print("Date: %s to %s" % (iso_start, iso_end))
box_str = ','.join(str(e) for e in bounding_box)
print("Lat/Lon Box: %s" % box_str)

url = (('http://sdf.ndbc.noaa.gov/sos/server.php?'
        'request=GetObservation&service=SOS&'
        'version=1.0.0&'
        'offering=urn:ioos:network:noaa.nws.ndbc:all&'
        'featureofinterest=BBOX:%s&'
        'observedproperty=%s&'
        'responseformat=text/csv&') % (box_str, sos_name))

print(url)
obs_loc_df = read_csv(url)

# <markdowncell>

# #### NDBC Station information

# <codecell>

st_list = processStationInfo(obs_loc_df, st_list, "ndbc")
st_list

# <codecell>

print(st_list[st_list.keys()[0]]['lat'])
print(st_list[st_list.keys()[0]]['lon'])

# <markdowncell>

# #### The function only support who date time differences

# <markdowncell>

# <div class="error">
# <strong>Large Temporal Requests Need To Be Broken Down</strong> -
# When requesting a large temporal range outside the SOS limit, the sos
# request needs to be broken down.  See issues in
# [ioos](https://github.com/ioos/system-test/issues/81),
# [ioos](https://github.com/ioos/system-test/issues/101),
# [ioos](https://github.com/ioos/system-test/issues/116)
# and
# [pyoos](https://github.com/ioos/pyoos/issues/35).  Unfortunately currents
# is not available via DAP
# ([ioos](https://github.com/ioos/system-test/issues/116))</div>

# <markdowncell>

# <div class="error">
# <strong>Large Temporal Requests Need To Be Broken Down</strong> -
# Obtaining long time series from COOPS via SOS is not ideal and the opendap
# links are not available, so we use the tides and currents api to get the
# currents in json format. The api response provides in default bin, unless a
# bin is specified (i.e bin=1)</div>

# <markdowncell>

# <div class="warning"><strong>Pyoos</strong> -
# Should be able to use the collector, but does not work?</div>

# <markdowncell>

# <div class="info">
# <strong>Use NDBC DAP endpoints to get time-series data</strong> -
# The DAP server for currents is available for NDBC data, we use that
# to get long time series data.</div>

# <markdowncell>

# <div class="info"><strong>Progress Information For Large Requests</strong> -
# Shows the user a progress bar for each stations as its processed.  Click
# [here]('http://www.tidesandcurrents.noaa.gov/cdata/StationList?type=Current+Data&filter=active')
# to show more information on the CO-OPS locations</div>

# <markdowncell>

# <div class="error"><strong>Processing long time series</strong> -
# The CO-OPS Server responds really slow (> 30 secs, for what should be
# a 5 sec request) to multiple requests, so getting long time series
# data is almost impossible.</div>

# <markdowncell>

# #### get CO-OPS station data

# <codecell>

# Used to define the number of days allowable by the service.
coops_point_max_days = ndbc_point_max_days = 30
print("start & end dates: %s, %s\n" % (jd_start, jd_stop))

for station_index in st_list.keys():
    # Set it so we can use it later.
    st = station_index.split(":")[-1]
    print('[%s]: %s' % (st_list[station_index]['source'], station_index))
    divid = str(uuid.uuid4())

    if st_list[station_index]['source'] == 'coops':
        # Coops fails for large requests.
        master_df = []
    elif st_list[station_index]['source'] == 'ndbc':
        # Use the dap catalog to get the data.
        master_df = get_ncfiles_catalog(station_index, jd_start, jd_stop)
    if len(master_df) > 0:
        st_list[station_index]['hasObsData'] = True
    st_list[station_index]['obsData'] = master_df

# <codecell>

# Check theres data in there.
st_list[st_list.keys()[2]]

# <markdowncell>

# ### Plot the pandas data frames for the stations

# <markdowncell>

# <div class="error"><strong>Station Data Plot</strong> -
# There might be an issue with some of the NDBC station data...</div>

# <codecell>

for station_index in st_list.keys():
    df = st_list[station_index]['obsData']
    if len(df) > 1:
        st_list[station_index]['hasObsData'] = True
        print("num rows: %s" % len(df))
        fig = plt.figure(figsize=(18, 3))
        plt.scatter(df.index, df['sea_water_speed (cm/s)'])
        fig.suptitle('Station:'+station_index, fontsize=20)
        plt.xlabel('Date', fontsize=18)
        plt.ylabel('sea_water_speed (cm/s)', fontsize=16)
    else:
        st_list[station_index]['hasObsData'] = False

# <markdowncell>

# #### Find the min and max data values

# <markdowncell>

# <div class="warning"><strong>Station Data Plot</strong> -
# Some stations might not plot due to the data.</div>

# <codecell>

# Build current roses.
filelist = [f for f in os.listdir("./images") if f.endswith(".png")]
for f in filelist:
    os.remove("./images/{}".format(f))

station_min_max = {}
for station_index in st_list.keys():
    all_spd_data = {}
    all_dir_data = {}
    all_time_spd = []
    all_time_dir = []
    df = st_list[station_index]['obsData']
    if len(df) > 1:
        try:
            spd_data = df['sea_water_speed (cm/s)'].values
            spd_data = np.array(spd_data)

            dir_data = df['direction_of_sea_water_velocity (degree)'].values
            dir_data = np.array(dir_data)

            time_data = df.index.tolist()
            time_data = np.array(time_data)

            # NOTE: This data cleanup can a vectorized function.
            for idx in range(0, len(spd_data)):
                if spd_data[idx] > 998:
                    continue
                elif np.isnan(spd_data[idx]):
                    continue
                elif dir_data[idx] == 0:
                    continue
                else:
                    dt_year = time_data[idx].year
                    dt_year = str(dt_year)
                    if dt_year not in all_spd_data.keys():
                        all_spd_data[dt_year] = []
                        all_dir_data[dt_year] = []
                    # Convert to knots.
                    knot_val = (spd_data[idx] * 0.0194384449)
                    knot_val = "%.4f" % knot_val
                    knot_val = float(knot_val)

                    all_spd_data[dt_year].append(knot_val)
                    all_dir_data[dt_year].append(dir_data[idx])

                    all_time_spd.append(knot_val)
                    all_time_dir.append(dir_data[idx])

            all_time_spd = np.array(all_time_spd, dtype=np.float)
            all_time_dir = np.array(all_time_dir, dtype=np.float)

            station_min_max[station_index] = {}
            for year in all_spd_data.keys():
                year_spd = np.array(all_spd_data[year])
                year_dir = np.array(all_dir_data[year])
                station_min_max[station_index][year] = {}
                station_min_max[station_index][year]['pts'] = len(year_spd)
                min_spd, max_spd = np.min(year_spd), np.max(year_spd)
                station_min_max[station_index][year]['spd_min'] = min_spd
                station_min_max[station_index][year]['spd_max'] = max_spd
                dir_min, dir_max = np.argmin(year_spd), np.argmax(year_spd)
                yr_dir_min, yr_dir_max = year_dir[dir_min], year_dir[dir_max]
                station_min_max[station_index][year]['dir_at_min'] = yr_dir_min
                station_min_max[station_index][year]['dir_at_max'] = yr_dir_max
            try:
                # A stacked histogram with normed
                # (displayed in percent) results.
                ax = new_axes()
                ax.set_title(station_index.split(":")[-1] +
                             " stacked histogram with normed (displayed in %)"
                             "\nresults (spd in knots), All Time.")
                ax.bar(all_time_dir, all_time_spd, normed=True,
                       opening=0.8, edgecolor='white')
                set_legend(ax)

                fig = plt.gcf()
                fig.set_size_inches(8, 8)
                fname = './images/%s.png' % station_index.split(":")[-1]
                fig.savefig(fname, dpi=100)
            except Exception as e:
                print("Error when plotting %s" % e)
                pass

        except Exception as e:  # Be specific here!
            print("Error: %s" % e)
            pass

# <codecell>

# Plot the min and max from each station.
fields = ['spd_']

for idx in range(0, len(fields)):
    d_field = fields[idx]
    fig, ax = plt.subplots(1, 1, figsize=(18, 5))
    for st in station_min_max:
        x, y_min, y_max = [], [], []
        for year in station_min_max[st]:
            x.append(year)
            y_max.append(station_min_max[st][year][d_field+'max'])
        marker_size = station_min_max[st][year]['pts'] / 80
        marker_size += 20
        station_label = st.split(":")[-1]

        ax.scatter(np.array(x), np.array(y_max),
                   label=station_label, s=marker_size,
                   c=np.random.rand(3, 1), marker="o")
        ax.set_xlim([2000, 2015])
        ax.set_title("Yearly Max Speed Per Station, Marker Scaled Per "
                     "Annual Pts (bigger = more pts per year)")
        ax.set_ylabel("speed (knots)")
        ax.set_xlabel("Year")
        ax.legend(loc='upper left')

# <markdowncell>

# #### Produce Interactive Map

# <codecell>

station = st_list[st_list.keys()[0]]
m = folium.Map(location=[station["lat"], station["lon"]], zoom_start=4)
m.line(get_coordinates(bounding_box, bounding_box_type),
       line_color='#FF0000', line_weight=5)

# Plot the obs station.
for st in st_list:
    hasObs = st_list[st]['hasObsData']
    if hasObs:
        fname = './images/%s.png' % st.split(":")[-1]
        if os.path.isfile(fname):
            popup = ('Obs Location:<br>%s<br><img border=120 src="'
                     './images/%s.png" width="242" height="242">' %
                     (st, st.split(":")[-1]))
            m.simple_marker([st_list[st]["lat"], st_list[st]["lon"]],
                            popup=popup,
                            marker_color="green",
                            marker_icon="ok")
        else:
            popup = 'Obs Location:<br>%s' % st
            m.simple_marker([st_list[st]["lat"], st_list[st]["lon"]],
                            popup=popup,
                            marker_color="green",
                            marker_icon="ok")
    else:
        popup = 'Obs Location:<br>%s' % st
        m.simple_marker([st_list[st]["lat"], st_list[st]["lon"]],
                        popup=popup,
                        marker_color="red",
                        marker_icon="remove")
inline_map(m)

# <codecell>

elapsed = time.time() - start_runtime
print('{:.2f} minutes'.format(elapsed / 60.))

