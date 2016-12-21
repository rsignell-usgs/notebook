# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

%matplotlib inline

# <codecell>

import matplotlib.pyplot as plt

import cartopy.crs as ccrs
from cartopy.io import shapereader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

def make_map(projection=ccrs.PlateCarree()):
    fig, ax = plt.subplots(figsize=(9, 13),
                           subplot_kw=dict(projection=projection))
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    return fig, ax

# <codecell>

from cartopy.feature import NaturalEarthFeature

extent = [-39, -38.25, -13.25, -12.5]

coast = NaturalEarthFeature(category='physical', scale='10m',
                            facecolor='none', name='coastline')

fig, ax = make_map(projection=ccrs.PlateCarree())

ax.set_extent(extent)

feature = ax.add_feature(coast, edgecolor='gray')

# <codecell>

from cartopy.io import img_tiles

tiles = img_tiles.OSM()

ax = plt.subplot(111, projection=ccrs.Mercator())
ax.set_extent(extent)
ax.add_image(tiles, 9)
ax.coastlines("10m")

# <codecell>

import netCDF4

# <codecell>


# <codecell>

from owslib.wcs import WebCoverageService
import numpy as np
import numpy.ma as ma
endpoint='http://geoport.whoi.edu/thredds/wcs/bathy/gom03_v1_0?service=WCS&version=1.0.0&request=GetCapabilities'

# <codecell>

wcs = WebCoverageService(endpoint,version='1.0.0',timeout=60)

# <codecell>

wcs.contents

# <codecell>

for k,v in wcs.contents.iteritems():
    print v.title

# <codecell>

# try Boston Harbor
bbox = (-71.05592748611777, 42.256890708126605, -70.81446033774644, 42.43833963977496)
output = wcs.getCoverage(identifier="topo",bbox=bbox,format='GeoTIFF',
                         resx=0.0003, resy=0.0003)

# <codecell>

f=open('test.tif','wb')
f.write(output.read())
f.close()

# <codecell>

from osgeo import gdal
gdal.UseExceptions()
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

elevation=ma.masked_less_equal(elevation,-1.e5)

# <codecell>

from cartopy.feature import NaturalEarthFeature
extent = [-71.5, -70.5, 42.0, 42.7]


coast = NaturalEarthFeature(category='physical', scale='10m',
                            facecolor='none', name='coastline')

fig, ax = make_map(projection=ccrs.PlateCarree())



ax.set_extent(extent)

feature = ax.add_feature(coast, edgecolor='gray')

# <codecell>


# <codecell>

plt.figure(figsize=(8,10))
ax = plt.axes(projection=ccrs.PlateCarree())
#tiler = MapQuestOpenAerial()
#ax.add_image(tiler, 14)
plt.imshow(elevation, cmap='jet', extent=[x0, x1, y1, y0],
           transform=ccrs.PlateCarree(),alpha=0.6,zorder=2);
ax.gridlines(draw_labels=True,zorder=3);

# <codecell>


