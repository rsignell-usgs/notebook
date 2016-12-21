# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# #Use CSW to find model data at NODC, NGDC, DATA.GOV and PACIOOS

# <codecell>

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import netCDF4
import datetime as dt

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

def service_urls(records,service_string='urn:x-esri:specification:ServiceType:odp:url'):
    """
    Get all URLs matching a specific ServiceType 
 
    Unfortunately these seem to differ between different CSW-ISO services.
    For example, OpenDAP is specified:
    NODC geoportal: 'urn:x-esri:specification:ServiceType:OPeNDAP'
    NGDC geoportal: 'urn:x-esri:specification:ServiceType:odp:url'
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


# <codecell>

# trying to do this search:
# ('roms' OR 'selfe' OR 'adcirc' OR 'ncom' OR 'hycom' OR 'fvcom') AND 'ocean' NOT 'regridded' NOT 'espresso'
# should return 11 records from NODC geoportal

model_name_list = ['roms','selfe','adcirc','ncom','hycom','fvcom']

#box=[-74.4751, 40.3890, -73.7432, 40.9397]
box=[-76.4751, 38.3890, -71.7432, 42.9397]

#box=[-180, -90, 180, 90]

# specific specific times (UTC) ...

# <codecell>

# ... or relative to now
jd_start = dt.datetime.utcnow()- dt.timedelta(days=3)
jd_stop = dt.datetime.utcnow() + dt.timedelta(days=3)

# <codecell>

# 2014 feb 10-15 storm
jd_start = dt.datetime(2014,2,10)
jd_stop = dt.datetime(2014,2,15)

# <codecell>

# 2014 recent
jd_start = dt.datetime(2014,3,8)
jd_stop = dt.datetime(2014,3,11)

# 2011 
#jd_start = dt.datetime(2013,4,20)
#jd_stop = dt.datetime(2013,4,24)

# <codecell>

# hurricane sandy
jd_start = dt.datetime(2012,10,26)
jd_stop = dt.datetime(2012,11,2)

# <codecell>

start_date = jd_start.strftime('%Y-%m-%d %H:00')
stop_date  = jd_stop.strftime('%Y-%m-%d %H:00')

jd_start = dt.datetime.strptime(start_date,'%Y-%m-%d %H:%M')
jd_stop = dt.datetime.strptime(stop_date,'%Y-%m-%d %H:%M')

print start_date,'to',stop_date

sos_name = 'water_surface_height_above_reference_datum'

# <codecell>


# convert User Input into FES filters
start,stop = dateRange(start_date,stop_date)
bbox = fes.BBox(box)

or_filt = fes.Or([fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                    escapeChar='\\',wildCard='*',singleChar='?') for val in model_name_list])

val = 'Averages'
not_filt = fes.Not([fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')])

filter_list = [fes.And([ bbox, start, stop, or_filt, not_filt]) ]



# <markdowncell>

# ##Find model results at NODC

# <codecell>

endpoint = 'http://www.nodc.noaa.gov/geoportal/csw'   # NODC/UAF Geoportal: granule level
endpoint = 'https://gis.ncdc.noaa.gov/geoportal/csw202/discovery'
csw = CatalogueServiceWeb(endpoint,timeout=60)
print csw.version

# <codecell>

for oper in csw.operations:
    if oper.name == 'GetRecords':
        print '\nISO Queryables:\n',oper.constraints['SupportedISOQueryables']['values']

# <codecell>

csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())

# <codecell>

choice=random.choice(list(csw.records.keys()))
print choice
csw.records[choice].references

# <codecell>

print csw.records[choice].xml

# <codecell>

dap_urls = service_urls(csw.records,service_string='urn:x-esri:specification:ServiceType:OPeNDAP')
len(dap_urls)

# <markdowncell>

# ## Find model results at NGDC

# <codecell>

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw' #  NGDC/IOOS Geoportal
csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version

# <codecell>

for oper in csw.operations:
    if oper.name == 'GetRecords':
        print '\nISO Queryables:\n',oper.constraints['SupportedISOQueryables']['values']

# <codecell>

csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())

# <codecell>

choice=random.choice(list(csw.records.keys()))
print choice
csw.records[choice].references

# <codecell>

#dap_urls = service_urls(csw.records,service_string='urn:x-esri:specification:ServiceType:OPeNDAP')
dap_urls = service_urls(csw.records,service_string='urn:x-esri:specification:ServiceType:odp:url')
len(dap_urls)

# <markdowncell>

# ## Find model data at CATALOG.DATA.GOV

# <codecell>

endpoint = 'http://catalog.data.gov/csw-all' #  catalog.data.gov CSW
csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version

# <codecell>

for oper in csw.operations:
    if oper.name == 'GetRecords':
        print '\nISO Queryables:\n',oper.constraints['SupportedISOQueryables']['values']

# <codecell>

filter_list = [fes.And([ bbox, start, stop, or_filt, not_filt]) ]
csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())

# <codecell>

filter_list = [fes.And([ bbox, or_filt, not_filt]) ]
csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())

# <codecell>

choice=random.choice(list(csw.records.keys()))
print choice
csw.records[choice].references

# <markdowncell>

# From the above, we can see that because the 'scheme' is 'None' on all the references, we can't extract the different service types, like OPeNDAP, WCS, etc. 

# <codecell>

#dap_urls = service_urls(csw.records,service_string='urn:x-esri:specification:ServiceType:odp:url')  #NGDC
#dap_urls = service_urls(csw.records,service_string='urn:x-esri:specification:ServiceType:OPeNDAP')  #NODC
dap_urls = service_urls(csw.records,service_string='?????????')    #CATALOG.DATA.GOV
len(dap_urls)

# <markdowncell>

# ## Search at PACIOOS

# <codecell>

endpoint = 'http://oos.soest.hawaii.edu/cgi-bin/csw.py' #  catalog.data.gov CSW
csw = CatalogueServiceWeb(endpoint,timeout=60)
print csw.version

# <codecell>

for oper in csw.operations:
    if oper.name == 'GetRecords':
        print '\nISO Queryables:\n',oper.constraints['SupportedISOQueryables']['values']

# <codecell>

filter_list = [fes.And([ bbox, start, stop, or_filt, not_filt]) ]
csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())

# <codecell>

choice=random.choice(list(csw.records.keys()))
print choice
csw.records[choice].references

# <codecell>

filter_list = [fes.And([ bbox,  or_filt]) ]
csw.getrecords2(constraints=filter_list,maxrecords=1000,esn='full')
len(csw.records.keys())

# <codecell>

for rec,item in csw.records.iteritems():
    print item.title

# <codecell>

choice=random.choice(list(csw.records.keys()))
print choice
csw.records[choice].references

# <codecell>


