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

# ncSOS endpoint with time series data
#url='http://geoport-dev.whoi.edu/thredds/sos/usgs/data2/notebook/1211-A1H.cdf'
url='http://www.neracoos.org:8180/thredds/sos/UMO/DSG/SOS/A01/Accelerometer/HistoricRealtime/Agg.ncml'
sos = SensorObservationService(url)
contents = sos.contents

# <codecell>

sos.contents

# <codecell>

off = sos.offerings[1]
off.name

# <codecell>

off.response_formats

# <codecell>

off.observed_properties

# <codecell>

#pdb.set_trace()
response = sos.get_observation(offerings=['A01'],
                                 responseFormat='text/xml;schema="om/1.0.0"',
                                 observedProperties=['significant_wave_height'])

# <codecell>

print response[0:1400]

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

# Try adding a time range to the getobs request:

start = '2010-03-01T00:00:00Z'
stop = '2010-04-15T00:00:00Z'

response = sos.get_observation(offerings=['A01'],
                                 responseFormat='text/xml;schema="om/1.0.0"',
                                 observedProperties=['significant_wave_height'],
                                 eventTime='%s/%s' % (start,stop))

# <codecell>

data, time = parse_om_xml(response)

# <codecell>

ts = pd.Series(data,index=time)

# <codecell>

ts.plot(figsize(12,4));

