# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=2>

# Test Data.gov bbox, start, stop filters

# <codecell>

from owslib.csw import CatalogueServiceWeb
from owslib.fes import SortBy, SortProperty
from owslib import fes
import datetime as dt

# <codecell>

#csw = CatalogueServiceWeb('http://www.ngdc.noaa.gov/geoportal/csw',timeout=60) # NGDC Geoportal
csw = CatalogueServiceWeb('http://catalog.data.gov/csw-all',timeout=60)

# <codecell>

csw.get_operation_by_name('GetRecords').constraints

# <codecell>

# adjust to match MaxRecordDefault of CSW, if would be cleaner if we pick this up Capabilities XML
# this issue will allow for this: https://github.com/geopython/OWSLib/issues/211
pagesize = 10
sort_property = 'dc:title'  # a supported queryable of the CSW
sort_order = 'ASC'  # should be 'ASC' or 'DESC'

# <codecell>

sortby = SortBy([SortProperty(sort_property, sort_order)])
foo=sortby.properties

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

val = 'salinity'
box=[-72.0, 41.0, -69.0, 43.0]   # gulf of maine

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

# 2014 recent
jd_start = dt.datetime(1988,1,1)
jd_stop = dt.datetime(1988,3,1)

# 2011 
#jd_start = dt.datetime(2013,4,20)
#jd_stop = dt.datetime(2013,4,24)

# ... or relative to now
#jd_now = dt.datetime.utcnow()
#jd_start = jd_now - dt.timedelta(days=3)
#jd_stop = jd_now + dt.timedelta(days=3)

start_date = jd_start.strftime('%Y-%m-%d %H:00')
stop_date  = jd_stop.strftime('%Y-%m-%d %H:00')

jd_start = dt.datetime.strptime(start_date,'%Y-%m-%d %H:%M')
jd_stop = dt.datetime.strptime(stop_date,'%Y-%m-%d %H:%M')

print start_date,'to',stop_date

# <codecell>

start,stop = dateRange(start_date,stop_date)
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
bbox = fes.BBox(box,crs='urn:ogc:def:crs:OGC:1.3:CRS84')

# <codecell>

filter_list = [fes.And([ bbox, filter1]) ]
csw.getrecords2(constraints=filter_list)
csw.results['matches']

# <codecell>

filter_list = [fes.And([ bbox, filter1, start,stop]) ]
csw.getrecords2(constraints=filter_list)
csw.results['matches']

# <codecell>

startposition = 0
maxrecords = 20
while True:
    
    print 'getting records %d to %d' % (startposition, startposition+pagesize)
    csw.getrecords2(constraints=filter_list,
                    startposition=startposition, maxrecords=pagesize, sortby=sortby)
#    print csw.request
    for rec,item in csw.records.iteritems():
        print item.title
    if csw.results['nextrecord'] == 0:
        break
    startposition += pagesize
    if startposition >= maxrecords:
        break

# <codecell>


