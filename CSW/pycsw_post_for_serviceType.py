# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import requests, json

# <codecell>

endpoint = 'http://geoport.whoi.edu/csw'
#endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw'
#endpoint = 'http://www.nodc.noaa.gov/geoportal/csw'
headers = {'Content-Type': 'application/xml'}

# <codecell>

input = '''
<csw:GetRecords xmlns:csw="http://www.opengis.net/cat/csw/2.0.2" version="2.0.2" service="CSW"
    resultType="results" startPosition="1" maxRecords="100">
    <csw:Query typeNames="csw:Record" xmlns:ogc="http://www.opengis.net/ogc"
        xmlns:gml="http://www.opengis.net/gml">
        <csw:ElementSetName>full</csw:ElementSetName>
        <csw:Constraint version="1.1.0">
            <ogc:Filter>
                <ogc:PropertyIsLike wildCard="*" singleChar="#" escapeChar="!">
                    <ogc:PropertyName>apiso:ServiceType</ogc:PropertyName>
                    <ogc:Literal>*WMS*</ogc:Literal>
                </ogc:PropertyIsLike>
            </ogc:Filter>
        </csw:Constraint>
    </csw:Query>
</csw:GetRecords>
'''

# <codecell>

xml_string=requests.post(endpoint, data=input, headers=headers).text
print xml_string[:2000]

# <codecell>

input = '''
<csw:GetRecords xmlns:csw="http://www.opengis.net/cat/csw/2.0.2" version="2.0.2" service="CSW"
    resultType="results" startPosition="1" maxRecords="100">
    <csw:Query typeNames="csw:Record" xmlns:ogc="http://www.opengis.net/ogc"
        xmlns:gml="http://www.opengis.net/gml">
        <csw:ElementSetName>full</csw:ElementSetName>
        <csw:Constraint version="1.1.0">
            <ogc:Filter>
                <ogc:PropertyIsLike wildCard="*" singleChar="#" escapeChar="!">
                    <ogc:PropertyName>apiso:AnyText</ogc:PropertyName>
                    <ogc:Literal>*coawst*</ogc:Literal>
                </ogc:PropertyIsLike>
            </ogc:Filter>
        </csw:Constraint>
    </csw:Query>
</csw:GetRecords>
'''

# <codecell>

xml_string=requests.post(endpoint, data=input, headers=headers).text
print xml_string[:2000]

# <codecell>


