# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# #IOOS System Test: [Extreme Events Theme](https://github.com/ioos/system-test/wiki/Development-of-Test-Themes#wiki-theme-2-extreme-events):  Inundation
# 
# ###Compare modeled water levels with observations for a specified bounding box and time period using IOOS recommended service standards for catalog search (CSW) and data retrieval (OPeNDAP & SOS). <p>
# 
# * Query CSW to find datasets that match criteria
# * Extract OPeNDAP data endpoints from model datasets and SOS endpoints from observational datasets
# * OPeNDAP model datasets will be granules
# * SOS endpoints may be datasets (from ncSOS) or collections of datasets (from NDBC, CO-OPS SOS servers)
# * Filter SOS services to obtain datasets
# * Extract data from SOS datasets
# * Extract data from model datasets at locations of observations
# * Compare time series data on same vertical datum

# <codecell>

from pylab import *
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
from lxml import etree
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.img_tiles import MapQuestOpenAerial, MapQuestOSM, OSM

# <markdowncell>

# ### Specify a time range and bounding box of interest:

# <codecell>

# specific specific times (UTC) ...

# hurricane sandy
jd_start = dt.datetime(2012,10,26)
jd_stop = dt.datetime(2012,11,2)

# 2014 feb 10-15 storm
jd_start = dt.datetime(2014,2,10)
jd_stop = dt.datetime(2014,2,15)

# 2014 recent
jd_start = dt.datetime(2014,3,8)
jd_stop = dt.datetime(2014,3,11)

# 2011 
#jd_start = dt.datetime(2013,4,20)
#jd_stop = dt.datetime(2013,4,24)

# ... or relative to now
jd_now = dt.datetime.utcnow()
jd_start = jd_now - dt.timedelta(days=3)
jd_stop = jd_now + dt.timedelta(days=3)

start_date = jd_start.strftime('%Y-%m-%d %H:00')
stop_date  = jd_stop.strftime('%Y-%m-%d %H:00')

jd_start = dt.datetime.strptime(start_date,'%Y-%m-%d %H:%M')
jd_stop = dt.datetime.strptime(stop_date,'%Y-%m-%d %H:%M')

print start_date,'to',stop_date


# <codecell>

# Bounding Box [lon_min, lat_min, lon_max, lat_max]
box=[-75., 39., -71., 41.5]  # new york harbor region
#box=[-72.0, 41.0, -69.0, 43.0]   # gulf of maine
#box=[-160.0, 18.0, -154., 23.0] #hawaii

# <markdowncell>

# Now we need to specify all the names we know for water level, names that will get used in the CSW search, and also to find data in the datasets that are returned.  This is ugly and fragile.  There hopefully will be a better way in the future...

# <codecell>

name_list=['water_surface_height_above_reference_datum',
    'sea_surface_height_above_geoid','sea_surface_elevation',
    'sea_surface_height_above_reference_ellipsoid','sea_surface_height_above_sea_level',
    'sea_surface_height','water level']

sos_name = 'water_surface_height_above_reference_datum'

# <markdowncell>

# ### Search CSW for datasets of interest

# <codecell>

#from IPython.core.display import HTML
#HTML('<iframe src=http://www.ngdc.noaa.gov/geoportal/ width=950 height=400></iframe>')

# <codecell>

# connect to CSW, explore it's properties

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw' # NGDC Geoportal
#endpoint = 'http://geoport.whoi.edu/geoportal/csw'  # USGS WHSC Geoportal

#endpoint = 'http://www.nodc.noaa.gov/geoportal/csw'   # NODC Geoportal: granule level
#endpoint = 'http://data.nodc.noaa.gov/geoportal/csw'  # NODC Geoportal: collection level   
#endpoint = 'http://geodiscover.cgdi.ca/wes/serviceManagerCSW/csw'  # NRCAN CUSTOM
#endpoint = 'http://geoport.whoi.edu/gi-cat/services/cswiso' # USGS Woods Hole GI_CAT
#endpoint = 'http://cida.usgs.gov/gdp/geonetwork/srv/en/csw' # USGS CIDA Geonetwork
#endpoint = 'http://cmgds.marine.usgs.gov/geonetwork/srv/en/csw' # USGS Coastal and Marine Program
#endpoint = 'http://geoport.whoi.edu/geoportal/csw' # USGS Woods Hole Geoportal 
#endpoint = 'http://geo.gov.ckan.org/csw'  # CKAN testing site for new Data.gov
#endpoint = 'https://edg.epa.gov/metadata/csw'  # EPA
#endpoint = 'http://cwic.csiss.gmu.edu/cwicv1/discovery'  # CWIC

csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version

# <codecell>

csw.get_operation_by_name('GetRecords').constraints

# <codecell>

# hopefully something like this will be implemented in fes soon
def dateRange(start_date='1900-01-01',stop_date='2100-01-01',constraint='overlaps'):
    if constraint == 'overlaps':
        start = fes.PropertyIsLessThanOrEqualTo(propertyname='apiso:TempExtent_begin', literal=stop_date)
        stop = fes.PropertyIsGreaterThanOrEqualTo(propertyname='apiso:TempExtent_end', literal=start_date)
    elif constraint == 'within':
        start = fes.PropertyIsGreaterThanOrEqualTo(propertyname='apiso:TempExtent_begin', literal=start_date)
        stop = fes.PropertyIsLessThanOrEqualTo(propertyname='apiso:TempExtent_end', literal=stop_date)
    return start,stop

# <codecell>


# <codecell>

stop_date

# <codecell>

# convert User Input into FES filters
start,stop = dateRange(start_date,stop_date)
bbox = fes.BBox(box)

# <codecell>

or_filt = fes.Or([fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                    escapeChar='\\',wildCard='*',singleChar='?') for val in name_list])

# <markdowncell>

# ROMS model output often has Averages and History files.  The Averages files are usually averaged over a tidal cycle or more, while the History files are snapshots at that time instant.  We are not interested in averaged data for this test, so in the cell below we remove any Averages files here by removing any datasets that have the term "Averages" in the metadata text.  A better approach would be to look at the `cell_methods` attributes propagated through to some term in the ISO metadata, but this is not implemented yet, as far as I know

# <codecell>

val = 'Averages'
not_filt = fes.Not([fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')])

# <codecell>

filter_list = [fes.And([ bbox, start, stop, or_filt, not_filt]) ]

# <codecell>

# try request using multiple filters "and" syntax: [[filter1,filter2]]
csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
print len(csw.records.keys())

# <markdowncell>

# Now print out some titles

# <codecell>

for rec,item in csw.records.iteritems():
    print item.title

# <markdowncell>

# Define a function that will return the endpoint for a specified service type

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

# <markdowncell>

# Print out all the OPeNDAP Data URL endpoints

# <codecell>

dap_urls = service_urls(csw.records,service_string='urn:x-esri:specification:ServiceType:odp:url')
print "\n".join(dap_urls)

# <markdowncell>

# Print out all the SOS Data URL endpoints

# <codecell>

sos_urls = service_urls(csw.records,service_string='urn:x-esri:specification:ServiceType:sos:url')
print "\n".join(sos_urls)

# <codecell>

def nearxy(x,y,xi,yi):
    """
    find the indices x[i] of arrays (x,y) closest to the points (xi,yi)
    """
    ind=ones(len(xi),dtype=int)
    dd=ones(len(xi),dtype='float')
    for i in arange(len(xi)):
        dist=sqrt((x-xi[i])**2+(y-yi[i])**2)
        ind[i]=dist.argmin()
        dd[i]=dist[ind[i]]
    return ind,dd

# <codecell>

def find_ij(x,y,d,xi,yi):
    """
    find non-NaN cell d[j,i] that are closest to points (xi,yi).
    """
    index = where(~isnan(d.flatten()))[0]
    ind,dd = nearxy(x.flatten()[index],y.flatten()[index],xi,yi)
    j,i=ind2ij(x,index[ind])
    return i,j,dd
    

# <codecell>

def find_timevar(cube):
    """
    return the time variable from Iris. This is a workaround for
    Iris having problems with FMRC aggregations, which produce two time coordinates
    """
    try:
        cube.coord(axis='T').rename('time')
    except:
        pass
    timevar = cube.coord('time')
    return timevar
    

# <codecell>

def ind2ij(a,index):
    """
    returns a[j,i] for a.ravel()[index]
    """
    n,m = shape(lon)
    j = ceil(index/m).astype(int)
    i = remainder(index,m)
    return i,j

# <markdowncell>

# ## 1. Get observations from SOS
# Here we are using a custom class from pyoos to read the CO-OPS SOS.  This is definitely unsavory, as the whole point of using a standard is avoid the need for custom classes for each service.  Need to examine the consequences of removing this and just going with straight SOS service using OWSLib. 

# <codecell>

collector = CoopsSos()
collector.set_datum('NAVD')
#collector.set_datum('MSL')

# <codecell>

collector.server.identification.title

# <codecell>

collector.start_time = jd_start
collector.end_time = jd_stop
collector.variables = [sos_name]

# <codecell>

ofrs = collector.server.offerings

# <codecell>

print len(ofrs)
for p in ofrs[700:710]: print p

# <markdowncell>

# ### Find the SOS stations within our bounding box and time extent
# We would like to just use a filter on a collection to get a new collection, but PYOOS doesn't do that yet. So we do a GetObservation request for a collection, including a bounding box, and asking for one value at the start of the time period of interest.   We use that to do a bounding box filter on the SOS server, which returns 1 point for each station found.  So for 3 stations, we get back 3 records, in CSV format.  We can strip the station ids from the CSV, and then we have a list of stations we can use with pyoos.  The template for the GetObservation query for the bounding box filtered collection was generated using the GUI at http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/

# <codecell>

iso_start = jd_start.strftime('%Y-%m-%dT%H:%M:%SZ')
print iso_start
box_str=','.join(str(e) for e in box)
print box_str

# <codecell>

url=('http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?'
     'service=SOS&request=GetObservation&version=1.0.0&'
     'observedProperty=%s&offering=urn:ioos:network:NOAA.NOS.CO-OPS:WaterLevelActive&'
     'featureOfInterest=BBOX:%s&responseFormat=text/csv&eventTime=%s') % (sos_name,box_str,iso_start)
print url
obs_loc_df = pd.read_csv(url)

# <codecell>

obs_loc_df.head()

# <codecell>

stations = [sta.split(':')[-1] for sta in obs_loc_df['station_id']]
print stations
obs_lon = [sta for sta in obs_loc_df['longitude (degree)']]
obs_lat = [sta for sta in obs_loc_df['latitude (degree)']]

# <markdowncell>

# ### Get longName from SOS DescribeSensor (station) request

# <codecell>

def get_Coops_longName(sta):
    """
    get longName for specific station from COOPS SOS using DescribeSensor request
    """
    url=('http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?service=SOS&'
        'request=DescribeSensor&version=1.0.0&outputFormat=text/xml;subtype="sensorML/1.0.1"&'
        'procedure=urn:ioos:station:NOAA.NOS.CO-OPS:%s') % sta
    tree = etree.parse(urllib2.urlopen(url))
    root = tree.getroot()
    longName=root.xpath("//sml:identifier[@name='longName']/sml:Term/sml:value/text()", namespaces={'sml':"http://www.opengis.net/sensorML/1.0.1"})
    return longName

# <markdowncell>

# ###Request CSV response from SOS and convert to Pandas DataFrames

# <codecell>

def coops2df(collector,coops_id,sos_name):
    collector.features = [coops_id]
    collector.variables = [sos_name]
    try:
        response = collector.raw(responseFormat="text/csv")

        data_df = pd.read_csv(cStringIO.StringIO(str(response)), parse_dates=True, index_col='date_time')

#    data_df['Observed Data']=data_df['water_surface_height_above_reference_datum (m)']-data_df['vertical_position (m)']
        data_df['Observed Data']=data_df['water_surface_height_above_reference_datum (m)']

        a = get_Coops_longName(coops_id)
        if len(a)==0:
            long_name=coops_id
        else:
            long_name=a[0]

        data_df.name=long_name
    except:
        print('datum not found')
    return data_df

# <markdowncell>

# Generate a uniform 6-min time base for model/data comparison:

# <codecell>

ts_rng = pd.date_range(start=jd_start, end=jd_stop, freq='6Min')
ts = pd.DataFrame(index=ts_rng)
print jd_start,jd_stop
print len(ts)

# <markdowncell>

# Create a list of obs dataframes, one for each station:

# <codecell>

obs_df=[]
sta_names=[]
for sta in stations:
    b=coops2df(collector,sta,sos_name)
    sta_names.append(b.name)
    print b.name
    # limit interpolation to 10 points (10 @ 6min = 1 hour)
    obs_df.append(pd.DataFrame(pd.concat([b, ts],axis=1).interpolate(limit=10)['Observed Data']))
    obs_df[-1].name=b.name

# <codecell>

from matplotlib.transforms import offset_copy
geodetic = ccrs.Geodetic(globe=ccrs.Globe(datum='WGS84'))
figure(figsize=(8,8))
# Open Source Imagery from MapQuest (max zoom = 16?)
tiler = MapQuestOpenAerial()
# Open Street Map (max zoom = 18?)
#tiler = OSM()
ax = plt.axes(projection=tiler.crs)
extent=[box[0],box[2],box[1],box[3]]
ax.set_extent(extent, geodetic)
ax.add_image(tiler, 7)
plt.scatter(obs_lon,obs_lat,marker='o',s=30.0,
         color='cyan',transform=ccrs.PlateCarree())
geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
text_transform = offset_copy(geodetic_transform, units='dots', x=-7,y=+7)

for x,y,label in zip(obs_lon,obs_lat,sta_names):
    plt.text(x,y,label,horizontalalignment='left',transform=text_transform,color='white')
gl=ax.gridlines(draw_labels=True)
gl.xlabels_top = False
gl.ylabels_right = False
title('Water Level Gauge Locations')

# <markdowncell>

# ### Get model output from OPeNDAP URLS
# Try to open all the OPeNDAP URLS using Iris from the British Met Office.  If 1D, assume dataset is data, if 2D assume dataset is an unstructured grid model, and if 3D, assume it's a structured grid model.

# <markdowncell>

# Construct an Iris contraint to load only cubes that match the std_name_list:

# <codecell>

print name_list
def name_in_list(cube):
    return cube.standard_name in name_list
constraint = iris.Constraint(cube_func=name_in_list)

# <codecell>

def mod_df(arr,timevar,istart,istop,mod_name,ts):
    """
    return time series (DataFrame) from model interpolated onto uniform time base
    """
    t=timevar.points[istart:istop]
    jd = timevar.units.num2date(t)

    # eliminate any data that is closer together than 10 seconds
    # this was required to handle issues with CO-OPS aggregations, I think because
    # they use floating point time in hours, which is not very accurate, so the FMRC
    # aggregation is aggregating points that actually occur at the same time
    dt =diff(jd)
    s = array([ele.seconds for ele in dt])
    ind=where(s>10)[0]
    arr=arr[ind+1]
    jd=jd[ind+1]
    
    b = pd.DataFrame(arr,index=jd,columns=[mod_name])
    # eliminate any data with NaN
    b = b[isfinite(b[mod_name])]
    # interpolate onto uniform time base, fill gaps up to: (10 values @ 6 min = 1 hour)
    c = pd.concat([b, ts],axis=1).interpolate(limit=10)
    return c

# <codecell>

# use only data within 0.04 degrees (about 4 km)
max_dist=0.04 

# use only data where the standard deviation of the time series exceeds 0.01 m (1 cm)
# this eliminates flat line model time series that come from land points that 
# should have had missing values.
min_var=0.01

for url in dap_urls:
    try:
        a = iris.load_cube(url,constraint)
        # convert to units of meters
 #       a.convert_units('m')     # this isn't working for unstructured data
        # take first 20 chars for model name
        mod_name = a.attributes['title'][0:20]
        r = shape(a)
        timevar = find_timevar(a)
        lat = a.coord(axis='Y').points
        lon = a.coord(axis='X').points
        jd = timevar.units.num2date(timevar.points)
        istart = timevar.nearest_neighbour_index(timevar.units.date2num(jd_start))
        istop = timevar.nearest_neighbour_index(timevar.units.date2num(jd_stop))
        
        # only proceed if we have data in the range requested
        if istart != istop:            
            nsta = len(obs_lon)
            if len(r)==3:
                print '[Structured grid model]:', url
                d = a[0,:,:].data
                # find the closest non-land point from a structured grid model
                if len(shape(lon))==1:
                    lon,lat= meshgrid(lon,lat)
                j,i,dd = find_ij(lon,lat,d,obs_lon,obs_lat)
                for n in range(nsta):
                    # only use if model cell is within 0.1 degree of requested location
                    if dd[n] <= max_dist:
                        arr = a[istart:istop,j[n],i[n]].data                    
                        if arr.std() >= min_var:
                            c = mod_df(arr,timevar,istart,istop,mod_name,ts)
                            name= obs_df[n].name
                            obs_df[n]=pd.concat([obs_df[n],c],axis=1)
                            obs_df[n].name = name
            elif len(r)==2:
                print '[Unstructured grid model]:', url
                # find the closest point from an unstructured grid model
                index,dd = nearxy(lon.flatten(),lat.flatten(),obs_lon,obs_lat)
                for n in range(nsta):
                    # only use if model cell is within 0.1 degree of requested location
                    if dd[n] <= max_dist:
                        arr = a[istart:istop,index[n]].data
                        if arr.std() >= min_var:
                            c = mod_df(arr,timevar,istart,istop,mod_name,ts)
                            name = obs_df[n].name
                            obs_df[n]=pd.concat([obs_df[n],c],axis=1)
                            obs_df[n].name = name 
            elif len(r)==1:
                print '[Data]:', url
                        
    except:
        pass

# <codecell>

for df in obs_df:
    print df.head()

# <codecell>

for df in obs_df:
    p=df.plot(figsize=(14,6),title=df.name,legend=False)
    setp(p.lines[0],linewidth=4.0,color=[0.7,0.7,0.7],zorder=1)
    legend()
    ylabel('m')

# <rawcell>

# # plot again, but now remove the mean offset (relative to data) from all plots
# for df in obs_df:
#     amean=df[jd_start:jd_now].mean()
#     df = df - amean + amean.ix[0]
# #    print amean.ix[0]-amean
#     df.plot(figsize=(14,6))
#     ylabel('m')

# <codecell>

obs_lon

# <codecell>

obs_lat

# <codecell>


