# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# #Read data from MPALA ERDDAP
# Exploring use of Python to formulate ERDDAP data requests and process the responses.  

# <codecell>

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
%matplotlib inline

# <markdowncell>

# If you go to the ERDDAP TableDap page, you can select which variables you want, the time ranges, etc, and then select how you want to download the data.  You can either then download the data, or just copy the URL that would download the data.   That URL can therefore be used as the basis of a custom data query, as shown below.  We simply generated a URL, then replaced the time and data requested with python variables.   
# 
# Note: If you just see a blank box below, you might have to tell your browser to "allow unsafe script".  In Chrome it's a little shield that shows up on the right hand side of the address bar.

# <codecell>

from IPython.display import IFrame
IFrame('http://geoport.whoi.edu/erddap/tabledap/tower_65ce_ba2b_9a66.html', width='100%', height=450)

# <codecell>

#select the variables you want
vars='Tsoil10cmGrass_Avg,Tsoil20cmGass_Avg'
# Use ERDDAP's built-in relative time functionality to get last 48 hours:
start='now-7days'
stop='now'
# or specify a specific period:
start = '2013-05-06T00:00:00Z'
stop =  '2013-06-07T00:00:00Z'

# <codecell>

#construct the ERDDAP URL
url='http://geoport.whoi.edu/erddap/tabledap/tower_65ce_ba2b_9a66.csvp?\
time,%s&time>=%s&time<=%s' % (vars,start,stop)
df = pd.read_csv(url,index_col=0,parse_dates=True)

# <codecell>

df.plot(figsize=(12,4));

# <codecell>

# List last ten records
df.tail(10)

# <codecell>

df.describe()

# <markdowncell>

# Use ERDDAP to make a plot

# <codecell>

from IPython.display import Image
url='http://geoport.whoi.edu/erddap/tabledap/tower_65ce_ba2b_9a66.png?time,TsoilOpen_Avg&time%3E=2014-08-27T00:00:00Z&time%3C=2014-09-03T00:00:00Z&.draw=lines&.color=0x000000'
Image(url=url,format=u'png')

# <codecell>

!git push

# <codecell>

pwd

# <codecell>

cd /usgs/data2/notebook/ERDDAP

# <codecell>


