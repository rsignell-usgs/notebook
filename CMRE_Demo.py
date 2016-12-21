# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# CMRE search, access and visualize demo

# <headingcell level=2>

# Search for data using OGC Catalog Service for the Web (CSW)

# <codecell>

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import netCDF4
import numpy as np

# <codecell>

endpoint='http://scsrv26v:8000/pycsw'
#endpoint='http://www.ngdc.noaa.gov/geoportal/csw'
csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version

# <codecell>

box=[38., 6., 41., 9.]     #  lon_min lat_min lon_max lat_max
start_date='2014-03-12 18:00'
stop_date='2014-09-18 18:00'
val = 'sea_water_potential_temperature'

# <codecell>

# convert User Input into FES filters
start,stop = dateRange(start_date,stop_date)
bbox = fes.BBox(box)
any_text = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')

# <codecell>

# combine filters into a list
filter_list = [fes.And([ start, stop, bbox,any_text]) ]

# <codecell>

csw.getrecords2(constraints=filter_list,maxrecords=100,esn='full')
len(csw.records.keys())

# <codecell>

#scheme='urn:x-esri:specification:ServiceType:odp:url'
scheme='OPeNDAP:OPeNDAP'
urls = service_urls(csw.records,service_string=scheme)
print "\n".join(urls)

# <headingcell level=2>

# Use Iris to access CF data

# <codecell>

cube = iris.load_cube(urls[7],'sea_water_potential_temperature')

# <codecell>

# color filled contour plot
h = iplt.contourf(cube[1,0,:,:],64)
plt.title(cube.attributes['title']);

