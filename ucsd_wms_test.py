# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=2>

# Test WMS performance of joinExisting and FMRC aggregations from UCSD THREDDS 

# <markdowncell>

# The [UCSD THREDDS server](http://hfrnet.ucsd.edu/thredds/catalog.html) has the largest archive of gridded HF Radar surface currents in the USA.  But their services have been very frustrating to use because sometimes they are fast and sometimes very slow.   
# 
# Based on conversations with Tom Cook and Mark Otero, here's how the datasets are constructed:
# 
# There are alway Matlab processes running, retrieving new HFRAdar data and as soon as a certain amount of data comes in, a gridded netcdf file is produced for a specific observation hour.   As additional radar data comes in, the *data* in the file is updated, but the metadata stays the same.  The file is updated by replacing the existing file with a new file of the same name. 
# 
# The files are scanned by a `joinExisting` aggregation scan and also by a `FMRC featureCollection` aggregation scan (accessible via the [FMRC aggregation catalog](http://hfrnet.ucsd.edu/thredds/fmrc-catalog.html))
# 
# Below we test the WMS performance of the two aggregation techniques. 
# 
# We find that even though `FMRC` is not designed for this type of aggregation, it performs consistently better than the `joinExisting`. 
# 
# Why?

# <codecell>

from IPython.core.display import Image
import time
import pandas as pd
import datetime as dt
import numpy as np
import urllib

# <codecell>

%matplotlib inline

# <codecell>

t = range(60)

# <codecell>

bbox=[-75.413, -70.1733582764, 37.586, 41.68049]  # [lonmin lonmax latmin latmax] 

# <codecell>

wms1='http://hfrnet.ucsd.edu/thredds/wms/HFRNet/USEGC/6km/hourly/RTV?'
wms_query='LAYERS=surface_sea_water_velocity&ELEVATION=0&TIME=2015-03-11T00%3A00%3A00.000Z&TRANSPARENT=true&STYLES=vector%2Frainbow&CRS=EPSG%3A4326&COLORSCALERANGE=0%2C0.5&NUMCOLORBANDS=20&LOGSCALE=false&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&EXCEPTIONS=application%2Fvnd.ogc.se_inimage&FORMAT=image%2Fpng&SRS=EPSG%3A4326&'
wms_bbox = 'BBOX=%.6f,%.6f,%.6f,%.6f&WIDTH=768&HEIGHT=600' % (bbox[0],bbox[2],bbox[1],bbox[3])
wms_get_map1 = wms1 + wms_query + wms_bbox
print wms_get_map1

# <codecell>

wms2='http://hfrnet.ucsd.edu/thredds/wms/USEGC/RTV/6km/HFRADAR,_US_East_and_Gulf_Coast,_6km_Resolution,_Hourly_RTV_best.ncd?'
wms_get_map2 = wms2 + wms_query + wms_bbox
print wms_get_map2

# <codecell>

indx=[]
dti1=[]
dti2=[]
for i in t:
    time.sleep(60)
    box= bbox + np.random.uniform(-.1,.1,size=4)
    wms_bbox = 'BBOX=%.6f,%.6f,%.6f,%.6f&WIDTH=768&HEIGHT=600' % (box[0],box[2],box[1],bbox[3])

    wms_get_map1 = wms1 + wms_query + wms_bbox
    indx.append(dt.datetime.now())
    time0=time.time()
    urllib.urlretrieve(wms_get_map1, 'foo.png')
    dti1.append(time.time()-time0)
    
    wms_get_map2 = wms2 + wms_query + wms_bbox
    time0=time.time()
    urllib.urlretrieve(wms_get_map2, 'foo.png')
    dti2.append(time.time()-time0)


# <codecell>

t1 = pd.Series(index=indx,data=dti1)
t1.plot(figsize=(12,4),marker='o')

# <codecell>

t2 = pd.Series(index=indx,data=dti2)
t2.plot(figsize=(12,4),marker='o')

# <markdowncell>

# The configuration of the `joinExisting` is as follows: 
# 
# ```xml
#     <dataset name="HFRADAR, US East and Gulf Coast, 2km Resolution, Hourly RTV" 
#        ID="HFRNet/USEGC/2km/hourly/RTV" urlPath="HFRNet/USEGC/2km/hourly/RTV">
#       <metadata>
#         <documentation type="Summary">HFRADAR, US East and Gulf Coast, 
#           2km Resolution, Hourly Combined Total Vectors (RTV)</documentation>
#       </metadata>
#       <netcdf xmlns="http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2">
#         <aggregation dimName="time" type="joinExisting" recheckEvery="10 min">
#           <scan location="/exports/hfradar/hfrnet/hfrtv/USEGC" subdirs="true" 
#             olderThan="2 min" 
#             regExp=".*[0-9]{12}_hfr_usegc_2km_rtv_uwls_SIO\.nc$"/>
#         </aggregation>
#       </netcdf>
#     </dataset>
# ```
# with the `threddsConfig.xml` cache settings like this:
# ```xml
#   <AggregationCache>
#     <scour>-1 hours</scour>
#   </AggregationCache>
# ```

