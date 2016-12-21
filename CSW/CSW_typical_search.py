# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

A typical CSW search on bounding box, time extent and 

# <codecell>

from owslib.csw import CatalogueServiceWeb
from owslib import fes

# <markdowncell>

# ### Specify a bounding box and time range of interest:

# <codecell>

#box=[-74.4751, 40.3890, -73.7432, 40.9397]
box=[-76.4751, 38.3890, -71.7432, 42.9397]
box=[-75., 39., -71., 41.5]
box=[39., -75., 41.5, -71.0]
#box=[-180, -90, 180, 90]

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
jd_start = dt.datetime.utcnow()- dt.timedelta(days=0)
jd_stop = dt.datetime.utcnow() + dt.timedelta(days=0)

# round to nearest minute
start_date = jd_start.strftime('%Y-%m-%dT%H:%M:00Z')
stop_date  = jd_stop.strftime('%Y-%m-%dT%H:%M:00Z')

jd_start = dt.datetime.strptime(start_date,'%Y-%m-%dT%H:%M:00Z')
jd_stop = dt.datetime.strptime(stop_date,'%Y-%m-%dT%H:%M:00Z')

'''
start_date = jd_start.strftime('%Y-%m-%d %H:00')
stop_date  = jd_stop.strftime('%Y-%m-%d %H:00')

jd_start = dt.datetime.strptime(start_date,'%Y-%m-%d %H:%M')
jd_stop = dt.datetime.strptime(stop_date,'%Y-%m-%d %H:%M')
'''
print start_date,'to',stop_date

sos_name = 'water_surface_height_above_reference_datum'

# <markdowncell>

# Now we need to specify all the names we know for water level, names that will get used in the CSW search, and also to find data in the datasets that are returned.  This is ugly and fragile.  There hopefully will be a better way in the future...

# <codecell>

std_name_list=['sea_water_salinity','foobar_salinity']

# <markdowncell>

# ### Search CSW for datasets of interest

# <codecell>

#from IPython.core.display import HTML
#HTML('<iframe src=http://www.ngdc.noaa.gov/geoportal/ width=950 height=400></iframe>')

# <codecell>

# connect to CSW, explore it's properties

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw' # NGDC Geoportal
#endpoint = 'http://catalog.data.gov/csw-all' #  catalog.data.gov CSW
#endpoint = 'http://catalog.data.gov/csw' #  catalog.data.gov CSW
#endpoint = 'http://www.nodc.noaa.gov/geoportal/csw'   # NODC Geoportal: granule level
#endpoint = 'http://data.nodc.noaa.gov/geoportal/csw'  # NODC Geoportal: collection level   

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

stop_date

# <codecell>

# convert User Input into FES filters
start,stop = dateRange(start_date,stop_date)
bbox = fes.BBox(box)

# <codecell>

or_filt = fes.Or([fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                    escapeChar='\\',wildCard='*',singleChar='?') for val in std_name_list])

# <codecell>

val = 'sea_water_salinity'
any_filt = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                    escapeChar='\\',wildCard='*',singleChar='?') 

# <codecell>

val = 'Averages'
not_filt = fes.Not([fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')])

# <codecell>

filter_list = [fes.And([ bbox, start, stop, any_filt]) ]

# <codecell>

# try request using multiple filters "and" syntax: [[filter1,filter2]]
csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
print len(csw.records.keys())

# <codecell>

csw.request

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

# <codecell>

choice=random.choice(list(csw.records.keys()))
print choice
csw.records[choice].references

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

# <codecell>

collector = CoopsSos()

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
     'featureOfInterest=BBOX:%s&responseFormat=text/csv&eventTime=%s&'
     'result=VerticalDatum==urn:ogc:def:datum:epsg::5103&'
     'dataType=PreliminarySixMinute') % (sos_name,box_str,iso_start)
print url
obs_loc_df = pd.read_csv(url)

# <codecell>

obs_loc_df.head()

# <codecell>

stations = [sta.split(':')[-1] for sta in obs_loc_df['station_id']]
print stations
obs_lon = [sta for sta in obs_loc_df['longitude (degree)']]
obs_lat = [sta for sta in obs_loc_df['latitude (degree)']]
print obs_lon
print obs_lat

# <markdowncell>

# ### Get longName from SOS DescribeSensor request

# <codecell>

def get_Coops_longName(sta):
    """
    get longName for specific station from COOPS SOS using DescribeSensor request
    """
    url=('http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?service=SOS&'
        'request=DescribeSensor&version=1.0.0&outputFormat=text/xml;subtype="sensorML/1.0.1"&'
        'procedure=urn:ioos:sensor:NOAA.NOS.CO-OPS:%s:B1') % sta
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
    response = collector.raw(responseFormat="text/csv")
    data_df = pd.read_csv(cStringIO.StringIO(str(response)), parse_dates=True, index_col='date_time')
    data_df['Observed Data']=data_df['water_surface_height_above_reference_datum (m)']-data_df['vertical_position (m)']
    a = get_Coops_longName(coops_id)
    if len(a)==0:
        long_name=coops_id
    else:
        long_name=a[0]
        
    data_df.name=long_name
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
for sta in stations:
    b=coops2df(collector,sta,sos_name)
    print b.name
    # limit interpolation to 10 points (10 @ 6min = 1 hour)
    obs_df.append(pd.DataFrame(pd.concat([b, ts],axis=1).interpolate(limit=10)['Observed Data']))
    obs_df[-1].name=b.name

# <codecell>

sta=0;obs_df[sta].plot(figsize=(12,5),title=obs_df[sta].name);

# <markdowncell>

# ### Get model output from OPeNDAP URLS
# Try to open all the OPeNDAP URLS using Iris from the British Met Office.  If we can open in Iris, we know it's a model result.

# <markdowncell>

# Construct an Iris contraint to load only cubes that match the std_name_list:

# <codecell>

print std_name_list
def name_in_list(cube):
    return cube.standard_name in std_name_list
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

for url in dap_urls:
    try:
        a = iris.load_cube(url,constraint)
        # convert to units of meters
        a.convert_units('m')
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
            print url
            nsta = len(obs_lon)
            if len(r)==3:
                d = a[0,:,:].data
                # find the closest non-land point from a structured grid model
                j,i,dd = find_ij(lon,lat,d,obs_lon,obs_lat)
                for n in range(nsta):
                    # only use if model cell is within 0.1 degree of requested location
                    if dd[n]<0.1:
                        arr = a[istart:istop,j[n],i[n]].data                    
                        c = mod_df(arr,timevar,istart,istop,mod_name,ts)
                        name= obs_df[n].name
                        obs_df[n]=pd.concat([obs_df[n],c],axis=1)
                        obs_df[n].name = name
            elif len(r)==2:
                # find the closest point from an unstructured grid model
                index,dd = nearxy(lon.flatten(),lat.flatten(),obs_lon,obs_lat)
                for n in range(nsta):
                    # only use if model cell is within 0.1 degree of requested location
                    if dd[n]<0.1:
                        arr = a[istart:istop,index[n]].data
                        c = mod_df(arr,timevar,istart,istop,mod_name,ts)
                        name = obs_df[n].name
                        obs_df[n]=pd.concat([obs_df[n],c],axis=1)
                        obs_df[n].name = name                 
    except:
        pass

# <codecell>

for df in obs_df:
    df.plot(figsize=(14,6),title=df.name)
    ylabel('m')

# <codecell>


