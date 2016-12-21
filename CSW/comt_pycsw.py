# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# #Use CSW to find ROMS data at COMT pycsw

# <codecell>

from owslib.csw import CatalogueServiceWeb
from owslib import fes

# <markdowncell>

# ##Find model results at COMT pycsw

# <codecell>

endpoint = 'http://comt.sura.org:8000/pycsw'   # NODC/UAF Geoportal: granule level
csw = CatalogueServiceWeb(endpoint,timeout=60)
print csw.version

# <codecell>

csw.get_operation_by_name('GetRecords').constraints

# <codecell>

val = 'ROMS'
filter1 = fes.PropertyIsLike(propertyname='apiso:AnyText',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ filter1 ]

# <codecell>

csw.getrecords2(constraints=filter_list,maxrecords=100,esn='full')
print len(csw.records.keys())
for rec in list(csw.records.keys()):
    print csw.records[rec].title 
    

# <codecell>

choice=np.random.choice(list(csw.records.keys()))
print(csw.records[choice].title)
csw.records[choice].references

# <markdowncell>

# Add bounding box constraint. To specify lon,lat order for bbox (which we want to do so that we can use the same bbox with either geoportal server or pycsw requests), we need to request the bounding box specifying the CRS84 coordinate reference system.   The CRS84 option is available in `pycsw 1.1.10`+. The ability to specify the `crs` in the bounding box request is available in `owslib 0.8.12`+.  For more info on the bounding box problem and how it was solved, see this [pycsw issue](https://github.com/geopython/pycsw/issues/287), this [geoportal server issue](https://github.com/Esri/geoportal-server/issues/124), and this [owslib issue](https://github.com/geopython/OWSLib/issues/201)

# <codecell>

bbox = [-87.40, 24.25, -74.70, 36.70]
bbox_filter = fes.BBox(bbox,crs='urn:ogc:def:crs:OGC:1.3:CRS84')
filter_list = [filter1, bbox_filter]
csw.getrecords2(constraints=filter_list, maxrecords=1000)

# <codecell>

print len(csw.records.keys())
for rec in list(csw.records.keys()):
    print csw.records[rec].title 

# <codecell>


# <codecell>


# <codecell>


