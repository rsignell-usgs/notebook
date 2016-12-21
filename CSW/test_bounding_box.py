# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from owslib.csw import CatalogueServiceWeb
from owslib import fes

# <codecell>

endpoints = {'geoportal(nodc)':      'http://www.nodc.noaa.gov/geoportal/csw',
             'geoportal(ngdc)':      'http://www.ngdc.noaa.gov/geoportal/csw',
             'geoportal(epa)':       'https://edg.epa.gov/metadata/csw',
             'geonetwork(cmg)': 'http://cmgds.marine.usgs.gov/geonetwork/srv/en/csw',
             'geonetwork(cida-gdp)':'http://cida.usgs.gov/gdp/geonetwork/srv/en/csw',
             'geonetwork(cida-glri)': 'http://cida.usgs.gov/glri/geonetwork/srv/en/csw',
             'pycsw(pacioos)':       'http://oos.soest.hawaii.edu/pacioos/ogc/csw.py',
             'pycsw(data.gov)':      'http://catalog.data.gov/csw-all',
             'compusult(cgdi)':      'http://geodiscover.cgdi.ca/wes/serviceManagerCSW/csw', 
             'gi-cat(ispra)':        'http://193.206.192.216:8080/gi%2Dcat/services/cswiso'}

# <codecell>

def test_bbox(endpoints,bbox):
    for title,url in endpoints.iteritems():
        try:
            csw = CatalogueServiceWeb(url, timeout=40)
            if "BBOX" in csw.filters.spatial_operators:
                filter_list = [fes.BBox(bbox)]
                try:
                    csw.getrecords2(constraints=filter_list, maxrecords=1000)
                    print("%s : Datasets = %d" % (title,len(csw.records.keys())))
                except Exception:
                    print "%s : BBOX Query FAILS" % title
            else:
                print "%s - BBOX Query NOT supported" % title
        except Exception:
            print "%s - Timed out" % title

# <headingcell level=2>

# Search for Hawaii using (lon,lat) ordering

# <codecell>

bbox = [-158.4, 20.7, -157.2, 21.6]   
test_bbox(endpoints,bbox)

# <headingcell level=2>

# Search for Hawaii using (lat,lon) ordering

# <codecell>

bbox = [20.7, -158.4, 21.6, -157.2]   
test_bbox(endpoints,bbox)

# <headingcell level=2>

# What does this mean?

# <markdowncell>

# * geoportal(ngdc) expects (lon,lat) order, gives 0 datasets back for (LAT,LON) order
# * geoportal(epa) expects (lon,lat) order, gives 0 datasets back for (LAT,LON) order
# * geoportal(nodc) gives 1000 datasets back regardless of order
# * geonetwork(usgs/cida) fails all bounding box queries
# * geonetwork(usgs/cmg) expects (lon,lat) order, gives 0 datasets back for (LAT,LON) order
# * compusult(cgsi) expects (LAT,LON) order, gives 0 datasets back for (lon,lat) order
# * gi-cat(ispra) expects (LAT,LON) order, gives 0 datasets back for (lon,lat) order
# * pycsw(pacioos) expects (LAT,LON) order, gives 0 datasets back for (lon,lat) order
# * pycsw(data.gov) expects (LAT,LON) order, gives 5 datasets back for (lon,lat) order

# <codecell>


# <codecell>


# <codecell>


# <codecell>


