
# coding: utf-8

# # Using Python to Access NEXRAD Level 2 Data from Unidata THREDDS Server

# This is a modified version of Ryan May's notebook here:
# http://nbviewer.jupyter.org/gist/dopplershift/356f2e14832e9b676207
# 
# The TDS provides a mechanism to query for available data files, as well as provides access to the data as native volume files, through OPeNDAP, and using its own CDMRemote protocol. Since we're using Python, we can take advantage of Unidata's Siphon package, which provides an easy API for talking to THREDDS servers.
# 
# Bookmark these resources for when you want to use Siphon later!
# + [latest Siphon documentation](http://siphon.readthedocs.org/en/latest/)
# + [Siphon github repo](https://github.com/Unidata/siphon)
# + [TDS documentation](http://www.unidata.ucar.edu/software/thredds/current/tds/TDS.html)

# ## Downloading the single latest volume
# 

# Just a bit of initial set-up to use inline figures and quiet some warnings.

# In[1]:

import matplotlib
import warnings
warnings.filterwarnings("ignore", category=matplotlib.cbook.MatplotlibDeprecationWarning)
get_ipython().magic(u'matplotlib inline')


# First we'll create an instance of RadarServer to point to the appropriate radar server access URL.

# In[2]:

# The archive of data on S3 URL did not work for me, despite .edu domain
#url = 'http://thredds-aws.unidata.ucar.edu/thredds/radarServer/nexrad/level2/S3/'

#Trying motherlode URL
url = 'http://thredds.ucar.edu/thredds/radarServer/nexrad/level2/IDD/'
from siphon.radarserver import RadarServer
rs = RadarServer(url)


# Next, we'll create a new query object to help request the data. Using the chaining methods, let's ask for the latest data at the radar KLVX (Louisville, KY). We see that when the query is represented as a string, it shows the encoded URL.

# In[3]:

from datetime import datetime, timedelta
query = rs.query()
query.stations('KLVX').time(datetime.utcnow())


# We can use the RadarServer instance to check our query, to make sure we have required parameters and that we have chosen valid station(s) and variable(s)
# 

# In[4]:

rs.validate_query(query)


# Make the request, which returns an instance of TDSCatalog; this handles parsing the returned XML information.

# In[5]:

catalog = rs.get_catalog(query)


# We can look at the datasets on the catalog to see what data we found by the query. We find one volume in the return, since we asked for the volume nearest to a single time.

# In[6]:

catalog.datasets


# We can pull that dataset out of the dictionary and look at the available access URLs. We see URLs for OPeNDAP, CDMRemote, and HTTPServer (direct download).

# In[7]:

ds = list(catalog.datasets.values())[0]
ds.access_urls


# We'll use the CDMRemote reader in Siphon and pass it the appropriate access URL.

# In[8]:

from siphon.cdmr import Dataset
data = Dataset(ds.access_urls['CdmRemote'])


# We define some helper functions to make working with the data easier. One takes the raw data and converts it to floating point values with the missing data points appropriately marked. The other helps with converting the polar coordinates (azimuth and range) to Cartesian (x and y).

# In[9]:

import numpy as np
def raw_to_masked_float(var, data):
    # Values come back signed. If the _Unsigned attribute is set, we need to convert
    # from the range [-127, 128] to [0, 255].
    if var._Unsigned:
        data = data & 255

    # Mask missing points
    data = np.ma.array(data, mask=data==0)

    # Convert to float using the scale and offset
    return data * var.scale_factor + var.add_offset

def polar_to_cartesian(az, rng):
    az_rad = np.deg2rad(az)[:, None]
    x = rng * np.sin(az_rad)
    y = rng * np.cos(az_rad)
    return x, y


# The CDMRemote reader provides an interface that is almost identical to the usual python NetCDF interface. We pull out the variables we need for azimuth and range, as well as the data itself.

# In[10]:

sweep = 0
ref_var = data.variables['Reflectivity_HI']
ref_data = ref_var[sweep]
rng = data.variables['distanceR_HI'][:]
az = data.variables['azimuthR_HI'][sweep]


# Then convert the raw data to floating point values and the polar coordinates to Cartesian.

# In[11]:

ref = raw_to_masked_float(ref_var, ref_data)
x, y = polar_to_cartesian(az, rng)


# MetPy is a Python package for meteorology (Documentation: http://metpy.readthedocs.org and GitHub: http://github.com/MetPy/MetPy). We import MetPy and use it to get the colortable and value mapping information for the NWS Reflectivity data.

# In[12]:

from metpy.plots import ctables  # For NWS colortable
ref_norm, ref_cmap = ctables.registry.get_with_steps('NWSReflectivity', 5, 5)


# Finally, we plot them up using matplotlib and cartopy. We create a helper function for making a map to keep things simpler later.

# In[13]:

import matplotlib.pyplot as plt
import cartopy

def new_map(fig, lon, lat):
    # Create projection centered on the radar. This allows us to use x
    # and y relative to the radar.
    proj = cartopy.crs.LambertConformal(central_longitude=lon, central_latitude=lat)

    # New axes with the specified projection
    ax = fig.add_subplot(1, 1, 1, projection=proj)

    # Add coastlines
    ax.coastlines('50m', 'black', linewidth=2, zorder=2)

    # Grab state borders
    state_borders = cartopy.feature.NaturalEarthFeature(
        category='cultural', name='admin_1_states_provinces_lines',
        scale='50m', facecolor='none')
    ax.add_feature(state_borders, edgecolor='black', linewidth=1, zorder=3)
    
    return ax


# ## Download a collection of historical data

# This time we'll make a query based on a longitude, latitude point and using a time range.

# In[14]:

# Our specified time
#dt = datetime(2012, 10, 29, 15) # Superstorm Sandy
#dt = datetime(2016, 6, 18, 1)
dt = datetime(2016, 6, 8, 18) 
query = rs.query()
query.lonlat_point(-73.687, 41.175).time_range(dt, dt + timedelta(hours=1))


# The specified longitude, latitude are in NY and the TDS helpfully finds the closest station to that point.  We can see that for this time range we obtained multiple datasets.

# In[15]:

cat = rs.get_catalog(query)
cat.datasets


# Grab the first dataset so that we can get the longitude and latitude of the station and make a map for plotting. We'll go ahead and specify some longitude and latitude bounds for the map.

# In[16]:

ds = list(cat.datasets.values())[0]
data = Dataset(ds.access_urls['CdmRemote'])
# Pull out the data of interest
sweep = 0
rng = data.variables['distanceR_HI'][:]
az = data.variables['azimuthR_HI'][sweep]
ref_var = data.variables['Reflectivity_HI']

# Convert data to float and coordinates to Cartesian
ref = raw_to_masked_float(ref_var, ref_var[sweep])
x, y = polar_to_cartesian(az, rng)


# Use the function to make a new map and plot a colormapped view of the data

# In[17]:

fig = plt.figure(figsize=(10, 10))
ax = new_map(fig, data.StationLongitude, data.StationLatitude)

# Set limits in lat/lon space
ax.set_extent([-77, -70, 38, 43])

# Add ocean and land background
ocean = cartopy.feature.NaturalEarthFeature('physical', 'ocean', scale='50m',
                                            edgecolor='face',
                                            facecolor=cartopy.feature.COLORS['water'])
land = cartopy.feature.NaturalEarthFeature('physical', 'land', scale='50m',
                                           edgecolor='face',
                                           facecolor=cartopy.feature.COLORS['land'])

ax.add_feature(ocean, zorder=-1)
ax.add_feature(land, zorder=-1)
ax.pcolormesh(x, y, ref, cmap=ref_cmap, norm=ref_norm, zorder=0);


# In[18]:

meshes = []
for item in sorted(cat.datasets.items()):
    # After looping over the list of sorted datasets, pull the actual Dataset object out
    # of our list of items and access over CDMRemote
    ds = item[1]
    data = Dataset(ds.access_urls['CdmRemote'])

    # Pull out the data of interest
    sweep = 0
    rng = data.variables['distanceR_HI'][:]
    az = data.variables['azimuthR_HI'][sweep]
    ref_var = data.variables['Reflectivity_HI']

    # Convert data to float and coordinates to Cartesian
    ref = raw_to_masked_float(ref_var, ref_var[sweep])
    x, y = polar_to_cartesian(az, rng)

    # Plot the data and the timestamp
    mesh = ax.pcolormesh(x, y, ref, cmap=ref_cmap, norm=ref_norm, zorder=0)
    text = ax.text(0.65, 0.03, data.time_coverage_start, transform=ax.transAxes,
                   fontdict={'size':16})
    
    # Collect the things we've plotted so we can animate
    meshes.append((mesh, text))


# In[19]:

# Set up matplotlib to do the conversion to HTML5 video
import matplotlib
matplotlib.rcParams['animation.html'] = 'html5'

# Create an animation
from matplotlib.animation import ArtistAnimation
ArtistAnimation(fig, meshes)

