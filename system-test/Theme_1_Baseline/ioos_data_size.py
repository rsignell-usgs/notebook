# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# #Estimate how many TB of data are served by IOOS 

# <markdowncell>

# Estimate dataset size from the OPeNDAP DDS. Here we use regular expressions to parse the DDS and just the variable size (32 or 64 bit Int or Float) by their shapes. This represents the size in memory, not on disk, since the data could be compressed.  But the data in memory is in some sense a more true representation of the quantity of data available by the service.

# <codecell>

from owslib.csw import CatalogueServiceWeb
from owslib import fes
import pandas as pd
import datetime as dt
import requests
import re
import time
from __future__ import print_function

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

# <markdowncell>

# ## Find OpenDAP endpoints from NGDC CSW

# <codecell>

endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw' #  NGDC/IOOS Geoportal
dap_timeout=4  # timeout for DAP response
csw_timeout=60 # timeout for CSW response
csw = CatalogueServiceWeb(endpoint,timeout=csw_timeout)
csw.version

# <codecell>

[op.name for op in csw.operations]

# <codecell>

csw.get_operation_by_name('GetRecords').constraints

# <codecell>

for oper in csw.operations:
    print(oper.name)

# <codecell>

csw.get_operation_by_name('GetRecords').constraints

# <markdowncell>

# Since the supported ISO queryables contain `apiso:ServiceType`, we can use CSW to find all datasets with services that contain the string "dap" 

# <codecell>

try:
    csw.get_operation_by_name('GetDomain')
    csw.getdomain('apiso:ServiceType', 'property')
    print(csw.results['values'])
except:
    print('GetDomain not supported')

# <markdowncell>

# Since this CSW service doesn't provide us a list of potential values for `apiso:ServiceType`, we guess `opendap`, which seems to work:

# <codecell>

val = 'opendap'
service_type = fes.PropertyIsLike(propertyname='apiso:ServiceType',literal=('*%s*' % val),
                        escapeChar='\\',wildCard='*',singleChar='?')
filter_list = [ service_type]

# <codecell>

csw.getrecords2(constraints=filter_list,maxrecords=10000,esn='full')
len(csw.records.keys())

# <markdowncell>

# By printing out the references from a random record, we see that for this CSW the DAP URL is identified by 
# `urn:x-esri:specification:ServiceType:odp:url`

# <codecell>

choice=random.choice(list(csw.records.keys()))
print(choice)
csw.records[choice].references

# <markdowncell>

# Get all the OPeNDAP endpoints

# <codecell>

dap_urls = service_urls(csw.records,service_string='urn:x-esri:specification:ServiceType:odp:url')
len(dap_urls)

# <codecell>

def calc_dsize(txt):
    ''' 
    Calculate dataset size from the OPeNDAP DDS. 
    Approx method: Multiply 32|64 bit Int|Float variables by their shape.
    '''
    # split the OpenDAP DDS on ';' characters
    all = re.split(';',txt)
    '''
    Use regex to find numbers following Float or Int (e.g. Float32, Int64)
    and also numbers immediately preceding a "]".  The idea is that in line like:
    
    Float32 Total_precipitation_surface_6_Hour_Accumulation[time2 = 74][y = 303][x = 491];
           
    we want to find only the numbers that are not part of a variable or dimension name
    (want to return [32, 74, 303, 491], *not* [32, 6, 2, 74, 303, 491])
    '''
    m = re.compile('\d+(?=])|(?<=Float)\d+|(?<=Int)\d+')
    dsize=0
    for var in all:
        c = map(int,m.findall(var))
        if len(c)>=2:
            vsize = reduce(lambda x,y: x*y,c)
            dsize += vsize
    
    return dsize/1.0e6/8.   # return megabytes

# <codecell>

def tot_dsize(url,dap_timeout=2):
    das = url + '.dds'
    tot = 0
    try:
        response = requests.get(das,verify=True, timeout=dap_timeout)
    except:
        return tot, -1
    if response.status_code==200:
        # calculate the total size for all variables:
        tot = calc_dsize(response.text)
        # calculate the size for MAPS variables and subtract from the total:
        maps = re.compile('MAPS:(.*?)}',re.MULTILINE | re.DOTALL)
        map_text = ''.join(maps.findall(response.text))
        if map_text:
            map_tot = calc_dsize(map_text)
            tot -= map_tot
    
    return tot,response.status_code

# <codecell>

time0 = time.time()
good_data=[]
bad_data=[]
count=0
for url in dap_urls:
    count += 1
    dtot, status_code = tot_dsize(url,dap_timeout=dap_timeout)
    if status_code==200:
        good_data.append([url,dtot])
        print('[{}]Good:{},{}'.format(count,url,dtot), end='\r')
    else:
        bad_data.append([url,status_code])
        print('[{}]Fail:{},{}'.format(count,url,status_code), end='\r')
    
print('Elapsed time={} minutes'.format((time.time()-time0)/60.))

# <codecell>

print('Elapsed time={} minutes'.format((time.time()-time0)/60.))

# <codecell>

len(bad_data)

# <codecell>

bad_data[0][0]

# <markdowncell>

# So how much data are we serving?

# <codecell>

sum=0
for ds in good_data:
    sum +=ds[1]
    
print('{} terabytes'.format(sum/1.e6))

# <codecell>

url=[]
size=[]
for item in good_data:
    url.append(item[0])
    size.append(item[1])

# <codecell>

d={}
d['url']=url
d['size']=size

# <codecell>

good = pd.DataFrame(d)

# <codecell>

good.head()

# <codecell>

good=good.sort(['size'],ascending=0)

# <codecell>

good.head()

# <codecell>

url=[]
code=[]
for item in bad_data:
    url.append(item[0])
    code.append(item[1])

# <codecell>

d={}
d['url']=url
d['code']=code
bad = pd.DataFrame(d)

# <codecell>

bad.head()

# <codecell>

cd /usgs/data2/notebook/system-test/Theme_1_Baseline

# <codecell>

td = dt.datetime.today().strftime('%Y-%m-%d')

# <codecell>

bad.to_csv('bad'+td+'.csv')

# <codecell>

good.to_csv('good'+td+'.csv')

# <codecell>

bad=bad.sort(['url','code'],ascending=[0,0])

# <codecell>

bad = pd.read_csv('bad'+td+'.csv',index_col=0)
good = pd.read_csv('good'+td+'.csv',index_col=0)

# <codecell>

bad.head()

# <codecell>

recs = bad[bad['url'].str.contains('neracoos')]
print(len(recs))

# <codecell>

recs = bad[bad['url'].str.contains('ucar')]
print(len(recs))

# <codecell>

recs = bad[bad['url'].str.contains('tamu')]
print(len(recs))

# <codecell>

recs = bad[bad['url'].str.contains('axiom')]
print(len(recs))

# <codecell>

recs = bad[bad['url'].str.contains('caricoos')]
print(len(recs))

# <codecell>

recs = bad[bad['url'].str.contains('secoora')]
print(len(recs))

# <codecell>

recs = bad[bad['url'].str.contains('nanoos')]
print(len(recs))

# <codecell>

recs.to_csv('axiom.csv')

# <codecell>

!git add *.csv

# <codecell>

!git commit -m 'new csv'

# <codecell>

!git push

# <codecell>


