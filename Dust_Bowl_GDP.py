# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# #Exploring Climate Data: Past and Future
# ##Roland Viger, Rich Signell, USGS
# First presented at the 2012 Unidata Workshop: Navigating Earth System Science Data, 9-13 July.
# 
# What if you were watching [Ken Burns's "The Dust Bowl"](http://www.pbs.org/kenburns/dustbowl/), saw the striking image below, and wondered: "How much precipitation there really was back in the dustbowl years?"  How easy is it to access and manipulate climate data in a scientific analysis?  Here we'll show some powerful tools that make it easy.

# <codecell>

from IPython.core.display import Image
Image('http://www-tc.pbs.org/kenburns/dustbowl/media/photos/s2571-lg.jpg')

# <markdowncell>

# Above:Dust storm hits Hooker, OK, June 4, 1937. 
# 
# To find out how much rainfall was there during the dust bowl years, we can use the [USGS/CIDA GeoDataPortal (GDP)](http://cida.usgs.gov/climate/gdp/) which can compute statistics of a gridded field within specified shapes, such as county outlines.  Hooker is in Texas County, Oklahoma, so here we use the GDP to compute a historical time series of mean precipitation in Texas County using the PRISM dataset. We then compare to climate forecast projections to see if similar droughts are predicted to occur in the future, and what the impact of different climate scenarios might be. 

# <codecell>

import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import urllib
import os
from IPython.core.display import HTML
import time
import pandas as pd

# <codecell>

cd /usgs/data2/notebook

# <codecell>

import pyGDP
import numpy as np
import matplotlib.dates as mdates

# <markdowncell>

# One way to interface with the GDP is with the interactive web interface, shown below.  In this interface, you can upload a shapefile or draw on the screen to define a polygon region, then you specify the statistics and datasets you want to use via dropdown menus.  

# <codecell>

HTML('<iframe src=http://screencast.com/t/K7KTcaFrSUc width=800 height=600></iframe>')

# <markdowncell>

# Here we use the python interface to the GDP, called PyGDP, which allows for scripting.  You can get the code and documentation at https://github.com/USGS-CIDA/pyGDP.

# <codecell>

# Create a pyGDP object
myGDP = pyGDP.pyGDPwebProcessing()

# <codecell>

# Let's see what shapefiles are already available on the GDP server
# this changes with time, since uploaded shapefiles are kept for a few days
shapefiles = myGDP.getShapefiles()
print 'Available Shapefiles:'
for s in shapefiles:
    print s

# <codecell>

# Is our shapefile there already?
# If not, upload it. 
OKshapeFile = 'upload:OKCNTYD'
if not OKshapeFile in shapefiles:
    shpfile = myGDP.uploadShapeFile('OKCNTYD.zip')

# <codecell>

# Let's check the attributes of the shapefile
attributes = myGDP.getAttributes(OKshapeFile)
print "Shapefile attributes:"
for a in attributes:
    print a

# <codecell>

# In this particular example, we are interested in attribute = 'DESCRIP', 
# which provides the County names for Oklahoma
user_attribute = 'DESCRIP'
values = myGDP.getValues(OKshapeFile, user_attribute)
print "Shapefile attribute values:"
for v in values:
    print v

# <codecell>

# we want Texas County, Oklahoma, which is where Hooker is located
user_value = 'Texas'

# <codecell>

# Let's see what gridded datasets are available for the GDP to operate on
dataSets = myGDP.getDataSetURI()
print "Available gridded datasets:"
for d in dataSets:
    print d[0]

# <codecell>

dataSets[0][0]

# <codecell>

df = pd.DataFrame(dataSets[1:],columns=['title','abstract','urls'])

# <codecell>

df.head()

# <codecell>

print df['title']

# <codecell>

df.ix[20].urls

# <codecell>

# If you choose a DAP URL, use the "dods:" prefix, even
# if the list above has a "http:" prefix.
# For example:  dods://cida.usgs.gov/qa/thredds/dodsC/prism
# Let's see what data variables are in our dataset
dataSetURI = 'dods://cida.usgs.gov/thredds/dodsC/prism'
dataTypes = myGDP.getDataType(dataSetURI)
print "Available variables:"
for d in dataTypes:
    print d

# <codecell>

# Let's see what the available time range is for our data variable
user_dataType = 'ppt'  # precip
timeRange = myGDP.getTimeRange(dataSetURI, user_dataType)
for t in timeRange:
    print t

# <codecell>

timeBegin = '1900-01-01T00:00:00Z'
timeEnd   = '2012-08-01T00:00:00Z'

# <codecell>

# Once we have our shapefile, attribute, value, dataset, datatype, and timerange as inputs, we can go ahead
# and submit our request.
name1='gdp_texas_county_prism.csv'
if not os.path.exists(name1):
    url_csv = myGDP.submitFeatureWeightedGridStatistics(OKshapeFile, dataSetURI, user_dataType, 
          timeBegin, timeEnd, user_attribute, user_value, delim='COMMA', stat='MEAN' )
    f = urllib.urlretrieve(url_csv,name1)

# <codecell>

# load historical PRISM precip
jd,precip=np.loadtxt(name1,unpack=True,skiprows=3,delimiter=',', 
                     converters={0: mdates.strpdate2num('%Y-%m-%dT%H:%M:%SZ')})

# <codecell>

def boxfilt(data,boxwidth):
    from scipy import signal
    import numpy as np
    weights=signal.get_window('boxcar',boxwidth)
    dataf=np.convolve(data,weights/boxwidth,mode='same')
    dataf=np.ma.array(dataf)
    dataf[:boxwidth/2]=np.nan
    dataf[-boxwidth/2:]=np.nan
    dataf=np.ma.masked_where(dataf==np.nan,dataf)
    return dataf

# <codecell>

# PRISM data is monthly:  filter over 36 months
plp=boxfilt(precip,36)

fig=plt.figure(figsize=(12,2), dpi=80) 
ax1 = fig.add_subplot(111)
g1=ax1.plot_date(jd,plp,fmt='b-')
g2=ax1.plot_date(jd,0*jd+np.mean(precip),fmt='k-')
fig.autofmt_xdate()
plt.title('Average Precip for Texas County, Oklahoma, calculated via GDP using PRISM data ')
plt.grid()

# <codecell>

HTML('<iframe src=http://www.ipcc.ch/publications_and_data/ar4/wg1/en/spmsspm-projections-of.html width=900 height=350></iframe>')

# <codecell>

#hayhoe_URI ='dods://cida-eros-thredds1.er.usgs.gov:8082/thredds/dodsC/dcp/conus_grid.w_meta.ncml'
hayhoe_URI ='dods://cida.usgs.gov/thredds/dodsC/dcp/conus'
timeRange = myGDP.getTimeRange(hayhoe_URI, dataType)

# <codecell>

timeRange

# <codecell>

# retrieve the CCSM3 model A1FI "Business-as-Usual" scenario:
name2='gdp_texas_county_ccsm_a1fi.csv'
if not os.path.exists(name2):
    dataType = 'ccsm-a1fi-pr-NAm-grid'
    result2 = myGDP.submitFeatureWeightedGridStatistics(OKshapeFile, hayhoe_URI, dataType,
            timeRange[0],timeRange[1],user_attribute,user_value, delim='COMMA', stat='MEAN' )
    f = urllib.urlretrieve(result2,name2)                                       

# <codecell>

# now retrieve the CCSM3 model B1 "Eco-Friendly" scenario:
time0=time.time();
name3='gdp_texas_county_ccsm_b1.csv'
if not os.path.exists(name3):
    dataType = 'ccsm-b1-pr-NAm-grid'
    result3 = myGDP.submitFeatureWeightedGridStatistics(OKshapeFile, hayhoe_URI, dataType,
            timeRange[0],timeRange[1],user_attribute,user_value, delim='COMMA', stat='MEAN' )
    f = urllib.urlretrieve(result3,name3)
    print('elapsed time=%d s' % (time.time()-time0))

# <codecell>

# Load the GDP result for: CCSM A1FI "Business-as-Usual" scenario:
jd_a1f1,precip_a1f1 = np.loadtxt(name2,unpack=True,skiprows=3,
    delimiter=',',converters={0: mdates.strpdate2num('%Y-%m-%dT%H:%M:%SZ')}) 

# Load the GDP result for:  CCSM B1 "Eco-Friendly" scenario:
jd_b1,precip_b1     = np.loadtxt(name3,unpack=True,skiprows=3,
    delimiter=',',converters={0: mdates.strpdate2num('%Y-%m-%dT%H:%M:%SZ')}) 

# <codecell>

# Hayhoe climate downscaling is hourly: filter over 1080 days (36 months)
plp_a1f1=boxfilt(precip_a1f1,1080)
plp_b1=boxfilt(precip_b1,1080)
#plp_a1b_c=boxfilt(precip_a1b_c,36)

# <codecell>

fig=plt.figure(figsize=(15,3), dpi=80) 
ax1 = fig.add_subplot(111)
fac=30. # convert from mm/day to mm/month (approx)
# plot A1FI scenario
g1=ax1.plot_date(jd_a1f1,plp_a1f1*fac,fmt='b-')
# plot B1 scenario 
g2=ax1.plot_date(jd_b1,plp_b1*fac,fmt='g-')
# plot PRISM data
g3=ax1.plot_date(jd,plp,fmt='r-')  # for some reason when I add this the labels get borked
ax1.xaxis.set_major_locator(mdates.YearLocator(10,month=1,day=1))
ylabel('mm/month')
plt.title('Average Precip for Texas County, Oklahoma, calculated via GDP using Hayhoe Downscaled GCM ')
grid()
legend(('A1FI','B1','PRISM Data'),loc='upper left')

# <markdowncell>

# As we can see from the above plot, the CCSM model is not doing very well simulating the precipitation in Texas County, OK during the period when the simulation and data overlap (1960-present). This makes us less confident about the future precipitation simulations, and suggests we might need to try some different climate models and learn a bit more about climate simulations.  When we do learn more, we find out that models have known biases in certain regions. 

# <markdowncell>

# Now just to show that we can access more than climate model time series, let's extract precipitation data from a dry winter (1936-1937) and a normal winter (2009-2010) for Texas County and look at the spatial patterns.  
# 
# We'll use the netCDF4-Python library, which allows us to open OPeNDAP datasets just as if they were local NetCDF files. 

# <codecell>

import netCDF4
url='http://cida.usgs.gov/thredds/dodsC/prism'
box = [-102,36.5,-100.95,37]  # Bounding box for Texas County, Oklahoma
#box = [-104,36.,-100,39.0]  # Bounding box for larger dust bowl region

# <codecell>

# define a mean precipitation function, here hard-wired for the PRISM data
def mean_precip(nc,bbox=None,start=None,stop=None):
    lon=nc.variables['lon'][:]
    lat=nc.variables['lat'][:]
    tindex0=netCDF4.date2index(start,nc.variables['time'],select='nearest')
    tindex1=netCDF4.date2index(stop,nc.variables['time'],select='nearest')
    bi=(lon>=box[0])&(lon<=box[2])
    bj=(lat>=box[1])&(lat<=box[3])
    p=nc.variables['ppt'][tindex0:tindex1,bj,bi]
    latmin=np.min(lat[bj])
    p=np.mean(p,axis=0)
    lon=lon[bi]
    lat=lat[bj]
    return p,lon,lat

# <codecell>

nc = netCDF4.Dataset(url)
p,lon,lat = mean_precip(nc,bbox=box,start=datetime.datetime(1936,11,1,0,0),
                        stop=datetime.datetime(1937,4,1,0,0))
p2,lon,lat = mean_precip(nc,bbox=box,start=datetime.datetime(2009,11,1,0,0),
                       stop=datetime.datetime(2010,4,1,0,0))
latmin = np.min(lat)

# <codecell>

# look at March 1935, just before black sunday on April 14, 1935
nc = netCDF4.Dataset(url)
p,lon,lat = mean_precip(nc,bbox=box,start=datetime.datetime(1935,3,1,0,0),
                        stop=datetime.datetime(1935,4,1,0,0))
p2,lon,lat = mean_precip(nc,bbox=box,start=datetime.datetime(2009,3,1,0,0),
                       stop=datetime.datetime(2009,4,1,0,0))
latmin = np.min(lat)

# <codecell>

import cartopy.crs as ccrs
import cartopy.feature as cfeature
states_provinces = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='50m',
        facecolor='none')
ax = plt.axes(projection=ccrs.PlateCarree())
pc = ax.pcolormesh(lon, lat, p, cmap=plt.cm.jet_r)
ax.add_feature(states_provinces,edgecolor='gray')
ax.text(-101,36.86,'Hooker',align='left')
ax.plot(-101,36.86,'o')
cb = plt.colorbar(pc, cax=cbax,  orientation='vertical')
cb.set_label('Precip (mm/month)')

# <codecell>

fig = plt.figure(figsize=(12,5), dpi=80) 
ax = fig.add_axes([0.1, 0.15, 0.3, 0.8])
pc = ax.pcolormesh(lon, lat, p, cmap=plt.cm.jet_r)
ax.set_aspect(1.0/np.cos(latmin * np.pi / 180.0))
plt.title('Precip in Texas County, Oklahoma: Winter 1936-1937')

cbax = fig.add_axes([0.45, 0.3, 0.03, 0.4])
cb = plt.colorbar(pc, cax=cbax,  orientation='vertical')
cb.set_label('Precip (mm/month)')

ax2 = fig.add_axes([0.6, 0.15, 0.3, 0.8])
pc2 = ax2.pcolormesh(lon, lat, p2, cmap=plt.cm.jet_r)
ax2.set_aspect(1.0/np.cos(latmin * np.pi / 180.0))
plt.title('Precip in Texas County, Oklahoma: Winter 2009-2010')

cbax2 = fig.add_axes([0.95, 0.3, 0.03, 0.4])
cb2 = plt.colorbar(pc2, cax=cbax2,  orientation='vertical')
cb2.set_label('Precip (mm/month)')


plt.show()

# <markdowncell>

# From the above patterns, we can see that it's significantly drier in the northwestern part of the county in both years.  We can also see that the *maximum* precip in 1936-1937 is less than the *minimum* precipitation in 2009-2010.  We can see just how much each part of the county was drier by doing the different plot below. 

# <codecell>

fig=plt.figure(figsize=(12,5), dpi=80) 
ax3 = fig.add_axes([0.1, 0.15, 0.3, 0.8])
pc3 = ax3.pcolormesh(lon, lat, p2-p, cmap=plt.cm.jet_r)
ax3.set_aspect(1.0/np.cos(latmin * np.pi / 180.0))
plt.title('Precip in Texas County, Oklahoma: Difference 2010-1937')

cbax3 = fig.add_axes([0.45, 0.3, 0.03, 0.4])
cb3 = plt.colorbar(pc3, cax=cbax3,  orientation='vertical')
cb3.set_label('Precip (mm/month)')

# <markdowncell>

# The above plot shows that relative to 2010, the drought during 1937 had the biggest different in precip in the northeastern part of the county.

# <markdowncell>

# Hopefully this demo inspires other investigation of historical and projected climate data using the GDP and Python.  

