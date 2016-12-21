# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

a='http://geoport.whoi.edu/thredds/wms/coawst_4/use/fmrc/coawst_4_use_best.ncd?service=WMS&version=1.3.0&request=GetCapabilities'

# <codecell>

# create a name for the WMS layer from the URL 
# by finding the text after the last '/' and before the '.' or the '?', which ever comes first
# also don't allow '-' in the name, as SciWMS doesn't like hyphens
nam=a.split('/')[-1].replace('-','_').replace('.','?').split('?')[0]
print nam

# <codecell>

# SCI-WMS endpoint
b='http://geoport.whoi.edu:8899/wms/datasets/%s/?REQUEST=GetCapabilities' % nam

# <codecell>

b

# <codecell>

import os
import urllib
from thredds_crawler.crawl import Crawl
from lxml import etree as et

# <codecell>

import logging
import logging.handlers
logger = logging.getLogger('thredds_crawler')
fh = logging.handlers.RotatingFileHandler('/usgs/data0/iso/logs/iso_harvest.log', maxBytes=1024*1024*10, backupCount=5)
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

SAVE_DIR="/usgs/data0/iso/iso_records"

namespace = {'gco': 'http://www.isotc211.org/2005/gco',
             'gmd': 'http://www.isotc211.org/2005/gmd'
             }

THREDDS_SERVERS = {
    "necofs1": "http://www.smast.umassd.edu:8080/thredds/forecasts.html",
    "coawst":   "http://geoport.whoi.edu/thredds/catalog/coawst_4/use/fmrc/catalog.html" 
}

for subfolder, thredds_url in THREDDS_SERVERS.items():
  logger.info("Crawling %s (%s)" % (subfolder, thredds_url))
  crawler = Crawl(thredds_url, debug=True)
  isos = [(d.id, s.get("url")) for d in crawler.datasets for s in d.services if s.get("service").lower() == "iso"]
  filefolder = os.path.join(SAVE_DIR, subfolder)
  if not os.path.exists(filefolder):
    os.makedirs(filefolder)
  for iso in isos:
    try:
      filename = iso[0].replace("/", "_") + ".iso.xml"
      filepath = os.path.join(filefolder, filename)
      logger.info("Downloading/Saving %s" % filepath)
      # retrieve XML from ncISO and put in file:
#      urllib.urlretrieve(iso[1], filepath)
      # retrieve XML from ncISO and put in etree
      tree = et.parse(iso[1])
      # Does metadata contain 'CMG_Portal' in a gco:CharacterString element?
      # if so, replace Thredds WMS endpoint with a SciWMS endpoint
      if tree.xpath(".//gco:CharacterString[text()='CMG_Portal']", namespaces=namespace):
        # find element with thredds WMS endpoint
        ele = tree.xpath(".//gmd:URL[contains(text(), 'thredds/wms')]", namespaces=namespace)
        url = ele[0].text
        # find the dataset name to use in the SciWMS endpoint
        name = url.split('/')[-1].replace('-','_').replace('.','?').split('?')[0]
        # replace element with new SciWMS endpoint
        new_url = 'http://geoport.whoi.edu:8899/wms/datasets/{0}/?REQUEST=GetCapabilities'.format(name)
        ele[0].text = new_url
        with open(filepath, 'w') as f:
          f.write(et.tostring(tree, pretty_print=True))
    except BaseException:
      logger.exception("Error!")

# <codecell>

iso

# <codecell>

xml_url = iso[1]
tree = et.parse(xml_url)
print(et.tostring(tree, pretty_print=True))

# <codecell>

namespace = {'gco': 'http://www.isotc211.org/2005/gco',
             'gmd': 'http://www.isotc211.org/2005/gmd'
             }
#cmg_portal = tree.findall(".//gmd:keyword[gco:CharacterString='CMG_Portal']/gco:CharacterString", namespace)
cmg_portal = tree.xpath(".//gco:CharacterString[text()='CMG_Portal']", namespaces=namespace)
print(cmg_portal)

# <codecell>

if not cmg_portal:
    print 'empty'

# <codecell>

cmg_portal = tree.xpath(".//gmd:URL[contains(text(), 'thredds/wms')]", namespaces=namespace)
print(cmg_portal[0].text)

# <codecell>

wms_url = cmg_portal[0].text
name = wms_url.split('/')[-1].replace('-','_').replace('.','?').split('?')[0]
print(name)

# <codecell>

new_wms_url = 'http://geoport.whoi.edu:8899/wms/datasets/{0}/?REQUEST=GetCapabilities'.format(name)
print(new_wms_url)

# <codecell>

cmg_portal[0].text = new_wms_url

# <codecell>

print(et.tostring(tree, pretty_print=True))

# <codecell>

with open('somefile.xml', 'w') as f:
    f.write(et.tostring(tree, pretty_print=True))

# <codecell>


