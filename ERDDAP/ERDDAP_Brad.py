
# coding: utf-8

# #Read realtime data from NERACOOS ERDDAP
# Exploring use of Python to formulate [NERACOOS ERDDAP](http://www.neracoos.org/erddap) data requests and process the responses.  

# ##Initialize

# In[1]:

import pandas as pd
import urllib2
import numpy as np
import seawater as sw
import matplotlib.pyplot as plt


# In[2]:

# Use ERDDAP's built-in relative time functionality to get last 48 hours:
start='now-7days'
stop='now'
# or specify a specific period:
#start = '2013-05-06T00:00:00Z'
#stop =  '2013-05-07T00:00:00Z'


# ##Obtain data from ERDDAP

# In[3]:

# read instrument data (E01_sbe16)
url='http://www.neracoos.org/erddap/tabledap/E01_sbe16_all.csv?station,time,depth,longitude,latitude,attenuation,sigma_t,temperature,salinity&time>=%s&time<=%s' % (start,stop)

df_sb = pd.read_csv(url,index_col='time',parse_dates=True,skiprows=[1])  # skip the units row 

new_index = pd.date_range(start=df.index[0],end=df.index[-1],freq='15min')
df.reindex(new_index).interpolate(limit=10)
# In[ ]:

# read met data (E01_met)
url='http://www.neracoos.org/erddap/tabledap/E01_met_all.csv?station,time,air_temperature,barometric_pressure,wind_gust,wind_speed,wind_direction,visibility&time>=%s&time<=%s' % (start,stop)

df_met = pd.read_csv(url,index_col='time',parse_dates=True,skiprows=[1])  # skip the units row 


# In[ ]:

# read wave data (E01_accelerometer)
url='http://www.neracoos.org/erddap/tabledap/E01_accelerometer_all.csv?station,time,mooring_site_desc,significant_wave_height,dominant_wave_period&time>=%s&time<=%s' % (start,stop)

# Load the CSV data directly into Pandas
df_wave = pd.read_csv(url,index_col='time',parse_dates=True,skiprows=[1])  # skip the units row 


# In[ ]:

# List last ten records
df_sb.tail(10)


# In[ ]:

df_sb['sigma_t'].plot(figsize=(12,4),title=df_sb['station'][0]);legend(loc=2)
df_sb['attenuation'].plot(figsize=(12,4),secondary_y=True,legend=True)


# In[ ]:

p1=df_met['wind_speed'].plot(figsize=(12,4));legend(loc=2)
p2=df_wave['significant_wave_height'].plot(secondary_y=True,legend=True)


# In[ ]:

p1.get_label()


# In[ ]:

df[['wind_speed','significant_wave_height']].plot(figsize=(12,4))


# In[ ]:

df_wave.plot(figsize=(12,4));


# In[ ]:

scatter(df_sb['sigma_t'],df_sb['attenuation'])
grid()


# In[ ]:

def tsplot(sobs,tobs):
    smin=sobs.min()
    smax=sobs.max()
    tmin=tobs.min()
    tmax=tobs.max()
    s_inc=(smax-smin)/8.
    t_inc=(tmax-tmin)/8.
    t = np.arange(tmin,tmax+t_inc,t_inc)
    s = np.arange(smin,smax+s_inc,s_inc)
    S, T = np.meshgrid(s, t)
    st = sw.dens0(S, T) - 1000
    st_inc=(st.max()-st.min())/8.
    levels = np.arange(st.min(),st.max()+st_inc,st_inc)
    from matplotlib import rcParams
    from matplotlib.ticker import MultipleLocator
    rcParams['xtick.direction'] = 'out'
    rcParams['ytick.direction'] = 'out'
    fig, ax = plt.subplots(figsize=(6, 4))
 #   ax.xaxis.set_major_locator(MultipleLocator(0.5))
 #   ax.xaxis.set_minor_locator(MultipleLocator(0.1))
 #   ax.yaxis.set_major_locator(MultipleLocator(5))
 #   ax.yaxis.set_minor_locator(MultipleLocator(1))
    ax.set_ylabel(u"Temperature \u00b0C")
    ax.set_xlabel(r"Salinity [g kg$^{-1}$]")
    ax.axis([smin,smax,tmin,tmax])

    cs = ax.contour(s, t, st, colors='black', levels=levels)
    ax.clabel(cs, fontsize=9, inline=1, fmt='%3.2f')
    #sg = ax.contour(s, t, sigma_theta, linestyle='--', colors='grey', levels=[0, line])
    #ax.clabel(sg, fontsize=9, inline=1, fmt='%2.1f')
    ax.plot(sobs,tobs,'o')


# In[ ]:

tsplot(df['salinity'],df['temperature'])


# In[ ]:



