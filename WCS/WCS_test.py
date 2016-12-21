# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Test ESRI WCS with OWSLib

# <codecell>

from owslib.wcs import WebCoverageService
endpoint='http://olga.er.usgs.gov/stpgis/services/lidar/Bare_Earth_Lidar/MapServer/WCSServer?request=GetCapabilities&service=WCS'

# <codecell>

wcs = WebCoverageService(endpoint,version='1.0.0',timeout=60)

# <codecell>

for k,v in wcs.contents.iteritems():
    print v.title

# <codecell>

wcs['1'].title

# <codecell>

cvg = wcs['1']
print cvg.title
print cvg.boundingBoxWGS84

# <codecell>

print cvg.supportedFormats

# <codecell>

print cvg.supportedCRS

# <codecell>

output = wcs.getCoverage(identifier=['1'],bbox=(-75.4,37.8,-75.2,38.0),crs='EPSG:4326',format='GeoTIFF')

# <codecell>

f=open('test.tif','wb')
f.write(output.read())
f.close()

# <codecell>

!more test.tif

# <codecell>


