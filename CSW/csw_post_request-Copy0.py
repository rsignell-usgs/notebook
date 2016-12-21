# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import requests, json

# <codecell>

headers = {'Content-Type': 'application/xml'}

# <headingcell level=2>

# BBOX query on NGDC Geoportal Server CSW

# <codecell>

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw'

# <codecell>

input='''
<csw:GetRecords xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:gml="http://www.opengis.net/gml" outputSchema="http://www.opengis.net/cat/csw/2.0.2"
    outputFormat="application/xml" version="2.0.2" service="CSW" resultType="results"
    maxRecords="1000"
    xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2 http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd">
    <csw:Query typeNames="csw:Record">
        <csw:ElementSetName>full</csw:ElementSetName>
        <csw:Constraint version="1.1.0">
            <ogc:Filter>
                <ogc:And>
                    <ogc:BBOX>
                        <ogc:PropertyName>ows:BoundingBox</ogc:PropertyName>
                        <gml:Envelope srsName="urn:ogc:def:crs:OGC:1.3:CRS84">
                            <gml:lowerCorner> -158.4 20.7</gml:lowerCorner>
                            <gml:upperCorner> -157.2 21.6</gml:upperCorner>
                        </gml:Envelope>
                    </ogc:BBOX>
                    <ogc:PropertyIsLessThanOrEqualTo>
                        <ogc:PropertyName>apiso:TempExtent_begin</ogc:PropertyName>
                        <ogc:Literal>2014-12-01T16:43:00Z</ogc:Literal>
                    </ogc:PropertyIsLessThanOrEqualTo>
                    <ogc:PropertyIsGreaterThanOrEqualTo>
                        <ogc:PropertyName>apiso:TempExtent_end</ogc:PropertyName>
                        <ogc:Literal>2014-12-01T16:43:00Z</ogc:Literal>
                    </ogc:PropertyIsGreaterThanOrEqualTo>
                    <ogc:PropertyIsLike wildCard="*" singleChar="?" escapeChar="\\">
                        <ogc:PropertyName>apiso:AnyText</ogc:PropertyName>
                        <ogc:Literal>*sea_water_salinity*</ogc:Literal>
                    </ogc:PropertyIsLike>
                </ogc:And>
            </ogc:Filter>
        </csw:Constraint>
    </csw:Query>
</csw:GetRecords>
''';

# <codecell>

xml_string=requests.post(endpoint, data=input, headers=headers).text
print xml_string[:2000]

# <headingcell level=2>

# BBOX query on PACIOOS pyCSW

# <codecell>

endpoint='http://oos.soest.hawaii.edu/pacioos/ogc/csw.py'

# <codecell>

input='''
<csw:GetRecords xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:gml="http://www.opengis.net/gml" outputSchema="http://www.opengis.net/cat/csw/2.0.2"
    outputFormat="application/xml" version="2.0.2" service="CSW" resultType="results"
    maxRecords="1000"
    xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2 http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd">
    <csw:Query typeNames="csw:Record">
        <csw:ElementSetName>full</csw:ElementSetName>
        <csw:Constraint version="1.1.0">
            <ogc:Filter>
                <ogc:And>
                    <ogc:BBOX>
                        <ogc:PropertyName>ows:BoundingBox</ogc:PropertyName>
                        <gml:Envelope srsName="urn:x-ogc:def:crs:EPSG:6.11:4326">
                            <gml:lowerCorner> 20.7 -158.4</gml:lowerCorner>
                            <gml:upperCorner> 21.6 -157.2</gml:upperCorner>
                        </gml:Envelope>
                    </ogc:BBOX>
                    <ogc:PropertyIsLessThanOrEqualTo>
                        <ogc:PropertyName>apiso:TempExtent_begin</ogc:PropertyName>
                        <ogc:Literal>2014-12-01T16:43:00Z</ogc:Literal>
                    </ogc:PropertyIsLessThanOrEqualTo>
                    <ogc:PropertyIsGreaterThanOrEqualTo>
                        <ogc:PropertyName>apiso:TempExtent_end</ogc:PropertyName>
                        <ogc:Literal>2014-12-01T16:43:00Z</ogc:Literal>
                    </ogc:PropertyIsGreaterThanOrEqualTo>
                    <ogc:PropertyIsLike wildCard="*" singleChar="?" escapeChar="\\">
                        <ogc:PropertyName>apiso:AnyText</ogc:PropertyName>
                        <ogc:Literal>*sea_water_salinity*</ogc:Literal>
                    </ogc:PropertyIsLike>
                </ogc:And>
            </ogc:Filter>
        </csw:Constraint>
    </csw:Query>
</csw:GetRecords>
''';

# <codecell>

xml_string=requests.post(endpoint, data=input, headers=headers).text

# <codecell>

print xml_string[:2000]

# <headingcell level=2>

# Query COMT pycsw

# <codecell>

endpoint='http://comt.sura.org:8000/pycsw/csw.py'

# <headingcell level=3>

# Try (lat,lon) order of bounding box with `srsName=EPSG:4326`

# <codecell>

input='''
<csw:GetRecords xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:gml="http://www.opengis.net/gml" outputSchema="http://www.opengis.net/cat/csw/2.0.2"
    outputFormat="application/xml" version="2.0.2" service="CSW" resultType="results"
    maxRecords="1000"
    xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2 http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd">
    <csw:Query typeNames="csw:Record">
        <csw:ElementSetName>full</csw:ElementSetName>
        <csw:Constraint version="1.1.0">
            <ogc:Filter>
                <ogc:And>
                    <ogc:BBOX>
                        <ogc:PropertyName>ows:BoundingBox</ogc:PropertyName>
                        <gml:Envelope srsName="urn:x-ogc:def:crs:EPSG:6.11:4326">
                            <gml:lowerCorner> 27 -100</gml:lowerCorner>
                            <gml:upperCorner> 30 -97</gml:upperCorner>
                        </gml:Envelope>
                    </ogc:BBOX>
                    <ogc:PropertyIsLessThanOrEqualTo>
                        <ogc:PropertyName>apiso:TempExtent_begin</ogc:PropertyName>
                        <ogc:Literal>2008-12-01T16:43:00Z</ogc:Literal>
                    </ogc:PropertyIsLessThanOrEqualTo>
                    <ogc:PropertyIsGreaterThanOrEqualTo>
                        <ogc:PropertyName>apiso:TempExtent_end</ogc:PropertyName>
                        <ogc:Literal>2008-06-01T16:43:00Z</ogc:Literal>
                    </ogc:PropertyIsGreaterThanOrEqualTo>
                    <ogc:PropertyIsLike wildCard="*" singleChar="?" escapeChar="\\">
                        <ogc:PropertyName>apiso:AnyText</ogc:PropertyName>
                        <ogc:Literal>*FVCOM*</ogc:Literal>
                    </ogc:PropertyIsLike>
                </ogc:And>
            </ogc:Filter>
        </csw:Constraint>
    </csw:Query>
</csw:GetRecords>
''';

# <codecell>

xml_string=requests.post(endpoint, data=input, headers=headers).text
xml_string[:2000]

# <headingcell level=3>

# Try (lon,lat) order of bounding box with `srsName=CRS84`

# <codecell>

input='''
<csw:GetRecords xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:gml="http://www.opengis.net/gml" outputSchema="http://www.opengis.net/cat/csw/2.0.2"
    outputFormat="application/xml" version="2.0.2" service="CSW" resultType="results"
    maxRecords="1000"
    xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2 http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd">
    <csw:Query typeNames="csw:Record">
        <csw:ElementSetName>full</csw:ElementSetName>
        <csw:Constraint version="1.1.0">
            <ogc:Filter>
                <ogc:And>
                    <ogc:BBOX>
                        <ogc:PropertyName>ows:BoundingBox</ogc:PropertyName>
                        <gml:Envelope srsName="urn:ogc:def:crs:OGC:1.3:CRS84">
                            <gml:lowerCorner>-100 27</gml:lowerCorner>
                            <gml:upperCorner> -97 30</gml:upperCorner>
                        </gml:Envelope>
                    </ogc:BBOX>
                    <ogc:PropertyIsLessThanOrEqualTo>
                        <ogc:PropertyName>apiso:TempExtent_begin</ogc:PropertyName>
                        <ogc:Literal>2008-12-01T16:43:00Z</ogc:Literal>
                    </ogc:PropertyIsLessThanOrEqualTo>
                    <ogc:PropertyIsGreaterThanOrEqualTo>
                        <ogc:PropertyName>apiso:TempExtent_end</ogc:PropertyName>
                        <ogc:Literal>2008-06-01T16:43:00Z</ogc:Literal>
                    </ogc:PropertyIsGreaterThanOrEqualTo>
                    <ogc:PropertyIsLike wildCard="*" singleChar="?" escapeChar="\\">
                        <ogc:PropertyName>apiso:AnyText</ogc:PropertyName>
                        <ogc:Literal>*FVCOM*</ogc:Literal>
                    </ogc:PropertyIsLike>
                </ogc:And>
            </ogc:Filter>
        </csw:Constraint>
    </csw:Query>
</csw:GetRecords>
''';

# <codecell>

xml_string=requests.post(endpoint, data=input, headers=headers).text
xml_string[:2000]

# <headingcell level=3>

# Woo hoo!   We get 4 records returned with both (lat,lon) EPSG:4326 and (lon,lat) CRS84 queries!  Success!!

# <codecell>

endpoint='http://geoport.whoi.edu/pycsw'

# <codecell>

xml_string=requests.post(endpoint, data=input, headers=headers).text
xml_string[:2000]

# <codecell>

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw'

# <codecell>


# <codecell>

input='''
<?xml version="1.0"?>	
<csw:GetRecords xmlns:csw="http://www.opengis.net/cat/csw/2.0.2" version="2.0.2" service="CSW" resultType="results" 
outputSchema="http://www.isotc211.org/2005/gmd" startPosition="1" maxRecords="1000">
  <csw:Query typeNames="csw:Record" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml">
  <csw:ElementSetName>full</csw:ElementSetName> 
  <csw:Constraint version="1.1.0">
  <ogc:Filter>
    <ogc:And>
      <ogc:PropertyIsEqualTo>
        <ogc:PropertyName>sys.siteuuid</ogc:PropertyName>
        <ogc:Literal>{68FF11D8-D66B-45EE-B33A-21919BB26421}</ogc:Literal>
      </ogc:PropertyIsEqualTo>
      <ogc:PropertyIsLike wildCard="*" escape="\" singleChar="?"> 
        <ogc:PropertyName>apiso:ServiceType</ogc:PropertyName>
        <ogc:Literal>*wms*</ogc:Literal>
      </ogc:PropertyIsLike>
    </ogc:And> 
  </ogc:Filter> 
</csw:Constraint> 
</csw:Query>
</csw:GetRecords>
'''

# <codecell>

xml_string=requests.post(endpoint, data=input, headers=headers).text
print xml_string[:2000]

# <codecell>


