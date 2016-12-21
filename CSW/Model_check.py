# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# #Use CSW to find model data at NODC, NGDC, and CATALOG.DATA.GOV

# <codecell>

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import netCDF4

# <codecell>

def service_urls(records,service_string='urn:x-esri:specification:ServiceType:odp:url'):
    """
    Get all URLs matching a specific ServiceType 
 
    Unfortunately these seem to differ between different CSW-ISO services.
    For example, OpenDAP is specified:
    NODC geoportal: 'urn:x-esri:specification:ServiceType:OPeNDAP'
    NGDC geoportal: 'urn:x-esri:specification:ServiceType:odp:url'
    """

    urls=[]
    for key,rec in records.iteritems():
        #create a generator object, and iterate through it until the match is found
        #if not found, gets the default value (here "none")
        url = next((d['url'] for d in rec.references if d['scheme'] == service_string), None)
        if url is not None:
            urls.append(url)
    return urls

# <codecell>

filt=[]
search_text = ['roms','selfe','adcirc','ncom','hycom','fvcom']
for val in search_text:
    filt.append(fes.PropertyIsLike(propertyname='apiso:AnyText', 
                                   literal=('*%s*' % val),escapeChar='\\',wildCard='*',singleChar='?'))

val='sea_water_temperature'
filt.append(fes.PropertyIsLike(propertyname='apiso:AnyText', 
                                   literal=('*%s*' % val),escapeChar='\\',wildCard='*',singleChar='?'))    

# <markdowncell>

# ##Find model results at NODC

# <codecell>

endpoint = 'http://www.nodc.noaa.gov/geoportal/csw'   # NODC/UAF Geoportal: granule level
csw = CatalogueServiceWeb(endpoint,timeout=60)
print csw.version

# <codecell>

for oper in csw.operations:
    if oper.name == 'GetRecords':
        print '\nISO Queryables:\n',oper.constraints['SupportedISOQueryables']['values']

# <codecell>

csw.getrecords2(constraints=filt,maxrecords=1000,esn='full')
len(csw.records.keys())

# <codecell>

dap_urls = service_urls(csw.records,service_string='urn:x-esri:specification:ServiceType:OPeNDAP')
len(dap_urls)

# <codecell>

bad_urls=[]
for url in dap_urls:
    try:
        nc = netCDF4.Dataset(url)
        #print url
        nc.close()
    except:
        bad_urls.append(url)
            

print 'NODC: bad urls:',len(bad_urls),'/',len(dap_urls)
print 'First five bad URLS:',"\n".join(bad_urls[0:5])

# <markdowncell>

# ## Find model results at NGDC

# <codecell>

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw' #  NGDC/IOOS Geoportal
csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version

# <codecell>

for oper in csw.operations:
    if oper.name == 'GetRecords':
        print '\nISO Queryables:\n',oper.constraints['SupportedISOQueryables']['values']

# <codecell>

csw.getrecords2(constraints=filt,maxrecords=1000,esn='full')
len(csw.records.keys())

# <codecell>

choice=random.choice(list(csw.records.keys()))
print choice
csw.records[choice].references

# <codecell>

#dap_urls = service_urls(csw.records,service_string='urn:x-esri:specification:ServiceType:OPeNDAP')
dap_urls = service_urls(csw.records,service_string='urn:x-esri:specification:ServiceType:odp:url')
len(dap_urls)

# <codecell>

bad_urls=[]
for url in dap_urls:
    try:
        nc = netCDF4.Dataset(url)
        #print url
        nc.close()
    except:
        bad_urls.append(url)
print 'NGDC: bad urls:',len(bad_urls),'/',len(dap_urls)
print 'First five bad URLS:',"\n".join(bad_urls[0:5])

# <markdowncell>

# ## Find model data at CATALOG.DATA.GOV

# <codecell>

endpoint = 'http://catalog.data.gov/csw-all' #  catalog.data.gov CSW
csw = CatalogueServiceWeb(endpoint,timeout=60)
csw.version

# <codecell>

for oper in csw.operations:
    if oper.name == 'GetRecords':
        print oper.constraints

# <codecell>

csw.getrecords2(constraints=filt,maxrecords=1000,esn='full')
len(csw.records.keys())

# <codecell>

choice=random.choice(list(csw.records.keys()))
print choice
csw.records[choice].references

# <markdowncell>

# From the above, we can see that because the 'scheme' is 'None' on all the references, we can't extract the different service types, like OPeNDAP, WCS, etc. 

# <codecell>

#dap_urls = service_urls(csw.records,service_string='urn:x-esri:specification:ServiceType:odp:url')  #NGDC
#dap_urls = service_urls(csw.records,service_string='urn:x-esri:specification:ServiceType:OPeNDAP')  #NODC
dap_urls = service_urls(csw.records,service_string='?????????')    #CATALOG.DATA.GOV
len(dap_urls)

# <codecell>


