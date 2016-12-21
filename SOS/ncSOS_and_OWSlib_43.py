# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Accessing ncSOS 1.0 on TDS 4.3 with OWSLib

# <codecell>

from owslib.sos import SensorObservationService
from owslib.etree import etree
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
%matplotlib inline

# <codecell>

# usgs woods hole
# regular time series data 
url='http://geoport.whoi.edu/thredds/sos/usgs/data2/emontgomery/stellwagen/CF-1.6/BUZZ_BAY/2651-A.cdf'
usgs = SensorObservationService(url)
contents = usgs.contents

# <codecell>

usgs.contents

# <codecell>

off = usgs.offerings[1]
off.name

# <codecell>

off.response_formats

# <codecell>

off.observed_properties

# <codecell>

#pdb.set_trace()
response = usgs.get_observation(offerings=['2651-A'],
                                 responseFormat='text/xml;schema="om/1.0.0"',
                                 observedProperties=['T_20'],
                                 procedure='urn:ioos:sensor:gov.usgs.cmgp:2651-A')

# <codecell>

print response[0:2000]

# <codecell>

def parse_om_xml(response):
    # extract data and time from OM-XML response
    root = etree.fromstring(response)
    # root.findall(".//{%(om)s}Observation" % root.nsmap )
    values = root.find(".//{%(swe)s}values" % root.nsmap )
    date_value = np.array( [ (dt.datetime.strptime(d,"%Y-%m-%dT%H:%M:%SZ"),float(v))
            for d,v in [l.split(',') for l in values.text.split()]] )
    time = date_value[:,0]
    data = date_value[:,1]
    return data,time

# <codecell>

data, time = parse_om_xml(response)

# <codecell>

ts = pd.Series(data,index=time)

# <codecell>

ts.plot(figsize=(12,4));

# <headingcell level=2>

# Try adding a subset on time:

# <codecell>

start = '1982-10-01T00:00:00Z'
stop = '1982-10-04T00:00:00Z'
response = usgs.get_observation(offerings=['2651-A'],
                                 responseFormat='text/xml;schema="om/1.0.0"',
                                 observedProperties=['T_20'],
                                 procedure='urn:ioos:sensor:gov.usgs.cmgp:2651-A',
                                 eventTime='%s/%s' % (start,stop))

# <codecell>

data, time = parse_om_xml(response)
ts = pd.Series(data,index=time)
ts.plot(figsize=(12,4));

# <codecell>


