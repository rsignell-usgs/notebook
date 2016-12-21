# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import pandas as pd
from pandas import Series, DataFrame
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import csv
import re
import cStringIO
import urllib2
import parser
import pdb
import random
import datetime as dt
from datetime import datetime
from pylab import *
from owslib.csw import CatalogueServiceWeb
from owslib.wms import WebMapService
from owslib.sos import SensorObservationService
from owslib.etree import etree
from owslib import fes
import netCDF4

# from: https://github.com/ioos/catalog/blob/master/ioos_catalog/tasks/reindex_services.py#L43-L58
from datetime import datetime
from urlparse import urlparse

import requests
import xml.etree.ElementTree as ET

from owslib import fes, csw
from owslib.util import nspath_eval
from owslib.namespaces import Namespaces
#import ioos_catalog
#from ioos_catalog import app,db


# <codecell>

#This is a collection of lists that we will need to examine Catalogs 

web_service_strings = ['urn:x-esri:specification:ServiceType:OPeNDAP',
                       'urn:x-esri:specification:ServiceType:odp:url',
                       'urn:x-esri:specification:ServiceType:WMS',
                       'urn:x-esri:specification:ServiceType:wms:url',
                       'urn:x-esri:specification:ServiceType:sos:url',
                       'urn:x-esri:specification:ServiceType:wcs:url']


services =      {'SOS'              : 'urn:x-esri:specification:ServiceType:sos:url',
                 'WMS'              : 'urn:x-esri:specification:ServiceType:wms:url',
                 'WCS'              : 'urn:x-esri:specification:ServiceType:wcs:url',
                 'DAP'              : 'urn:x-esri:specification:ServiceType:odp:url' }

# This looks like a good notebook to work from
# https://www.wakari.io/sharing/bundle/rsignell/Model_search

# <codecell>

#This cell lists catalog endpoints.  As CSW's are discovered within the larger
#    IOOS Umbrealla, this list is updated by the IOOS Program Office here:
#    https://github.com/ioos/system-test/wiki/Service-Registries-and-Data-Catalogs

#endpoint = 'http://data.nodc.noaa.gov/geoportal/csw'  # NODC Geoportal: collection level
#endpoint = 'http://geodiscover.cgdi.ca/wes/serviceManagerCSW/csw'  # NRCAN 
#endpoint = 'http://geoport.whoi.edu/gi-cat/services/cswiso' # USGS Woods Hole GI_CAT
#endpoint = 'http://cida.usgs.gov/gdp/geonetwork/srv/en/csw' # USGS CIDA Geonetwork
#endpoint = 'http://www.nodc.noaa.gov/geoportal/csw'   # NODC Geoportal: granule level
#endpoint = 'http://cmgds.marine.usgs.gov/geonetwork/srv/en/csw'  # USGS Coastal & Marine Program Geonetwork
#endpoint = 'http://www.ngdc.noaa.gov/geoportal/csw' # NGDC Geoportal
#endpoint = 'http://www.ncdc.noaa.gov/cdo-web/api/v2/' #NCDC CDO Web Services
#endpoint = 'http://geo.gov.ckan.org/csw' #CKAN Testing Site for new Data.gov
#endpoint = 'https://edg.epa.gov/metadata/csw' #EPA
#endpoint = 'http://geoport.whoi.edu/geoportal/csw' #WHOI Geoportal
#endpoint = 'http://cwic.csiss.gmu.edu/cwicv1/discovery' #CWIC
#endpoint = 'http://portal.westcoastoceans.org/connect/' #West Coast Governors Alliance (Based on ESRI Geoportal back end
#print out version
#endpoint = 'http://gcmdsrv.gsfc.nasa.gov/csw' #NASA's Global Change Master Directory (GCMD) CSW Service (Requires Authorization)
#endpoint = 'http://gcmdsrv3.gsfc.nasa.gov/csw' #NASA's Global Change Master Directory (GCMD) CSW Service (Requires Authorization)
#endpoint = 'https://data.noaa.gov/csw' #data.noaa.gov csw

endpoints = ['http://oos.soest.hawaii.edu/pacioos/ogc/csw.py',
             'http://www.nodc.noaa.gov/geoportal/csw',
             'http://www.ngdc.noaa.gov/geoportal/csw',
             'http://catalog.data.gov/csw-all',
             'http://cwic.csiss.gmu.edu/cwicv1/discovery',
             'http://geoport.whoi.edu/geoportal/csw',
             'https://edg.epa.gov/metadata/csw',
             'http://cmgds.marine.usgs.gov/geonetwork/srv/en/csw',
             'http://cida.usgs.gov/gdp/geonetwork/srv/en/csw',
             'http://geodiscover.cgdi.ca/wes/serviceManagerCSW/csw', 
             'http://geoport.whoi.edu/gi-cat/services/cswiso']

# <codecell>

endpoints = ['http://oos.soest.hawaii.edu/pacioos/ogc/csw.py']

# <codecell>

def service_urls(records,service_string='urn:x-esri:specification:ServiceType:wms:url'):
    urls=[]
    for key,rec in records.iteritems():
        #create a generator object, and iterate through it until the match is found
        #if not found, gets the default value (here "none")
        url = next((d['url'] for d in rec.references if d['scheme'] == service_string), None)
        if url is not None:
            urls.append(url)
    return urls
records1 = []
titles1 = []
lenrecords1 = []
lentitles1 = []
list1 = []
list2 = []
list3 = []
dict1 = {}
dict2 = {}
dict3 = {}
list4 = []
lenurls = []

for endpoint in endpoints:
    try:
        csw = CatalogueServiceWeb(endpoint,timeout=100)
        csw.getrecords2(maxrecords = 100)
        for web_service_string in web_service_strings:
            urls1 = service_urls(csw.records,service_string=web_service_string)
            list3.append(urls1)
            list1.append(web_service_string)
            list2.append(endpoint)
            list4.append(len(urls1))
            dict2['Service_URL']= list1
            dict2['endpoint'] = list2
            dict2['urls'] = list3
            dict2['number_urls'] = list4
    except Exception, ex1:
        print 'Error'
        
        
    
    #dict2['lenrecords'] = lenrecords1
    
#print dict2        
print pd.DataFrame(dict2)
#print pd.DataFrame(dict2.keys()) 


# <codecell>


