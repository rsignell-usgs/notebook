
# coding: utf-8

# # Try some "RAW" requests to pycsw

# In[1]:

import requests, json


# In[2]:

headers = {'Content-Type': 'application/xml'}


# ### Try apiso:serviceType query

# In[3]:

input = '''
<csw:GetRecords xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
    xmlns:ogc="http://www.opengis.net/ogc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    outputSchema="http://www.opengis.net/cat/csw/2.0.2" outputFormat="application/xml"
    version="2.0.2" service="CSW" resultType="results" maxRecords="1000"
    xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2 http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd">
    <csw:Query typeNames="csw:Record">
        <csw:ElementSetName>summary</csw:ElementSetName>
        <csw:Constraint version="1.1.0">
            <ogc:Filter>
                    <ogc:PropertyIsLike wildCard="*" singleChar="?" escapeChar="\">
                        <ogc:PropertyName>apiso:ServiceType</ogc:PropertyName>
                        <ogc:Literal>*WMS*</ogc:Literal>
                    </ogc:PropertyIsLike>
            </ogc:Filter>
        </csw:Constraint>
    </csw:Query>
</csw:GetRecords>
'''


# Geoport pycsw instance

# In[4]:

endpoint = 'http://geoport.whoi.edu/csw'  
xml_string=requests.post(endpoint, data=input, headers=headers).text
print xml_string[:2000]


# Geonode pycsw instance

# In[ ]:

endpoint = 'http://geonode.wfp.org/catalogue/csw'
xml_string=requests.post(endpoint, data=input, headers=headers).text
print xml_string[:2000]


# geodata.gov.gr pycsw instance

# In[ ]:

endpoint = 'http://geodata.gov.gr/csw'
xml_string=requests.post(endpoint, data=input, headers=headers).text
print xml_string[:2000]


# Data.Gov pycsw instance

# In[5]:

endpoint = 'http://catalog.data.gov/csw-all'  
xml_string=requests.post(endpoint, data=input, headers=headers).text
print xml_string[:2000]


# PACIOOS pycsw instance

# In[6]:

endpoint = 'http://oos.soest.hawaii.edu/pacioos/ogc/csw.py' 
xml_string=requests.post(endpoint, data=input, headers=headers).text
print xml_string[:2000]


# Data.ioos.us endpoint

# In[7]:

endpoint = 'http://data.ioos.us/csw' 
xml_string=requests.post(endpoint, data=input, headers=headers).text
print xml_string[:2000]


# ### Try using both apiso:AnyText and apiso:ServiceType queries 

# In[ ]:

input = '''
<csw:GetRecords xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
    xmlns:ogc="http://www.opengis.net/ogc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    outputSchema="http://www.opengis.net/cat/csw/2.0.2" outputFormat="application/xml"
    version="2.0.2" service="CSW" resultType="results" maxRecords="1000"
    xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2 http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd">
    <csw:Query typeNames="csw:Record">
        <csw:ElementSetName>summary</csw:ElementSetName>
        <csw:Constraint version="1.1.0">
            <ogc:Filter>
                <ogc:And>
                    <ogc:PropertyIsLike wildCard="*" singleChar="?" escapeChar="\">
                        <ogc:PropertyName>apiso:AnyText</ogc:PropertyName>
                        <ogc:Literal>*coawst*</ogc:Literal>
                    </ogc:PropertyIsLike>
                    <ogc:PropertyIsLike wildCard="*" singleChar="?" escapeChar="\">
                        <ogc:PropertyName>apiso:ServiceType</ogc:PropertyName>
                        <ogc:Literal>*OPeNDAP*</ogc:Literal>
                    </ogc:PropertyIsLike>
                </ogc:And>
            </ogc:Filter>
        </csw:Constraint>
    </csw:Query>
</csw:GetRecords>
'''


# In[ ]:

endpoint = 'http://geoport.whoi.edu/csw' 
xml_string=requests.post(endpoint, data=input, headers=headers).text
print xml_string[:2000]


# In[ ]:

endpoint = 'http://catalog.data.gov/csw-all' 
xml_string=requests.post(endpoint, data=input, headers=headers).text
print xml_string[:2000]


# In[ ]:

endpoint = 'http://data.ioos.us/csw' 
xml_string=requests.post(endpoint, data=input, headers=headers).text
print xml_string[:2000]


# In[ ]:

endpoint = 'http://catalog.data.gov/csw-all' 
xml_string=requests.post(endpoint, data=input, headers=headers).text
print xml_string[:2000]


# ### BBOX query on NGDC Geoportal Server CSW

# In[ ]:

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw'


# In[ ]:

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


# In[ ]:

xml_string=requests.post(endpoint, data=input, headers=headers).text
print xml_string[:650]


# ## BBOX query on PACIOOS pyCSW

# In[ ]:

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


# In[ ]:

endpoint='http://oos.soest.hawaii.edu/pacioos/ogc/csw.py'


# In[ ]:

xml_string=requests.post(endpoint, data=input, headers=headers).text


# In[ ]:

print xml_string[:2000]


# ## Query COMT pycsw

# ### Try (lat,lon) order of bounding box with `srsName=EPSG:4326`

# In[ ]:

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


# In[ ]:

endpoint='http://comt.sura.org:8000/pycsw/csw.py'


# In[ ]:

xml_string=requests.post(endpoint, data=input, headers=headers).text
xml_string[:2000]


# ### Try (lon,lat) order of bounding box with `srsName=CRS84`

# In[ ]:

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


# In[ ]:

xml_string=requests.post(endpoint, data=input, headers=headers).text
xml_string[:2000]


# ### Woo hoo!   We get 4 records returned with both (lat,lon) EPSG:4326 and (lon,lat) CRS84 queries!  Success!!

# In[ ]:

endpoint='http://geoport.whoi.edu/pycsw'


# In[ ]:

xml_string=requests.post(endpoint, data=input, headers=headers).text
xml_string[:2000]


# In[ ]:



