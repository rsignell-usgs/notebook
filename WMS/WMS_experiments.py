
# coding: utf-8

# In[1]:

get_ipython().magic(u'matplotlib inline')
from IPython.core.display import Image


# In[2]:

import time


# In[3]:

# the region we want to subset, in Matlab style bbox:
bbox=[-95.0, -94.4, 29.3, 29.8]  # [lonmin lonmax latmin latmax] Galveston Bay


# In[4]:

# Plot WMS bathy image from NOAA Coastal Relief Model
wms = 'http://geoport-dev.whoi.edu/thredds/wms/bathy/crm_vol5.nc?'
wms_query = 'LAYERS=topo&ELEVATION=0&TIME=2012-12-07T08%3A42%3A13Z&TRANSPARENT=true&STYLES=boxfill%2Frainbow&CRS=EPSG%3A4326&COLORSCALERANGE=-20%2C0&NUMCOLORBANDS=32&LOGSCALE=false&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&EXCEPTIONS=application%2Fvnd.ogc.se_inimage&FORMAT=image%2Fpng&SRS=EPSG%3A4326&WIDTH=360&HEIGHT=360'
wms_bbox = '&BBOX=%.6f,%.6f,%.6f,%.6f' % (bbox[0],bbox[2],bbox[1],bbox[3])
wms_get_map = wms + wms_query + wms_bbox
print wms_get_map
Image(url=wms_get_map)


# In[5]:

get_ipython().magic(u'time')
url='http://geoport.whoi.edu:7000/wms/COAWST_4_use/?LAYERS=temp&TRANSPARENT=TRUE&STYLES=pcolor_average_jet_5_20_node_False&TIME=2013-10-22T00:00&ELEVATION=15&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&FORMAT=image%2Fpng&SRS=EPSG%3A3857&BBOX=-8226581.0302639,4886373.4405533,-6673380.6157253,5848868.5005863&WIDTH=635&HEIGHT=393'
Image(url=url)


# In[22]:

get_ipython().magic(u'time')
url='http://geoport.whoi.edu/thredds/wms/coawst_4/use/fmrc/coawst_4_use_best.ncd?LAYERS=temp&ELEVATION=-0.03125&TIME=2013-10-22T00%3A00%3A00.000Z&TRANSPARENT=true&STYLES=boxfill%2Frainbow&CRS=EPSG%3A4326&COLORSCALERANGE=10%2C30&NUMCOLORBANDS=64&LOGSCALE=false&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&EXCEPTIONS=application%2Fvnd.ogc.se_inimage&FORMAT=image%2Fpng&SRS=EPSG%3A4326&BBOX=-83.006379190914,31.242026011357,-58.757973988643,55.490431213629&WIDTH=512&HEIGHT=512'
Image(url=url)


# In[ ]:

url='http://www.neracoos.org/erddap/wms/WW3_EastCoast_latest/request?service=WMS&version=1.3.0&request=GetCapabilities'


# In[23]:

print 'elapsed time for ncWMS= %f' % (time.time() -time0)


# In[24]:

url='http://osm.woc.noaa.gov/mapcache/?LAYERS=osm&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&STYLES=&FORMAT=image%2Fjpeg&SRS=EPSG%3A900913&BBOX=-8915008.2154043,4697514.0102924,-6612113.4272285,5507135.013889&WIDTH=1883&HEIGHT=662'
Image(url=url)


# In[ ]:



