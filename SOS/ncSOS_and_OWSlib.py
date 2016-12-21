# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Accessing ncSOS with OWSLib

# <codecell>

from owslib.sos import SensorObservationService
import pdb
from owslib.etree import etree
import pandas as pd
import datetime as dt

# <codecell>

# usgs woods hole
# buoy data (single current meter)
url='http://geoport.whoi.edu/thredds/sos/usgs/data2/emontgomery/stellwagen/CF-1.6/ARGO_MERCHANT/1211-A1H.cdf'
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

# the get observation request below works.  How can we recreate this using OWSLib?
# http://geoport-dev.whoi.edu/thredds/sos/usgs/data2/notebook/1211-A1H.cdf?service=SOS&version=1.0.0&request=GetObservation&responseFormat=text%2Fxml%3Bsubtype%3D%22om%2F1.0.0%22&offering=1211-A1H&observedProperty=u_1205&procedure=urn:ioos:station:gov.usgs:1211-A1H

# <codecell>

#pdb.set_trace()
response = usgs.get_observation(offerings=['1211-A1H'],
                                 responseFormat='text/xml;schema="om/1.0.0"',
                                 observedProperties=['u_1205'],
                                 procedure='urn:ioos:station:gov.usgs:1211-A1H')

# <codecell>

print response[0:4000]

# <codecell>

# usgs woods hole ADCP data
# url='http://geoport-dev.whoi.edu/thredds/sos/usgs/data2/notebook/9111aqd-a.nc'
# adcp = SensorObservationService(url)

# <codecell>

def parse_om_xml(response):
    # extract data and time from OM-XML response
    root = etree.fromstring(response)
    # root.findall(".//{%(om)s}Observation" % root.nsmap )
    values = root.find(".//{%(swe)s}values" % root.nsmap )
    date_value = array( [ (dt.datetime.strptime(d,"%Y-%m-%dT%H:%M:%SZ"),float(v))
            for d,v in [l.split(',') for l in values.text.split()]] )
    time = date_value[:,0]
    data = date_value[:,1]
    return data,time

# <codecell>

data, time = parse_om_xml(response)

# <codecell>

ts = pd.Series(data,index=time)

# <codecell>

ts.plot(figsize(12,4));

# <codecell>

''' this doesn't work
# Try adding a time range to the getobs request:

start = '1976-12-302T00:00:00Z'
stop = '1977-01-07T00:00:00Z'

response = usgs.get_observation(offerings=['1211-A1H'],
                                 responseFormat='text/xml;subtype="om/1.0.0"',
                                 observedProperties=['u_1205'],
                                 procedure='urn:ioos:station:gov.usgs:1211-A1H',
                                 eventTime='%s/%s' % (start,stop)
''';

# <headingcell level=2>

# Try adding a subset on time:

# <codecell>

start = '1977-01-01T00:00:00Z'
stop = '1977-01-04T00:00:00Z'
response = usgs.get_observation(offerings=['1211-A1H'],
                                 responseFormat='text/xml;schema="om/1.0.0"',
                                 observedProperties=['u_1205'],
                                 procedure='urn:ioos:station:gov.usgs:1211-A1H',
                                 eventTime='%s/%s' % (start,stop))

# <codecell>

data, time = parse_om_xml(response)
ts = pd.Series(data,index=time)
ts.plot(figsize(12,4));

