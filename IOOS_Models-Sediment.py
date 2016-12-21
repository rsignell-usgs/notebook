# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Using Iris to access data from US-IOOS models

# <codecell>

import datetime as dt
import time
import matplotlib.pyplot as plt
import numpy as np
%matplotlib inline

# <markdowncell>

# Note: `iris` is not a default package in Wakari or Anaconda, [but installation is easy](https://github.com/ioos/conda-recipes/issues/11). 

# <codecell>

# use contraints to select nearest time
mytime=dt.datetime(2015,1,29,17)  #specified time...
#mytime=dt.datetime.utcnow()      # .... or now
print mytime

# <codecell>

# [lon_min, lon_max, lat_min, lat_max]  for subsetting and plotting
bbox=[-72,-63,39,46]

# <codecell>

import iris

# <codecell>

def find_timevar(cube):
    """Return the variable attached to
    time axis and rename it to time."""
    try:
        cube.coord(axis='T').rename('time')
        print('Renaming {} to time'.format(cube.coord('time').var_name))
    except:
        pass
    timevar = cube.coord('time')
    return timevar

# <codecell>

def time_near(cube, start):
    """Return the nearest time to `start`.
    TODO: Adapt to the new slice syntax"""
    timevar = find_timevar(cube)
    try:
        time1 = timevar.units.date2num(start)
        itime = timevar.nearest_neighbour_index(time1)
    except IndexError:
        itime = -1
    return timevar.points[itime]

# <codecell>

def minmax(v):
    return np.min(v), np.max(v)

# <codecell>

def var_lev_date(url=None,var=None,mytime=None,lev=0,subsample=1,bbox=None):
    '''
    specify lev=None if the variable does not have layers
    '''
    time0= time.time()
#    cube = iris.load_cube(url,iris.Constraint(name=var.strip()))[0]
    cube = iris.load_cube(url,var)
#    cube = iris.load(url,var)[0]
#    print cube.coord('time')

    try:
        cube.coord(axis='T').rename('time')
    except:
        pass
    slice = cube.extract(iris.Constraint(time=time_near(cube,mytime)))

    if bbox is None:
        imin=0
        jmin=0
        imax=-2
        jmax=-2
    else:
        lats=slice.coord(axis='Y').points
        lons=slice.coord(axis='X').points
        inregion = np.logical_and(np.logical_and(lons > bbox[0], lons < bbox[1]),
                          np.logical_and(lats > bbox[2], lats < bbox[3]))
        # extract the rectangular subarray containing the whole valid region ...
        region_inds = np.where(inregion)
        jmin, jmax = minmax(region_inds[0])
        imin, imax = minmax(region_inds[1])
    if lev is None:
        slice = slice[jmin:jmax+1:subsample,imin:imax+1:subsample]  
    else:
        slice = slice[lev,jmin:jmax+1:subsample,imin:imax+1:subsample]  
    print 'slice retrieved in %f seconds' % (time.time()-time0)
    return slice

# <codecell>

def myplot(slice,model=None,crange=None,bbox=None,ptype='linear'):
    """ 
    bbox = [lon_min, lon_max, lat_min, lat_max]
    crange = [vmin, vmax]  
    ptype = 'linear' or 'log10'
    model =  dataset name  (string), e.g. 'COAWST US-EAST'
    """
    fig=plt.figure(figsize=(12,8))
    lat=slice.coord(axis='Y').points
    lon=slice.coord(axis='X').points
    time=slice.coord('time')[0]
    ax1 = plt.subplot(111,aspect=(1.0/cos(mean(lat)*pi/180.0)))
    
    if ptype is 'linear':
        data = ma.masked_invalid(slice.data)
    elif ptype is 'log10':
        data = np.log10(ma.masked_invalid(slice.data))
    else:
        raise
    if crange is None:
        im = ax1.pcolormesh(lon,lat,data);           
    else:
        im = ax1.pcolormesh(lon,lat,data,vmin=crange[0],vmax=crange[-1]);
    if bbox is not None:
        ax1.set_xlim(bbox[:2])
        ax1.set_ylim(bbox[2:])
    fig.colorbar(im,ax=ax1)
    ax1.grid()
    date=time.units.num2date(time.points)
    date_str=date[0].strftime('%Y-%m-%d %H:%M:%S %Z')
    plt.title('%s: %s: %s' % (model,slice.long_name,date_str));

# <codecell>

ds_name='VIIRS Data'
url='http://www.star.nesdis.noaa.gov/thredds//dodsC/CoastWatch/VIIRS/Rrs672/Daily/NE05'
var='Remote sensing reflectance at 672 nm'
lev=0
slice=var_lev_date(url=url,var=var, mytime=mytime, lev=lev, subsample=2,bbox=bbox)

# <codecell>

myplot(slice,model=ds_name,bbox=bbox,ptype='log10',crange=[-3,-1])

# <codecell>

model='USGS/COAWST Model'
url='http://geoport.whoi.edu/thredds/dodsC/coawst_4/use/fmrc/coawst_4_use_best.ncd'
var='suspended noncohesive sediment, size class 06'
lev=-1

#slice=var_lev_date(url=url,var=var, mytime=mytime, lev=lev, subsample=1,bbox=[-72,-63,39,46])

# if we issue the above command to slice out data in a specified bounding box, 
# it actually takes longer (34 seconds) because we have a curvlinear grids
# and the whole 2D lon,lat fields must be downloaded to determine the index range to extract
# of course if were doing this again, we could just use the already calculated index ranges, and 
# it would be faster.  But since we just need this one slice, we here just download the whole thing

slice=var_lev_date(url=url,var=var, mytime=mytime, lev=lev, subsample=1)

# <codecell>

myplot(slice,model=model,bbox=bbox,ptype='log10',crange=[-12,-1])

# <codecell>

print slice

# <codecell>


