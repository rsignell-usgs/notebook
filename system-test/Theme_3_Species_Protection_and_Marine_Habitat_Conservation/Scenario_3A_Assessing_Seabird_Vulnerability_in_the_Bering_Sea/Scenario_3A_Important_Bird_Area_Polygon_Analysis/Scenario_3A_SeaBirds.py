# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from utilities import css_styles
css_styles()

# <markdowncell>

# # IOOS System Test - Theme 3 - Scenario A - [Description](https://github.com/ioos/system-test/wiki/Development-of-Test-Themes#scenario-3a-assessing-seabird-vulnerability-in-the-bering-sea)
# 
# ## Assessing Seabird Vulnerability in the Bering Sea
# 
# ## Questions
# 1. Can we discover, access, and overlay Important Bird Area polygons (and therefore other similar layers for additional important resource areas) on modeled datasets in the Bering Sea?
# 3. Is metadata for projected climate data layers and Important Bird Area polygons sufficient to determine a subset of polygons desired by a query?
# 4. Can a simple set statistics (e.g., mean and standard deviation) be derived from multiple variables in each of the six models to derive the forecast variability of climate conditions through time, through the end of the model runs (2003-2040)?
# 5. Can we create a standardized matrix or other display method for output variables that allow resource experts to easily assess projected changes in climate variables, within given ranges of time, and compare projected changes across multiple coupled oceanographic and climate models?
# 6. Can we develop a set of process-specific guidelines and a standardized set of outputs for a tool that would allow researchers to address a diversity of resource management questions relative to projected changes in climate for specific zones of interest?

# <markdowncell>

# ## Q1 - Can we discover, access, and overlay Important Bird Area polygons (and therefore other similar layers for additional important resource areas) on modeled datasets in the Bering Sea?

# <markdowncell>

# <div class="error"><strong>Discovery is not possible</strong> - No Important Bird Area polygons are not discoverable at this time.  They are, however, available in a GeoServer 'known' to us.  This should be fixed.  The WFS service should be added to a queryable CSW.</div>

# <markdowncell>

# ##### Load 'known' WFS endpoint with Important Bird Area polygons

# <codecell>

from owslib.wfs import WebFeatureService
known_wfs = "http://solo.axiomalaska.com/geoserver/audubon/ows"
wfs = WebFeatureService(known_wfs, version='1.0.0')
print sorted(wfs.contents.keys())

# <markdowncell>

# ##### We already know that the 'audubon:audubon_ibas' layer is Import Bird Areas.  Request 'geojson' response from the layer

# <codecell>

import geojson
geojson_response = wfs.getfeature(typename=['audubon:audubon_ibas'], maxfeatures=1, outputFormat="application/json", srsname="urn:x-ogc:def:crs:EPSG:4326").read()
feature = geojson.loads(geojson_response)

# <markdowncell>

# ##### Convert to Shapely geometry objects

# <codecell>

from shapely.geometry import shape
shapes = [shape(s.get("geometry")) for s in feature.get("features")]

# <markdowncell>

# ##### Map the geometry objects

# <codecell>

import folium
map_center = shapes[0].centroid
mapper = folium.Map(location=[map_center.x, map_center.y], zoom_start=6)
for s in shapes:
    if hasattr(s.boundary, 'coords'):
        mapper.line(s.boundary.coords, line_color='#FF0000', line_weight=5)
    else:
        for p in s:
            mapper.line(p.boundary.coords, line_color='#FF0000', line_weight=5)
mapper._build_map()

from IPython.core.display import HTML
HTML('<iframe srcdoc="{srcdoc}" style="width: 100%; height: 535px; border: none"></iframe>'.format(srcdoc=mapper.HTML.replace('"', '&quot;')))

# <markdowncell>

# ### Can we discover other datasets in this polygon area?

# <markdowncell>

# ##### Setup BCSW Filters to find models in the area of the Important Bird Polygon

# <codecell>

from owslib import fes 

# Polygon filters
polygon_filters = []
for s in shapes:
    f = fes.BBox(bbox=list(reversed(s.bounds)))
    polygon_filters.append(f)
# If we have more than one polygon filter, OR them together
if len(polygon_filters) > 1:
    polygon_filters = fes.Or(polygon_filters)
elif len(polygon_filters) == 1:
    polygon_filters = polygon_filters[0]
    
# Name filters
name_filters = []
model_strings = ['roms', 'selfe', 'adcirc', 'ncom', 'hycom', 'fvcom', 'wrf', 'wrams']
for model in model_strings:
    title_filter   = fes.PropertyIsLike(propertyname='apiso:Title',   literal='*%s*' % model, wildCard='*')
    name_filters.append(title_filter)
    subject_filter = fes.PropertyIsLike(propertyname='apiso:Subject', literal='*%s*' % model, wildCard='*')
    name_filters.append(subject_filter)
# Or all of the name filters together
name_filters = fes.Or(name_filters)

# Final filters
filters = fes.And([polygon_filters, name_filters])

# <markdowncell>

# ##### The actual CSW filters look like this

# <codecell>

from owslib.etree import etree
print etree.tostring(filters.toXML(), pretty_print=True)

# <markdowncell>

# ##### Find all models contain in all CSW endpoints

# <codecell>

from owslib.csw import CatalogueServiceWeb
endpoints = ['http://www.nodc.noaa.gov/geoportal/csw',
             'http://www.ngdc.noaa.gov/geoportal/csw',
             'http://catalog.data.gov/csw-all',
             #'http://cwic.csiss.gmu.edu/cwicv1/discovery',
             'http://geoport.whoi.edu/geoportal/csw',
             'https://edg.epa.gov/metadata/csw',
             'http://cmgds.marine.usgs.gov/geonetwork/srv/en/csw',
             'http://cida.usgs.gov/gdp/geonetwork/srv/en/csw',
             'http://geodiscover.cgdi.ca/wes/serviceManagerCSW/csw', 
             'http://geoport.whoi.edu/gi-cat/services/cswiso']

# <markdowncell>

# ##### Filter out CSW servers that do not support a BBOX query

# <codecell>

bbox_endpoints = []
for url in endpoints:
    queryables = []
    try:
        csw = CatalogueServiceWeb(url, timeout=20)
    except BaseException:
        print "Failure - %s - Timed out" % url
    if "BBOX" in csw.filters.spatial_operators:
        print "Success - %s - BBOX Query supported" % url
        bbox_endpoints.append(url)    
    else:
        print "Failure - %s - BBOX Query NOT supported" % url

# <codecell>

dap_urls = []
dap_services = ["urn:x-esri:specification:ServiceType:odp:url",
                "urn:x-esri:specification:ServiceType:OPeNDAP"]
for url in bbox_endpoints:
    print "*", url
    try:
        csw = CatalogueServiceWeb(url, timeout=20)
        csw.getrecords2(constraints=[filters], maxrecords=1000, esn='full')
        for record, item in csw.records.items():
            print "  -", item.title
            # Get DAP URLs
            url = next((d['url'] for d in item.references if d['scheme'] in dap_services), None)
            if url:
                print "    + OPeNDAP URL: %s" % url
                dap_urls.append(url)
            else:
                print "    + No OPeNDAP service available"
    except BaseException as e:
        print "  - FAILED", url, e.msg

# <markdowncell>

# ##### Get bounding polygons from each dataset 

# <codecell>

from paegan.cdm.dataset import CommonDataset

lookup_standard_name = "sea_water_temperature"

# Filter out DAP servers that are taking FOREVER
dap_urls = [url for url in dap_urls if "data1.gfdl.noaa.gov" not in url]

dataset_polygons = {}
for i, dap in enumerate(dap_urls):
    print '(%d/%s)' % (i+1, len(dap_urls)),
    try:
        cd = CommonDataset.open(dap)
    except BaseException:
        print "Could not access", dap
    
    try:
        var = cd.get_varname_from_stdname(standard_name=lookup_standard_name)[0]
        dataset_polygons[dap] = cd.getboundingpolygon(var=var)
        print "Retrieved bounding polygon from %s" % dap
    except (IndexError, AssertionError):
        print "No standard_name '%s' in '%s'" % (lookup_standard_name, dap)

# <markdowncell>

# ##### Overlay dataset polygons on top of Important Bird Area polygons

# <codecell>

import random
mapper = folium.Map(location=[map_center.x, map_center.y], zoom_start=0)
for name, polygon in dataset_polygons.items():
    color = "#%06x" % random.randint(0,0xFFFFFF)
    # Normal coordinates
    mapper.line(polygon.boundary.coords, line_color=color, line_weight=3)
    # Fliipped coordinates
    mapper.line([(y,x) for x,y in polygon.boundary.coords], line_color=color, line_weight=3)
    
mapper._build_map()

from IPython.core.display import HTML
HTML('<iframe srcdoc="{srcdoc}" style="width: 100%; height: 535px; border: none"></iframe>'.format(srcdoc=mapper.HTML.replace('"', '&quot;')))

# <codecell>


