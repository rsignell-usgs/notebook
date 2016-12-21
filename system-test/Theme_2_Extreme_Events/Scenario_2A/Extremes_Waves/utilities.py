"""
Utility functions for Scenario_2A_Waves.ipynb
"""

from lxml import etree
from io import BytesIO
import datetime as dt
import calendar # used to get number of days in a month and year
from warnings import warn
try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

# Scientific stack.
import numpy as np
from IPython.display import HTML
import pandas as pd
# Custom IOOS/ASA modules (available at PyPI).
from owslib import fes
from owslib.ows import ExceptionReport


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


def get_station_longName(station):
    """Get longName for specific station using DescribeSensor
    request."""

    url = ('http://sdf.ndbc.noaa.gov/sos/server.php?service=SOS&'
           'request=DescribeSensor&version=1.0.0&outputFormat=text/xml;subtype="sensorML/1.0.1"&'
           'procedure=urn:ioos:station:wmo:%s') % station
    tree = etree.parse(urlopen(url))
    root = tree.getroot()
    namespaces = {'sml': "http://www.opengis.net/sensorML/1.0.1"}
    longName = root.xpath("//sml:identifier[@name='longName']/sml:Term/sml:value/text()", namespaces=namespaces)
    if len(longName) == 0:
        longName = station
        return longName
    else:
        return longName[0]


def get_station_data(collector, station_id, sos_name, field_of_interest):
    """
    This function breaks up the SOS requests into one month chunks and
    returns all of the data in a Pandas DataFrame
    """

    collector.features = [station_id]
    collector.variables = [sos_name]
    #loop through the years and get the data needed
    st_yr = int(collector.start_time.year)
    ed_yr = int(collector.end_time.year+1)

    yearly_df = []
    # Only 31 days are allowed to be requested at once
    for year_station in range(st_yr, ed_yr):
        print 'Processing ' + str(year_station) + ' now...'
        obs_df = pd.DataFrame()
        for month in range(1, 13):
            num_days = calendar.monthrange(year_station, month)[1]

            st = dt.datetime(year_station, month, 1, 0, 0, 0)
            ed = dt.datetime(year_station, month, num_days, 23, 59, 59)

            start_time1 = dt.datetime.strptime(str(st), '%Y-%m-%d %H:%M:%S')
            end_time1 = dt.datetime.strptime(str(ed), '%Y-%m-%d %H:%M:%S')

            collector.start_time = start_time1
            collector.end_time = end_time1

            try:
                response = collector.raw(responseFormat="text/csv")
                #get the response then get the data
                data_df = pd.read_csv(BytesIO(response.encode('utf-8')),
                                      parse_dates=True,
                                      index_col='date_time')
                # Eliminate any data with NaN.
                # data_df['date_time'] = data_df.Time.map(lambda x: pd.datetools.parse(x).time())
                # data_df = data_df[np.isfinite(data_df[field_of_interest])]
                if obs_df.empty:
                    obs_df = data_df[field_of_interest]
                else:
                    obs_df = pd.concat([obs_df, data_df[field_of_interest]])
            except Exception as e:
                print str(e)
        if not obs_df.empty:
            yearly_df.append(obs_df)
        else:
            print '\t No Data'

    return yearly_df


def mod_df(arr, timevar, istart, istop, mod_name, ts):
    """Return time series (DataFrame) from model interpolated onto uniform time
    base."""
    t = timevar.points[istart:istop]
    jd = timevar.units.num2date(t)

    # Eliminate any data that is closer together than 10 seconds this was
    # required to handle issues with CO-OPS aggregations, I think because they
    # use floating point time in hours, which is not very accurate, so the
    # FMRC aggregation is aggregating points that actually occur at the same
    # time.
    dt = np.diff(jd)
    s = np.array([ele.seconds for ele in dt])
    ind = np.where(s > 10)[0]
    arr = arr[ind+1]
    jd = jd[ind+1]

    b = pd.DataFrame(arr, index=jd, columns=[mod_name])
    # Eliminate any data with NaN.
    b = b[np.isfinite(b[mod_name])]
    # Interpolate onto uniform time base, fill gaps up to:
    # (10 values @ 6 min = 1 hour).
    c = pd.concat([b, ts], axis=1).interpolate(limit=10)
    return c


def service_urls(records, service='odp:url'):
    """Extract service_urls of a specific type (DAP, SOS) from records."""
    service_string = 'urn:x-esri:specification:ServiceType:' + service
    urls = []
    for key, rec in records.iteritems():
        # Create a generator object, and iterate through it until the match is
        # found if not found, gets the default value (here "none").
        url = next((d['url'] for d in rec.references if
                    d['scheme'] == service_string), None)
        if url is not None:
            urls.append(url)
    return urls


def nearxy(x, y, xi, yi):
    """Find the indices x[i] of arrays (x,y) closest to the points (xi, yi)."""
    ind = np.ones(len(xi), dtype=int)
    dd = np.ones(len(xi), dtype='float')
    for i in np.arange(len(xi)):
        dist = np.sqrt((x-xi[i])**2 + (y-yi[i])**2)
        ind[i] = dist.argmin()
        dd[i] = dist[ind[i]]
    return ind, dd


def find_ij(x, y, d, xi, yi):
    """Find non-NaN cell d[j,i] that are closest to points (xi, yi)."""
    index = np.where(~np.isnan(d.flatten()))[0]
    ind, dd = nearxy(x.flatten()[index], y.flatten()[index], xi, yi)
    j, i = ind2ij(x, index[ind])
    return i, j, dd


def find_timevar(cube):
    """Return the time variable from Iris. This is a workaround for iris having
    problems with FMRC aggregations, which produce two time coordinates."""
    try:
        cube.coord(axis='T').rename('time')
    except:  # Be more specific.
        pass
    timevar = cube.coord('time')
    return timevar


def ind2ij(a, index):
    """Returns a[j, i] for a.ravel()[index]."""
    n, m = a.shape
    j = np.int_(np.ceil(index//m))
    i = np.remainder(index, m)
    return i, j


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
            background-color: #fcf8e3; border-color: #faebcc; border-left: 5px solid #8a6d3b; padding: 0.5em; color: #8a6d3b;
        }
        .success {
            background-color: #d9edf7; border-color: #bce8f1; border-left: 5px solid #31708f; padding: 0.5em; color: #31708f;
        }
        .error {
            background-color: #f2dede; border-color: #ebccd1; border-left: 5px solid #a94442; padding: 0.5em; color: #a94442;
        }
        .warning {
            background-color: #fcf8e3; border-color: #faebcc; border-left: 5px solid #8a6d3b; padding: 0.5em; color: #8a6d3b;
        }
        </style>
    """)
