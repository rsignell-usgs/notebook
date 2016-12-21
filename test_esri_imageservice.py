# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=2>

# Extract DEM data from USACE LIDAR Test via ESRI Rest Service

# <codecell>

import json
import urllib2

# <codecell>

serviceURL='http://gis.sam.usace.army.mil/server/rest/services/JALBTCX/NCMP_BareEarth_1m/ImageServer'

# <codecell>

# Get general image service info: Spatial reference, Pixel Type, etc
def getISinfo(serviceURL):
    
    try:
        # Sending request for general service info
        post_data = ""
        
        headers = {}
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        
        serviceURL = serviceURL.replace("arcgis/services", "arcgis/rest/services")+"?f=json"                
        
        # Send general server request
        req = urllib2.Request(serviceURL, post_data, headers)
        response_stream = urllib2.urlopen(req)
        response = response_stream.read()    
        
        jsondict = json.loads(response)    
        isprj = jsondict["extent"]["spatialReference"]
        pixtype = jsondict["pixelType"]
        defaultrr = jsondict["rasterFunctionInfos"][0]["name"]
        
        return isprj, pixtype, defaultrr
    except Exception,e: 
        print str(e)

# <codecell>

isprj, pixtype, defaultrr = getISinfo(serviceURL)

# <codecell>

print isprj
print pixtype
print defaultrr

# <codecell>

serviceURL

# <codecell>


