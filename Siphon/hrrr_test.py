# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import matplotlib.pyplot as plt
import numpy as np
%matplotlib inline

# <headingcell level=2>

# Extract HRRR data using Unidata's Siphon package

# <codecell>

# Resolve the latest HRRR dataset
from siphon.catalog import TDSCatalog
latest_hrrr = TDSCatalog('http://thredds-jumbo.unidata.ucar.edu/thredds/catalog/grib/HRRR/CONUS_3km/surface/latest.xml')
hrrr_ds = list(latest_hrrr.datasets.values())[0]

# Set up access via NCSS
from siphon.ncss import NCSS
ncss = NCSS(hrrr_ds.access_urls['NetcdfSubset'])

# Create a query to ask for all times in netcdf4 format for
# the Temperature_surface variable, with a bounding box
query = ncss.query()

# <codecell>

query.all_times().accept('netcdf4').variables('Temperature_surface')
query.lonlat_box(45, 41., -63, -71.5)

# Get the raw bytes and write to a file.
data = ncss.get_data_raw(query)
with open('test.nc', 'wb') as outf:
    outf.write(data)

# <headingcell level=2>

# Try reading extracted data with Xray

# <codecell>

import xray

# <codecell>

nc = xray.open_dataset('test.nc')

# <codecell>

nc

# <codecell>

var='Temperature_surface'
ncvar = nc[var]
ncvar

# <codecell>

grid = nc[ncvar.grid_mapping]
grid

# <codecell>

lon0 = grid.longitude_of_central_meridian
lat0 = grid.latitude_of_projection_origin
lat1 = grid.standard_parallel
earth_radius = grid.earth_radius

# <headingcell level=2>

# Try plotting the LambertConformal data with Cartopy

# <codecell>

import cartopy
import cartopy.crs as ccrs

# <codecell>

#cartopy wants meters, not km
x = ncvar.x.data*1000.
y = ncvar.y.data*1000.

# <codecell>

#globe = ccrs.Globe(ellipse='WGS84') #default
globe = ccrs.Globe(ellipse='sphere', semimajor_axis=grid.earth_radius)

crs = ccrs.LambertConformal(central_longitude=lon0, central_latitude=lat0, 
                            standard_parallels=(lat0,lat1), globe=globe)

# <codecell>

print(ncvar.x.data.shape)
print(ncvar.y.data.shape)
print(ncvar.data.shape)

# <codecell>

ncvar[6,:,:].time1.data

# <codecell>

istep =6
fig = plt.figure(figsize=(12,8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.pcolormesh(x,y,ncvar[istep,:,:].data, transform=crs,zorder=0)
ax.coastlines(resolution='10m',color='black',zorder=1)
gl = ax.gridlines(draw_labels=True)
gl.xlabels_top = False
gl.ylabels_right = False
plt.title(ncvar[istep].time1.data);

# <codecell>


