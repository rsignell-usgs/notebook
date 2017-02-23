
# coding: utf-8

# # Search GliderDAC for Pioneer Glider Data

# Use ERDDAP's RESTful advanced search to try to find OOI Pioneer glider water temperatures from the IOOS GliderDAC.  Use case from Stace Beaulieu (sbeaulieu@whoi.edu)

# In[1]:

import pandas as pd


# ### First try just searching for "glider"

# In[2]:

url = 'https://data.ioos.us/gliders/erddap/search/advanced.csv?page=1&itemsPerPage=1000&searchFor={}'.format('glider')
dft = pd.read_csv(url, usecols=['Title', 'Summary', 'Institution','Dataset ID'])  
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
endpoint = 'https://data.ioos.us/gliders/erddap/search/advanced.csv'


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

dft = pd.read_csv(url, usecols=['Title', 'Summary', 'Institution', 'Dataset ID'])  
print('Glider Datasets Found = {}'.format(len(dft)))
dft


# Define a function that returns a Pandas DataFrame based on the dataset ID.  The ERDDAP request variables (e.g. pressure, temperature) are hard-coded here, so this routine should be modified for other ERDDAP endpoints or datasets

# In[6]:

def download_df(glider_id):
    from pandas import DataFrame, read_csv
#    from urllib.error import HTTPError
    uri = ('https://data.ioos.us/gliders/erddap/tabledap/{}.csv'
           '?trajectory,wmo_id,time,latitude,longitude,depth,pressure,temperature'
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

# concatenate the dataframes for each dataset into one single dataframe   
df = pd.concat(list(map(download_df, dft['Dataset ID'].values)))


# In[8]:

print('Total Data Values Found: {}'.format(len(df)))


# In[9]:

df.head()


# In[10]:

df.tail()


# # plot up the trajectories with Cartopy (Basemap replacement)

# In[12]:

get_ipython().magic('matplotlib inline')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature
bathym_1000 = NaturalEarthFeature(name='bathymetry_J_1000',
                                  scale='10m', category='physical')
fig, ax = plt.subplots(
    figsize=(9, 9),
    subplot_kw=dict(projection=ccrs.PlateCarree())
)
ax.coastlines(resolution='10m')
ax.add_feature(bathym_1000, facecolor=[0.9, 0.9, 0.9], edgecolor='none')
dx = dy = 0.5
ax.set_extent([lon_min-dx, lon_max+dx, lat_min-dy, lat_max+dy])

g = df.groupby('trajectory')
for glider in g.groups:
    traj = df[df['trajectory'] == glider]
    ax.plot(traj['longitude'], traj['latitude'], label=glider)

gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--')
ax.legend();


# In[ ]:



