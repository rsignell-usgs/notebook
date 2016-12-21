# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Extract data from USGS ScienceBase

# <codecell>

%matplotlib inline

# <codecell>

from owslib.wcs import WebCoverageService
import numpy as np
import numpy.ma as ma
endpoint='https://www.sciencebase.gov/catalogMaps/mapping/ows/5638cf1fe4b0d6133fe73040?service=wcs&request=getcapabilities&version=1.1.1'

# <codecell>

wcs = WebCoverageService(endpoint,version='1.1',timeout=60)

# <codecell>

wcs.contents

# <codecell>

for k,v in wcs.contents.iteritems():
    print v.title

# <codecell>

g = wcs['bh_30mbathy']
print g.title
print g.boundingBoxWGS84
print g.supportedFormats

# <codecell>

# try Boston Harbor
bbox = (-71.05592748611777, 42.256890708126605, -70.81446033774644, 42.43833963977496)
output = wcs.getCoverage(identifier="bh_30mbathy",bbox=bbox,crs='EPSG:4326',format='GeoTIFF',
                         resx=0.0003, resy=0.0003)

# <codecell>

wcs.

# <codecell>

f=open('test.tif','wb')
f.write(output.read())
f.close()

# <codecell>

from osgeo import gdal
gdal.UseExceptions()

# <codecell>

ds = gdal.Open('test.tif')

# <codecell>

band = ds.GetRasterBand(1)
elevation = band.ReadAsArray()
nrows, ncols = elevation.shape

# I'm making the assumption that the image isn't rotated/skewed/etc. 
# This is not the correct method in general, but let's ignore that for now
# If dxdy or dydx aren't 0, then this will be incorrect
x0, dx, dxdy, y0, dydx, dy = ds.GetGeoTransform()

if dxdy == 0.0:
    x1 = x0 + dx * ncols
    y1 = y0 + dy * nrows

# <codecell>

import cartopy.crs as ccrs
from cartopy.io.img_tiles import MapQuestOpenAerial, MapQuestOSM, OSM

# <codecell>

print x0,x1,y1,y0

# <codecell>

elevation=ma.masked_less_equal(elevation,-1.e5)

# <codecell>

print elevation.min(), elevation.max()

# <codecell>

plt.figure(figsize=(8,10))
ax = plt.axes(projection=ccrs.PlateCarree())
tiler = MapQuestOpenAerial()
ax.add_image(tiler, 14)
plt.imshow(elevation, cmap='jet', extent=[x0, x1, y1, y0],
           transform=ccrs.PlateCarree(),alpha=0.6,zorder=2);
ax.gridlines(draw_labels=True,zorder=3);

# <codecell>


