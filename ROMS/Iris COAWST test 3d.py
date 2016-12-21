# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Using Iris to access data from COAWST (curvilinear grid ROMS model output)

# <codecell>

from IPython.core.display import Iframe
IFRAME('<iframe src=http://scitools.org.uk/iris/ width=800 height=350></iframe>')

# <codecell>

import numpy
import matplotlib.pyplot as plt
import datetime as dt

import iris
import iris.quickplot as qplt
import cartopy.crs as ccrs


# <codecell>

def time_near(cube,start):
    timevar=cube.coord('time')
    itime = timevar.nearest_neighbour_index(timevar.units.date2num(start))
    return timevar.points[itime]

# <codecell>

# DAP URL: USGS COAWST model
# cubes = iris.load('http://geoport.whoi.edu/thredds/dodsC/fmrc/NCEP/ww3/cfsr/4m/best')
#cubes = iris.load('http://geoport.whoi.edu/thredds/dodsC/coawst_4/use/fmrc/coawst_4_use_best.ncd');
temp = iris.load('http://barataria.tamu.edu:8080/thredds/dodsC/NcML/txla_nesting6.nc', 'potential temperature')[0]

# <codecell>

print temp

# <codecell>

# Let's do this above instead..  -rdh.
#temp=cubes[0]
#temp=cubes[32]

# <codecell>

#print temp

# <codecell>

# slice by indices
# use contraints to select geographic subset and nearest time
mytime=dt.datetime(2009,3,1,12)  #specified time...
#mytime=dt.datetime.utcnow()      # .... or now
slice=temp.extract(iris.Constraint(time=time_near(temp,mytime)))
slice=slice[-1,:,:]  # surface
print slice

# <codecell>

def slice_bbox_extract(slice,bbox):
    ''' 
    Extract a subsetted slice inside a lon,lat bounding box
    bbox=[lon_min lon_max lat_min lat_max]
    '''
    data = slice.data
    lons = slice.coord('longitude').points
    lats = slice.coord('latitude').points

    def minmax(v):
        return np.min(v), np.max(v)

    inregion = np.logical_and(np.logical_and(lons > bbox[0], lons < bbox[1]),
                          np.logical_and(lats > bbox[2], lats < bbox[3]))
    # extract the rectangular subarray containing the whole valid region ...
    region_inds = np.where(inregion)
    imin, imax = minmax(region_inds[0])
    jmin, jmax = minmax(region_inds[1])
    subslice = slice[imin:imax+1, jmin:jmax+1]
    return subslice

# <codecell>

# bbox to extract
bbox=[ -71.5, -65.0, 39.5, 46.0]
subslice=slice_bbox_extract(slice,bbox)

# <codecell>

print subslice

# <codecell>

# make the plot
figure(figsize=(12,8))
Z=subslice.data
Zm = ma.masked_where(np.isnan(Z),Z)
ax1 = plt.axes(projection=ccrs.PlateCarree())
ax2=pcolormesh(subslice.coord('longitude').points,subslice.coord('latitude').points,Zm,vmin=0,vmax=20);
dat=slice.coord('time')[0].units.num2date(slice.coord('time')[0].points)
plt.colorbar()
ax1.gridlines(draw_labels=True);
plt.title('Temperature in the Gulf of Maine: %s' % dat)

