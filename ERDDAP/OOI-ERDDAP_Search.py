
# coding: utf-8

# # Search OOI ERDDAP for Pioneer Glider Data

# Use ERDDAP's RESTful advanced search to try to find OOI Pioneer glider water temperatures from the OOI ERDDAP.  Use case from Stace Beaulieu (sbeaulieu@whoi.edu)

# In[1]:

import pandas as pd


# ### First try just searching for "glider"

# In[2]:

url = 'http://ooi-data.marine.rutgers.edu/erddap/search/advanced.csv?page=1&itemsPerPage=1000&searchFor=glider'
dft = pd.read_csv(url, usecols=['Title', 'Summary', 'Institution', 'Dataset ID'])  
dft.head()


# ### Now search for all temperature data in specified bounding box and temporal extent

# In[3]:

start = '2000-01-01T00:00:00Z'
stop  = '2017-02-22T00:00:00Z'
lat_min =  39.
lat_max =  41.5
lon_min = -72.
lon_max = -69.
standard_name = 'sea_water_temperature'
endpoint = 'http://ooi-data.marine.rutgers.edu/erddap/search/advanced.csv'


# In[4]:

import pandas as pd


base = (
    '{}'
    '?page=1'
    '&itemsPerPage=1000'
    '&searchFor='
    '&protocol=(ANY)'
    '&cdm_data_type=(ANY)'
    '&institution=(ANY)'
    '&ioos_category=(ANY)'
    '&keywords=(ANY)'
    '&long_name=(ANY)'
    '&standard_name={}'
    '&variableName=(ANY)'
    '&maxLat={}'
    '&minLon={}'
    '&maxLon={}'
    '&minLat={}'
    '&minTime={}'
    '&maxTime={}').format

url = base(
    endpoint,
    standard_name,
    lat_max,
    lon_min,
    lon_max,
    lat_min,
    start,
    stop
)

print(url)


# In[5]:

dft = pd.read_csv(url, usecols=['Title', 'Summary', 'Institution','Dataset ID'])  

print('Datasets Found = {}'.format(len(dft)))
print(url)
dft


# Define a function that returns a Pandas DataFrame based on the dataset ID.  The ERDDAP request variables (e.g. "ctdpf_ckl_wfp_instrument_ctdpf_ckl_seawater_temperature") are hard-coded here, so this routine should be modified for other ERDDAP endpoints or datasets.   
# 
# Since we didn't actually find any glider data, we just request the last temperature value from each dataset, using the ERDDAP `orderByMax("time")` constraint.  This way we can see when the data ends, and if the mooring locations look correct

# In[6]:

def download_df(glider_id):
    from pandas import DataFrame, read_csv
#    from urllib.error import HTTPError
    uri = ('http://ooi-data.marine.rutgers.edu/erddap/tabledap/{}.csv'
           '?trajectory,'
           'time,latitude,longitude,'
           'ctdpf_ckl_wfp_instrument_ctdpf_ckl_seawater_temperature'
           '&orderByMax("time")'
           '&time>={}'
           '&time<={}'
           '&latitude>={}'
           '&latitude<={}'
           '&longitude>={}'
           '&longitude<={}').format
    url = uri(glider_id,start,stop,lat_min,lat_max,lon_min,lon_max)
    print(url)
    # Not sure if returning an empty df is the best idea.
    try:
        df = read_csv(url, index_col='time', parse_dates=True, skiprows=[1])
    except:
        df = pd.DataFrame()
    return df


# In[7]:

df = pd.concat(list(map(download_df, dft['Dataset ID'].values)))


# In[8]:

print('Total Data Values Found: {}'.format(len(df)))


# In[9]:

df


# In[10]:

get_ipython().magic('matplotlib inline')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER


fig, ax = plt.subplots(
    figsize=(9, 9),
    subplot_kw=dict(projection=ccrs.PlateCarree())
)
ax.coastlines(resolution='10m')
dx = dy = 0.5
ax.set_extent([lon_min-dx, lon_max+dx, lat_min-dy, lat_max+dy])

g = df.groupby('trajectory')
for glider in g.groups:
    traj = df[df['trajectory'] == glider]
    ax.plot(traj['longitude'], traj['latitude'], 'o', label=glider)

gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--')

ax.legend();


# In[ ]:



