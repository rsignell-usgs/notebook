"""
Utility functions for Scenario_A_Extreme_Currents.ipynb
"""

import fnmatch
import lxml.html
from urllib import urlopen

from windrose import WindroseAxes

# Scientific stack.
import matplotlib.pyplot as plt
from owslib import fes
from pandas import DataFrame
from IPython.display import HTML
from netCDF4 import MFDataset, date2index, num2date


def fes_date_filter(start_date='1900-01-01', stop_date='2100-01-01',
                    constraint='overlaps'):
    """Hopefully something like this will be implemented in fes soon."""
    if constraint == 'overlaps':
        propertyname = 'apiso:TempExtent_begin'
        start = fes.PropertyIsLessThanOrEqualTo(propertyname=propertyname,
                                                literal=stop_date)
        propertyname = 'apiso:TempExtent_end'
        stop = fes.PropertyIsGreaterThanOrEqualTo(propertyname=propertyname,
                                                  literal=start_date)
    elif constraint == 'within':
        propertyname = 'apiso:TempExtent_begin'
        start = fes.PropertyIsGreaterThanOrEqualTo(propertyname=propertyname,
                                                   literal=start_date)
        propertyname = 'apiso:TempExtent_end'
        stop = fes.PropertyIsLessThanOrEqualTo(propertyname=propertyname,
                                               literal=stop_date)
    return start, stop


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
    return urls


def get_coordinates(bounding_box, bounding_box_type=''):
    """Create bounding box coordinates for the map."""
    coordinates = []
    if bounding_box_type == "box":
        coordinates.append([bounding_box[1], bounding_box[0]])
        coordinates.append([bounding_box[1], bounding_box[2]])
        coordinates.append([bounding_box[3], bounding_box[2]])
        coordinates.append([bounding_box[3], bounding_box[0]])
        coordinates.append([bounding_box[1], bounding_box[0]])
    return coordinates


def inline_map(m):
    """From http://nbviewer.ipython.org/gist/rsignell-usgs/
    bea6c0fe00a7d6e3249c."""
    m._build_map()
    srcdoc = m.HTML.replace('"', '&quot;')
    embed = HTML('<iframe srcdoc="{srcdoc}" '
                 'style="width: 100%; height: 500px; '
                 'border: none"></iframe>'.format(srcdoc=srcdoc))
    return embed


def css_styles():
    return HTML("""
        <style>
        .info {
            background-color: #fcf8e3; border-color: #faebcc;
                border-left: 5px solid #8a6d3b; padding: 0.5em; color: #8a6d3b;
        }
        .success {
            background-color: #d9edf7; border-color: #bce8f1;
                border-left: 5px solid #31708f; padding: 0.5em; color: #31708f;
        }
        .error {
            background-color: #f2dede; border-color: #ebccd1;
                border-left: 5px solid #a94442; padding: 0.5em; color: #a94442;
        }
        .warning {
            background-color: #fcf8e3; border-color: #faebcc;
                border-left: 5px solid #8a6d3b; padding: 0.5em; color: #8a6d3b;
        }
        </style>
    """)


def processStationInfo(obs_loc_df, st_list, source):
    st_data = obs_loc_df['station_id']
    lat_data = obs_loc_df['latitude (degree)']
    lon_data = obs_loc_df['longitude (degree)']
    for k in range(0, len(st_data)):
        station_name = st_data[k]
        if station_name in st_list:
            pass
        else:
            st_list[station_name] = {}
            st_list[station_name]["lat"] = lat_data[k]
            st_list[station_name]["source"] = source
            st_list[station_name]["lon"] = lon_data[k]
            print(station_name)
    print("number of stations in bbox %s" % len(st_list.keys()))
    return st_list


def get_ncfiles_catalog(station_id, jd_start, jd_stop):
    station_name = station_id.split(":")[-1]
    uri = 'http://dods.ndbc.noaa.gov/thredds/dodsC/data/adcp'
    url = ('%s/%s/' % (uri, station_name))
    urls = _url_lister(url)
    filetype = "*.nc"
    file_list = [filename for filename in fnmatch.filter(urls, filetype)]
    files = [fname.split('/')[-1] for fname in file_list]
    urls = ['%s/%s/%s' % (uri, station_name, fname) for fname in files]

    nc = MFDataset(urls)

    time_dim = nc.variables['time']
    calendar = 'gregorian'
    idx_start = date2index(jd_start, time_dim, calendar=calendar,
                           select='nearest')
    idx_stop = date2index(jd_stop, time_dim, calendar=calendar,
                          select='nearest')

    dir_dim = nc.variables['water_dir'][idx_start:idx_stop, ...].squeeze()
    speed_dim = nc.variables['water_spd'][idx_start:idx_stop, ...].squeeze()
    if dir_dim.ndim != 1:
        dir_dim = dir_dim[:, 0]
        speed_dim = speed_dim[:, 0]
    time_dim = nc.variables['time']
    dates = num2date(time_dim[idx_start:idx_stop],
                     units=time_dim.units,
                     calendar='gregorian').squeeze()
    data = dict()
    data['sea_water_speed (cm/s)'] = speed_dim
    col = 'direction_of_sea_water_velocity (degree)'
    data[col] = dir_dim
    time = dates
    columns = ['sea_water_speed (cm/s)',
               'direction_of_sea_water_velocity (degree)']
    df = DataFrame(data=data, index=time, columns=columns)
    return df


def new_axes():
    fig = plt.figure(figsize=(8, 8), dpi=80, facecolor='w', edgecolor='w')
    rect = [0.1, 0.1, 0.8, 0.8]
    ax = WindroseAxes(fig, rect, axisbg='w')
    fig.add_axes(ax)
    return ax


def set_legend(ax):
    """Adjust the legend box."""
    l = ax.legend()
    plt.setp(l.get_texts(), fontsize=8)


def _url_lister(url):
    urls = []
    connection = urlopen(url)
    dom = lxml.html.fromstring(connection.read())
    for link in dom.xpath('//a/@href'):
        urls.append(link)
    return urls
