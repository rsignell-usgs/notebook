# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# **Task:**
# 
#     Work with data interactively
#    
# **Solution:**
# 
#     IPython widgets, interact

# <markdowncell>

# [Notebook file](http://nbviewer.ipython.org/urls/raw.github.com/koldunovn/earthpy.org/master/content/notebooks/pyncview_pm.ipynb)

# <markdowncell>

# I always wanted to write a GUI to explore my data. This is probably one of the things that you can't get rid of as a former hardcore Windows user. You need all this buttons and sliders and check boxes, or at least you think you do. But every time I looked at GUI toolkits for python I was bored after 10 minutes of reading. I just want to show the plot and control couple of variables, and in order to do so I have to learn first how to place elements on the canvas, create handlers and so on and so forth. Boring and not worth it.
# 
# Now with IPython 2.0 widgets and `interact` command my dream come true - I can build a GUI for my data visualisation basically with one line of code. Below I will show how to create simple interactive visualization of geophysical variables from netCDF files. It is sort of quick and dirty replacement for great [ncview program](http://meteora.ucsd.edu/~pierce/ncview_home_page.html), but at the same time it allows you to have much more control over how and what to display.
# 
# **This notebook is going to work properly only in IPython >= 2.0, and you would have to run it on your computer - web version will not be able to show you the widgets.**

# <markdowncell>

# Necessary inputs:

# <codecell>

from netCDF4 import Dataset, num2date, date2num
from IPython.html.widgets import *
%matplotlib inline

# <markdowncell>

# First let's have a look at simple sine wave with frequency `f`

# <codecell>

x=linspace(0,1,100)
f=2

# <codecell>

plot(x,sin(2*pi*x*f));

# <markdowncell>

# We can also create a function out of this line and provide frequency as an argument:

# <codecell>

def pltsin(f):
    plot(x,sin(2*pi*x*f))

# <markdowncell>

# In order to plot with different frequencies we have to always change the value of input argument:

# <codecell>

pltsin(9)

# <markdowncell>

# Bet there is a better way to do this - use `interact`. You give it the name of the function as a first argument, and parameter that you would like to vary (`f` in our case) with some limits (from 1 to 10) and step (0.1).

# <codecell>

interact(pltsin, f=(1,10,0.1));

# <markdowncell>

# Now you can interactively change frequency and immediately see the result. This slider will work with both mouse and arrow keys.

# <markdowncell>

# Let’s add another parameter - amplitude (`a`):

# <codecell>

def pltsin(f, a):
    plot(x,a*sin(2*pi*x*f))
    ylim(-10,10)

# <codecell>

interact(pltsin, f=(1,10,0.1), a=(1,10,1));

# <markdowncell>

# Now we have to sliders, and we can vary two parameters independently.

# <markdowncell>

# Now for something completely different. We going to explore netCDF data with `interact`, but first we have to download them. Here is a little script, that will download daily air temperature, relative humidity, and wind components from NCEP reanalysis:

# <codecell>

variabs = ['air', 'uwnd', 'vwnd', 'rhum']
for vvv in variabs:
    for i in range(2000,2010):
        !wget ftp://ftp.cdc.noaa.gov/Datasets/ncep.reanalysis.dailyavgs/surface/{vvv}.sig995.{i}.nc

# <markdowncell>

# First consider simplest one file case. We open the file:

# <codecell>

f = Dataset('air.sig995.2000.nc')

# <markdowncell>

# Get our variable:

# <codecell>

air = f.variables['air']

# <markdowncell>

# And display first time step:

# <codecell>

imshow(air[0,:,:])

# <markdowncell>

# Obvious thing to do is to browse through days. We make our plotting function:

# <codecell>

def sh(time):
    imshow(air[time,:,:])

# <markdowncell>

# That will take day's number as an argument:

# <codecell>

sh(0)

# <markdowncell>

# And make it interactive:

# <codecell>

interact(sh, time=(0,355,1));

# <markdowncell>

# But what if we would like to switch between variables? We can do this by adding another argument (we just open different files):

# <codecell>

def sh(var='air', time=0):
    f = Dataset(var+'.sig995.2000.nc')
    vv = f.variables[var]
    imshow(vv[time,:,:])

# <markdowncell>

# For our `interact` function we also have to have list of all possible variables:

# <codecell>

variabs = ['air', 'uwnd', 'vwnd', 'rhum']

# <codecell>

interact(sh, time=(0,355,1), var=variabs);

# <markdowncell>

# Since we give is a list, `interact` creates not a slider, but drop-down list.

# <markdowncell>

# Let's add years to the picture:

# <codecell>

def sh(year='2000',var='air', time=0):
    f = Dataset(var+'.sig995.'+year+'.nc')
    vv = f.variables[var]
    imshow(vv[time,:,:])

# <markdowncell>

# I don't want to select years with slider, I want them to be also a drop down list, so I form the the list with years: 

# <codecell>

years = [str(x) for x in range(2000,2010)]

# <codecell>

interact(sh, year=years, time=(0,355,1), var=variabs);

# <markdowncell>

# Two drop-down lists and a slider. Already looks pretty much like a serious GUI and all in just a few lines of code.

# <markdowncell>

# The problem with previous versions is that color scale is jumping together with data. This is not always nice, especially if we want to compare things. So let's add a check-box (boolean variable) that will switch from "jumping" to constant color scale, and upper and lower limits:

# <codecell>

def sh(year='2000',var='air', FixedColor=False, vm=-3., vma=0., time=0):
    f = Dataset(var+'.sig995.'+year+'.nc')
    vv = f.variables[var]
    if FixedColor==False:
        imshow(vv[time,:,:])
        colorbar()
    else:
        imshow(vv[time,:,:], vmin=vm, vmax=vma)
        colorbar()

# <codecell>

interact(sh, year=years, time=(0,355,1), var=variabs,\
         vm=FloatTextWidget(value=250), vma=FloatTextWidget(value=300));

# <markdowncell>

# Here in case of the limits it is not clear what widget `interact` should use, so you can provide the name of it directly. The list of widgets is quite long and can be obtained like this: 

# <codecell>

from IPython.html import widgets
[widget for widget in dir(widgets) if widget.endswith('Widget')]

# <markdowncell>

# Often you want to have not just simple *heat-map* representation of your data, but really the map. You can do this with help of Basemap. It will work surprisingly fast (at least in case of this small data).

# <codecell>

from mpl_toolkits.basemap import Basemap

# <codecell>

m = Basemap(projection='npstere',boundinglat=60,lon_0=0,resolution='l')

# <codecell>

lon = f.variables['lon'][:]
lat = f.variables['lat'][:]
lon, lat = np.meshgrid(lon, lat)
x, y = m(lon, lat)

# <codecell>

def sh(year='2000',var='air', FixedColor=False, vm=-3., vma=0., inte=10, time=0):
    f = Dataset(var+'.sig995.'+year+'.nc')
    vv = f.variables[var]
    tt = f.variables['time']
    dd = num2date(tt[time], tt.units)
    if FixedColor==False:
        m.fillcontinents(color='gray',lake_color='gray')
        m.drawparallels(np.arange(-80.,81.,20.))
        m.drawmeridians(np.arange(-180.,181.,20.))
        m.drawmapboundary(fill_color='white')
        cs = m.contourf(x,y,vv[time,:,:]-273.15)
        #imshow(vv[time,:,:])
        colorbar()
        title(str(dd))
        
    else:
        m.fillcontinents(color='gray',lake_color='gray')
        m.drawparallels(np.arange(-80.,81.,20.))
        m.drawmeridians(np.arange(-180.,181.,20.))
        m.drawmapboundary(fill_color='white')
        cs = m.contourf(x,y,vv[time,:,:]-273.15, levels = linspace(vm,vma,inte))
        #imshow(vv[time,:,:])
        colorbar()
        title(str(dd))

# <codecell>

interact(sh, year=years, time=(0,355,1), var=variabs,\
         vm=FloatTextWidget(value=250), vma=FloatTextWidget(value=300), inte=FloatTextWidget(value=10));

