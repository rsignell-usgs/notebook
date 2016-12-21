# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Performance of sci-wms and ncwms for curvilinear grid data

# <codecell>

%matplotlib inline
from IPython.core.display import Image

# <headingcell level=3>

# Let's see if we can get ncwms and sci-wms maps that look the same from COAWST output

# <codecell>

url='http://sci-wms.whoi.edu/wms/datasets/coawst?service=WMS&request=GetMap&version=1.1.1&layers=temp&styles=pcolor_jet&format=image/png&transparent=true&height=256&width=256&colorscalerange=10,30&srs=EPSG%3A4326&BBOX=-89.8606,21.882,-67.887973988643,40.890&elevation=15'
from IPython.core.display import Image
Image(url=url)

# <codecell>

url='http://geoport-dev.whoi.edu/thredds/wms/coawst_4/use/fmrc/coawst_4_use_best.ncd?LAYERS=temp&ELEVATION=-0.03125&TRANSPARENT=true&STYLES=boxfill%2Frainbow&COLORSCALERANGE=10.0%2C30.00&LOGSCALE=false&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&EXCEPTIONS=application%2Fvnd.ogc.se_inimage&FORMAT=image%2Fpng&SRS=EPSG%3A4326&BBOX=-89.8606,21.882,-67.887973988643,40.890&WIDTH=256&HEIGHT=256'
Image(url=url)

# <headingcell level=3>

# How long does the sci-wms getmap query take?

# <codecell>

!curl -o /tmp/foo.png "http://sci-wms.whoi.edu/wms/datasets/coawst?service=WMS&request=GetMap&version=1.1.1&layers=temp&styles=pcolor_jet&format=image/png&transparent=true&height=256&width=256&colorscalerange=10,30&srs=EPSG%3A4326&BBOX=-89.8606,21.882,-67.887973988643,40.890&elevation=15"

# <headingcell level=3>

# How long does the ncWMS getmap query take?

# <codecell>

!curl -o /tmp/foo2.png "http://geoport-dev.whoi.edu/thredds/wms/coawst_4/use/fmrc/coawst_4_use_best.ncd?LAYERS=temp&ELEVATION=-0.03125&TRANSPARENT=true&STYLES=boxfill%2Frainbow&COLORSCALERANGE=10.0%2C30.00&LOGSCALE=false&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&EXCEPTIONS=application%2Fvnd.ogc.se_inimage&FORMAT=image%2Fpng&SRS=EPSG%3A4326&BBOX=-89.8606,21.882,-67.887973988643,40.890&WIDTH=256&HEIGHT=256"

# <headingcell level=3>

# So on this test, sci-wms is much slower

# <markdowncell>

# Kyle points out [here](https://github.com/sci-wms/sci-wms/issues/96#issuecomment-152262018) that the slowness in sci-wms might come from OPeNDAP rather than local file access.   Let's check that out.

# <headingcell level=3>

# Try NetCDF4 with OPeNDAP

# <codecell>

%%timeit
from netCDF4 import Dataset
url = 'http://geoport-dev.whoi.edu/thredds/dodsC/coawst_4/use/fmrc/coawst_4_use_best.ncd'
nc = Dataset(url)
ncv = nc.variables
t = ncv['temp'][-1,-1,:,:]
lon = ncv['lon_rho'][:,:]
lat = ncv['lat_rho'][:,:]

# <headingcell level=3>

# Try NetCDF4 with local file

# <codecell>

%%timeit
from netCDF4 import Dataset
url = '/usgs/vault0/coawst/coawst_4/Output/use/coawst_us_20151029_13.nc'
nc = Dataset(url)
ncv = nc.variables
t = ncv['temp'][-1,-1,:,:]
lon = ncv['lon_rho'][:,:]
lat = ncv['lat_rho'][:,:]

# <headingcell level=3>

# Try Siphon with CDMRemote

# <codecell>

%%timeit
from siphon.cdmr import Dataset
url='http://geoport-dev.whoi.edu/thredds/cdmremote/coawst_4/use/fmrc/coawst_4_use_best.ncd'
ds = Dataset(url)
ncv = ds.variables
t = ncv['temp'][-1,-1,:,:]
lon = ncv['lon_rho'][:,:]
lat = ncv['lat_rho'][:,:]

# <markdowncell>

# Conclusion: Since sci-wms uses OPeNDAP, it can't compete with ncWMS local file reads.  However, CDMRemote is faster than OPeNDAP on this test.  We could check for CDMRemote and use it if is exists. 

# <codecell>


