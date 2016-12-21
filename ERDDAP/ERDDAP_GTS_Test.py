# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# #Experimenting with GTS data from ERDDAP
# Exploring use of Python to formulate ERDDAP image and data REST requests and process the responses.  

# <codecell>

from IPython.display import IFrame
IFrame('http://osmc.noaa.gov:8180/erddap/tabledap/OSMC_PROFILERS.html', width='100%', height=450)

# <codecell>

##Initialize

# <codecell>

import urllib2
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
%matplotlib inline

# <codecell>

# dictionary for valid parameter_name 
d={'sea_water_temperature':'ZTMP', 'sea_water_salinity':'ZSAL'}

# <codecell>

# Specify variable to retrieve: 
param=d['sea_water_temperature']

# Get data shallower than this water depth:
depth_max = 10   

# Use ERDDAP's built-in relative time functionality to get last 48 hours:
start='now-24hours'
stop='now'
# or specify a specific period:
#start = '2013-05-06T00:00:00Z'
#stop =  '2013-05-07T00:00:00Z'

# <markdowncell>

# ##Retrieve an image from ERDDAP

# <codecell>

# Construct URL for large PNG:
url='http://osmc.noaa.gov:8180/erddap/tabledap/OSMC_PROFILERS\
.largePng?longitude,latitude,observation_value\
&time>=%s&time<=%s&parameter_name="%s"&observation_depth<=%d&.trim=5&\
.draw=markers&.marker=5|6&.color=0x000000&.colorBar=|||||' % (start,stop,param,depth_max)

# <codecell>

# Read the image
im = plt.imread(urllib2.urlopen(url),format='png')

# <codecell>

# Display the image
plt.figure(figsize=(12,8))
plt.imshow(im)   
plt.axis('off');

# <markdowncell>

# ##Obtain data from ERDDAP

# <codecell>

# Construct URL for CSV data:
url='http://osmc.noaa.gov:8180/erddap/tabledap/OSMC_PROFILERS\
.csv?time,longitude,latitude,observation_depth,observation_value\
&time>=%s&time<=%s&parameter_name="%s"&observation_depth<=%d' % (start,stop,param,depth_max)

# <codecell>

# Load the CSV data directly into Pandas
df = pd.read_csv(url,index_col='time',parse_dates=True,skiprows=[1])  # skip the units row 

# <codecell>

# List last ten records
df.tail(10)

# <codecell>

df['longitude']

# <codecell>

df.plot()

# <codecell>


