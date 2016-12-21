# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LinearSegmentedColormap
from mpl_toolkits.basemap import Basemap, cm
from netCDF4 import Dataset
import netCDF4
import scipy.ndimage as ndimage
import time
from time import mktime
from datetime import datetime, timedelta
%matplotlib inline

# <codecell>

############################################################################
# four_panel.py
# By: Kevin Goebbert
#
# Date: 5 October 2014
#
# This script uses 1 deg GFS model output via nomads URL to plot the 192-h
# forecast in a four panel plot.
#
# UL Panel - MSLP, 1000-500 hPa Thickness, Precip (in)
# UR Panel - 850-hPa Heights and Temperature (C)
# LL Panel - 500-hPa Heights and Absolute Vorticity (*10^-5 s^-1)
# LR Panel - 300-hPa Heights and Wind Speed (kts)
#
# Created using the Anaconda Distribution of Python 2.7
# Install Anaconda from http://continuum.io/downloads
# Then install binstar to use the conda package management software
#      conda install binstar
#
# Then use conda to install two packages not a part of the main distribution.
#      conda install basemap
#
#      conda install netcdf4
#
#############################################################################

# <codecell>

#############################################################################
# A class definition to help with the colormap for 850-hPa Temps.
class MidpointNormalize(Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
       self.midpoint = midpoint
       Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
# I'm ignoring masked values and all kinds of edge cases to make a
# simple example...
       x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.50, 1]
       return np.ma.masked_array(np.interp(value, x, y))
#############################################################################

# <codecell>

# Choose a model - right now this program is based on the 0.5 deg GFS output,
# there shouldn't be much to change for other GFS resolution sets, mainly smoothing

# To modify for another model you would need to know variable names and determine
# what array elements are associated with your view window and vertical levels.

# Uncomment the gfs model of your choice below!
#model = 'gfs_2p50'
#model = 'gfs_1p00'
model = 'gfs_0p50'
#model = 'gfs_0p25'
#print(model[0:3])

# Get the current hour from the computer and choose the proper model
# initialization time.
# These times are set based on when they appear on the nomads server.
currhr = int(datetime.utcnow().strftime('%H'))
if currhr >= 4 and currhr < 11:
   run = '00'
elif currhr >= 11 and currhr < 17:
   run = '06'
elif currhr >= 17 and currhr < 23:
   run = '12'
else:
   run = '18'

# <codecell>

# Setting some time and date strings for use in constructing the filename and for output.
# fdate looks like ... 20141005 ... and is used in constructing the filename
# date looks like ... 2014-10-05 00:00:00 and is used for output
if (run == '18') and (currhr < 3): # because we need to go back to the previous day
   date1 = (datetime.utcnow() - timedelta(hours=24)).strftime('%Y%m%d') + run
   fdate = (datetime.utcnow() - timedelta(hours=24)).strftime('%Y%m%d')
else:    
   date1 = datetime.utcnow().strftime('%Y%m%d') + run
   fdate = datetime.utcnow().strftime('%Y%m%d')
   
date = time.strptime(date1, "%Y%m%d%H")
date = datetime.fromtimestamp(mktime(date))

# If you wanted to run a past date (I think they keep a week or two on the website), then
# just uncomment the following three lines to not use the current model run.
#date  = '20141005 00:00:00'
#fdate = '20141005'
#run   = '00'
print date

# <codecell>

# Here we are using the NETCDF-4 OPENDAP feature to get the data from a URL.
# You need an internet connection to be able to use this feature.
data=Dataset("http://nomads.ncep.noaa.gov:9090/dods/%s/%s%s/%s_%sz" %\
        (model,model[0:3],fdate,model,run))

# Pulling in only the data we need.
lats  = data.variables['lat']
lons  = data.variables['lon']
levs  = data.variables['lev']   # 26 levels, 850 = [5], 500 = [12], 300 = [16]
#print levs[0],levs[5],levs[16]
times  = data.variables['time']
print("The time resolution is "+str(times.resolution)+" days")
time_step = 24*times.resolution
print("The time step between forecast hours is "+str(time_step)+" hours")

# Set US Bounds for GFS 1 deg data, these are the reference index values
#iLLlat = 110
#iLLlon = 220
iLLlat = np.where(np.array(lats)==20)[0][0]
iLLlon = np.where(np.array(lons)==220)[0][0]


#iURlat = 160
#iURlon = 310
iURlat = np.where(np.array(lats)==70)[0][0]
iURlon = np.where(np.array(lons)==310)[0][0]

# The following lines will tell you want the lat and lon values are for the 
# specific Lower Left (LL) and Upper Right (UR) corners of the US area.
#LLlat = lats[iLLlat]
#LLlon = lons[iLLlon]
#URlat = lats[iURlat]
#URlon = lons[iURlon]

#print LLlat,LLlon
#print URlat,URlon

lev1000 = np.where(np.array(levs)==1000)[0][0]
lev850 = np.where(np.array(levs)==850)[0][0]
lev700 = np.where(np.array(levs)==700)[0][0]
lev500 = np.where(np.array(levs)==500)[0][0]
lev300 = np.where(np.array(levs)==300)[0][0]


#hghts = data.variables['hgtprs'][0:24,0:20,iLLlat:iURlat,iLLlon:iURlon]
hght850 = data.variables['hgtprs'][:,lev850,iLLlat:iURlat,iLLlon:iURlon]
temp850 = data.variables['tmpprs'][:,lev850,iLLlat:iURlat,iLLlon:iURlon]
#rh700   = data.variables['rhprs'][:,lev700,iLLlat:iURlat,iLLlon:iURlon]
print "Got the 850-hPa Heights and TMPK"

hght500 = data.variables['hgtprs'][:,lev500,iLLlat:iURlat,iLLlon:iURlon]
avor500 = data.variables['absvprs'][:,lev500,iLLlat:iURlat,iLLlon:iURlon]
#uwnd_500  = data.variables['ugrdprs'][:,12,iLLlat:iURlat,iLLlon:iURlon]
#vwnd_500  = data.variables['vgrdprs'][:,12,iLLlat:iURlat,iLLlon:iURlon]
print "Got the 500-hPa Heights and AVOR"

hght300 = data.variables['hgtprs'][:,lev300,iLLlat:iURlat,iLLlon:iURlon]
uwnd_300  = data.variables['ugrdprs'][:,lev300,iLLlat:iURlat,iLLlon:iURlon]
vwnd_300  = data.variables['vgrdprs'][:,lev300,iLLlat:iURlat,iLLlon:iURlon]
print "Got the 300-hPa Heights, UWND, and VWND"

mslp  = data.variables['prmslmsl'][:,iLLlat:iURlat,iLLlon:iURlon]
#temp2m = data.variables['tmpsfc'][:,iLLlat:iURlat,iLLlon:iURlon]
hght1000 = data.variables['hgtprs'][:,lev1000,iLLlat:iURlat,iLLlon:iURlon]
precip   = data.variables['apcpsfc'][:,iLLlat:iURlat,iLLlon:iURlon]
print "Got the MSLPs, 1000-hPa Heights, and SFC Precip"
#uwnd10= data.variables['ugrd10m'][:,iLLlat:iURlat,iLLlon:iURlon]
#print "Got the 10 m UWND"
#vwnd10= data.variables['vgrd10m'][:,iLLlat:iURlat,iLLlon:iURlon]
#print "Got the 10 m VWND"

# <codecell>

# For a few variables we want to smooth the data to remove non-synoptic scale wiggles.
Z_1000 = ndimage.gaussian_filter(hght1000, sigma=1.5, order=0)
Z_850 = ndimage.gaussian_filter(hght850, sigma=1.5, order=0)
Z_500 = ndimage.gaussian_filter(hght500, sigma=1.5, order=0)
Z_300 = ndimage.gaussian_filter(hght300, sigma=1.5, order=0)
pmsl = ndimage.gaussian_filter(mslp/100., sigma=1.5, order=0)

# <codecell>

# Convert data to common formats
tmpc850 = temp850 - 273.15
#tmpf2m = (9./5.)*(temp2m - 273.15) + 32.0
avor500 = avor500 *10**5
wspd300 = np.sqrt(uwnd_300**2 + vwnd_300**2)*1.94384
pcpin   = precip * .0393700787

# Set number of forecast hours from hght850 data
fhours = np.shape(times)[0]
print("Number of steps in the loop for all forecast hours in the dataset = "+str(fhours))

# Set counter intervals for various parameters.
clevpmsl = np.arange(900,1100,4)
#clevtmpf2m = np.arange(0,120,2)
clev850 = np.arange(1200,1800,30)
clevrh700 = [70,80,90]
clevtmpc850 = np.arange(-30,40,2)
clev500 = np.arange(5100,6000,60)
clevavor500 = [-4,-3,-2,-1,0,7,10,13,16,19,22,25,28,31,34,37,40,43,46]
clev300 = np.arange(8160,10080,120)
clevsped300 = np.arange(50,230,20)
clevprecip = [0,0.01,0.03,0.05,0.10,0.15,0.20,0.25,0.30,0.40,0.50,0.60,0.70,0.80,0.90,1.00,1.25,1.50,1.75,2.00,2.50]

# Colors for Vorticity
colorsavor500 = ('#660066', '#660099', '#6600CC', '#6600FF', 'w', '#ffE800', '#ffD800', '#ffC800', '#ffB800', '#ffA800', '#ff9800', '#ff8800', '#ff7800', '#ff6800', '#ff5800', '#ff5000', '#ff4000', '#ff3000')

# Subset the lats and lons from the model according to view desired.
clats1 = lats[iLLlat:iURlat]
clons1 = lons[iLLlon:iURlon]

# Shift the grid with US in negative longitudes
for i in range(0,len(clons1)):
   if clons1[i] > 180:
      clons1[i] = clons1[i] - 360.0

# Make a grid of lat/lon values to use for plotting with Basemap.
clats, clons = np.meshgrid(clons1, clats1)

# <codecell>

# Make Plot
Basemap.latlon_default=True

# Set your view for the image, which can be different than your the data you bring in for your array.
m = Basemap(llcrnrlon=-135,llcrnrlat=20,urcrnrlon=-55,urcrnrlat=60,projection='mill',resolution='l')

# Loop over the forecast hours. Current setting is use all 192-h at the 1 deg resolution.
for fh in range(0,fhours):
  fig=plt.figure(1,figsize=(17.,12.))

# Following line is to get wind barbs properly on the correct projection.
# udat, vdat, xv, yv = m.transform_vector(uwnd_500[0,:,:],vwnd_500[0,:,:],clons1,clats1,15,21,returnxy=True)

# Upper-left panel MSLP, 1000-500 hPa Thickness, Precip (in)
  plt.subplot(221)
  plt.subplots_adjust(bottom=0, left=.01, right=.99, top=.99, hspace=.5, wspace = 0.2)
  m.drawcoastlines(linewidth=0.5)
  m.drawcountries(linewidth=0.5)
  m.drawstates(linewidth=0.5)
  cmap = cm.s3pcpn_l
  if fh % 2 != 0:
     cf = m.contourf(clats,clons,pcpin[fh,:,:],clevprecip,cmap=cmap,latlon=True)
  else:
     cf = m.contourf(clats,clons,pcpin[fh,:,:]-pcpin[fh-1,:,:],clevprecip,cmap=cmap,latlon=True)
  cbar = plt.colorbar(cf,orientation='horizontal',extend='both',aspect=65,shrink=0.913,pad=0,extendrect='True')
  cs2 = m.contour(clats,clons,Z_500[fh,:,:]-Z_1000[fh,:,:],clev500,colors='r',linewidths=1.5,linestyles='dashed',latlon=True)
  cs  = m.contour(clats,clons,pmsl[fh,:,:],clevpmsl,colors='k',linewidths=1.5,latlon=True)
  plt.clabel(cs, fontsize=8, inline=1, inline_spacing=10, fmt='%i', rightside_up=True)
  plt.clabel(cs2, fontsize=7, inline=1, inline_spacing=10, fmt='%i', rightside_up=True)
  plt.title('MSLP (hPa), 2m TMPF, and Precip',loc='left')
  plt.title('VALID: %s' %(date),loc='right')
# Upper-right panel 850-hPa Heights and Temp (C)
  plt.subplot(222)
  plt.subplots_adjust(bottom=0, left=.01, right=.99, top=.99, hspace=.5,wspace = 0.2)
  m.drawcoastlines(linewidth=0.5)
  m.drawcountries(linewidth=0.5)
  m.drawstates(linewidth=0.5)
  cmap = plt.cm.jet
  norm = MidpointNormalize(midpoint=10)
  cf = m.contourf(clats,clons,tmpc850[fh,:,:],clevtmpc850,cmap=cmap,norm=norm,extend='both',latlon=True)
  cbar = plt.colorbar(cf,orientation='horizontal',extend='both',aspect=65,shrink=0.913,pad=0,extendrect='True')
  cs = m.contour(clats,clons,Z_850[fh,:,:],clev850,colors='k',linewidths=1.5,latlon=True)
  plt.clabel(cs, fontsize=8, inline=1, inline_spacing=10, fmt='%i', rightside_up=True)
  plt.title('850-hPa HGHTs (m) and TMPC',loc='left')
  plt.title('VALID: %s' %(date),loc='right')


# Lower-left panel 500-hPa Heights and AVOR
  plt.subplot(223)
  plt.subplots_adjust(bottom=0, left=.01, right=.99, top=.95, hspace=.005, wspace = 0.1)
  m.drawcoastlines(linewidth=0.5)
  m.drawcountries(linewidth=0.5)
  m.drawstates(linewidth=0.5)
  #cmap = plt.cm.get_cmap("YlOrBr")
  cf = m.contourf(clats,clons,avor500[fh,:,:],clevavor500,colors=colorsavor500,extend='both',latlon=True)
  cbar = plt.colorbar(cf,orientation='horizontal',extend='both',aspect=65,shrink=0.913,pad=0,extendrect='True')
  cs = m.contour(clats,clons,Z_500[fh,:,:],clev500,colors='k',linewidths=1.5,latlon=True)
  ##wind = m.barbs(xv[::thin],yv[::thin],udat[::thin],vdat[::thin],length=6,barbcolor='k',axes=ax)
  ##wind = m.barbs(xv,yv,udat,vdat,length=6,barbcolor='k')
  plt.clabel(cs, fontsize=8, inline=1, inline_spacing=10, fmt='%i', rightside_up=True)
  plt.title('500-hPa HGHTs (m) and AVOR ($*10^5$ $s^{-1}$)',loc='left')
  plt.title('VALID: %s' %(date),loc='right')


# Lower-right panel 300-hPa Heights and Wind Speed (kts)
  plt.subplot(224)
  plt.subplots_adjust(bottom=0, left=.01, right=.99, top=.95, hspace=.005, wspace = 0.1)
  m.drawcoastlines(linewidth=0.5)
  m.drawcountries(linewidth=0.5)
  m.drawstates(linewidth=0.5)
  cmap = plt.cm.get_cmap("BuPu")
  cf = m.contourf(clats,clons,wspd300[fh,:,:],clevsped300,cmap=cmap,extend='max',latlon=True)
  cbar = plt.colorbar(cf,orientation='horizontal',extend='max',aspect=65,shrink=0.913,pad=0,extendrect='True')
  cs = m.contour(clats,clons,Z_300[fh,:,:],clev300,colors='k',linewidths=1.5,latlon=True)
  plt.clabel(cs, fontsize=8, inline=1, inline_spacing=10, fmt='%i', rightside_up=True)
  plt.title('300-hPa HGHTs (m) and SPED (kts)',loc='left')
  plt.title('VALID: %s' %(date),loc='right')

# To make a nicer layout use plt.tight_layout()
  plt.tight_layout()

# Add room at the top of the plot for a main title
  plt.subplots_adjust(top=.90)
  plt.suptitle('%s GFS %sZ' %(fdate,run),fontsize=20)

# Save the figure to a unique name every time.
  plt.savefig('/tmp/500hgt_f%02d.png' % (fh*time_step),dpi=150)

# Close the figure to clear for the next panel.
  plt.close()

# Step forward in time for the output date and display to screen.
  date = date+timedelta(hours=time_step)
  print date

# <codecell>

img = plt.imread('/tmp/500hgt_f%02d.png' % (fh*time_step))
fig = plt.figure(figsize=(30,30))
plt.imshow(img)

# <codecell>


