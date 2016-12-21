# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from suds.client import *
wsdlurl = 'http://daac.ornl.gov/cgi-bin/MODIS/GLBVIZ_1_Glb_subset/MODIS_webservice.wsdl'
client = Client(wsdlurl)
result = client.service.getsubset(40.115,-110.025,"MOD11A2","LST_Day_1km","A2001001","A2001025",1,1)
print result

# <codecell>

client.service.getproducts()

# <codecell>

url='http://acdisc.gsfc.nasa.gov:80/opendap/Aqua_MODIS_Level3/MYD08_D3.051/2014/MYD08_D3.A2014001.051.2014002194328.pscs_000500796355.hdf'

# <codecell>

import netCDF4

# <codecell>

nc = netCDF4.Dataset(url)

# <codecell>

nc.variables

# <codecell>

result = client.service.getsubset(40.115,-110.025,"MOD11A2","LST_Day_1km","A2001001","A2001009",100,100)

# <codecell>

result.nrows

# <codecell>

result.band.

# <codecell>

xml = etree.fromstring(result[0])

# <codecell>

len(result)

# <codecell>

b=a[0]

# <codecell>

type(b)

# <codecell>

len(c)

# <codecell>


