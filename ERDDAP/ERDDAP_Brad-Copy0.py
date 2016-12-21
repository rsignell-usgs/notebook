# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import pandas as pd

# Use ERDDAP's built-in relative time functionality to get last 48 hours:
start='now-7days'
stop='now'

# URL for wind data
url='http://www.neracoos.org/erddap/tabledap/E01_met_all.csv?\
station,time,air_temperature,barometric_pressure,wind_gust,wind_speed,\
wind_direction,visibility\
&time>=%s&time<=%s' % (start,stop)

# load CSV data into Pandas
df_met = pd.read_csv(url,index_col='time',parse_dates=True,skiprows=[1])  # skip the units row 

# URL for wave data
url='http://www.neracoos.org/erddap/tabledap/E01_accelerometer_all.csv?\
station,time,mooring_site_desc,significant_wave_height,dominant_wave_period&\
time>=%s&time<=%s' % (start,stop)

# Load the CSV data into Pandas
df_wave = pd.read_csv(url,index_col='time',parse_dates=True,skiprows=[1])  # skip the units row 

# <codecell>

df_met['wind_speed'].plot(figsize=(12,4),legend=True);

# <codecell>

df_met['wind_speed'].plot(figsize=(12,4))
df_wave['significant_wave_height'].plot(secondary_y=True);
ax=gca();
lines = ax.left_ax.get_lines() + ax.right_ax.get_lines()
ax.legend(lines, [l.get_label() for l in lines])

# <codecell>

ax=gca();
lines = ax.left_ax.get_lines() + ax.right_ax.get_lines()

