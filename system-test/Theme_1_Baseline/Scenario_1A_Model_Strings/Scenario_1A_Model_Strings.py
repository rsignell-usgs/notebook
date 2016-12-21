# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from utilities import css_styles
css_styles()

# <markdowncell>

# # IOOS System Test - Theme 1 - Scenario A - [Description](https://github.com/ioos/system-test/wiki/Development-of-Test-Themes#theme-1-baseline-assessment)
# 
# ## Model Strings
# 
# ## Questions
# 1. What Model records and how many are available via each endpoint?

# <markdowncell>

# ## Q1 - What Model records and how many are available via each endpoint?

# <codecell>

# https://github.com/ioos/system-test/wiki/Service-Registries-and-Data-Catalogs
known_csw_servers = endpoints = ['http://data.nodc.noaa.gov/geoportal/csw',
                                 'http://cwic.csiss.gmu.edu/cwicv1/discovery',
                                 'http://geoport.whoi.edu/geoportal/csw',
                                 'https://edg.epa.gov/metadata/csw',
                                 'http://www.ngdc.noaa.gov/geoportal/csw',
                                 'http://cmgds.marine.usgs.gov/geonetwork/srv/en/csw',
                                 'http://www.nodc.noaa.gov/geoportal/csw',
                                 'http://cida.usgs.gov/gdp/geonetwork/srv/en/csw',
                                 'http://geodiscover.cgdi.ca/wes/serviceManagerCSW/csw',
                                 'http://geoport.whoi.edu/gi-cat/services/cswiso',
                                 #'https://data.noaa.gov/csw',
                                 ]

# <markdowncell>

# <div class="error"><strong>CSW Server Broken</strong> - 'https://data.noaa.gov/csw' has been omitted because it is not working.  See: https://github.com/ioos/system-test/issues/130</div>

# <codecell>

known_model_strings = ['roms', 'selfe', 'adcirc', 'ncom', 'hycom', 'fvcom', 'pom', 'wrams', 'wrf']

# <markdowncell>

# ### Searching for models via CSW 'keyword'

# <markdowncell>

# #### Construct CSW Filters

# <codecell>

from owslib import fes

model_name_filters = []
for model in known_model_strings:
    title_filter   = fes.PropertyIsLike(propertyname='apiso:Title',   literal='*%s*' % model, wildCard='*')
    subject_filter = fes.PropertyIsLike(propertyname='apiso:Subject', literal='*%s*' % model, wildCard='*')
    model_name_filters.append(fes.Or([title_filter, subject_filter]))

# <markdowncell>

# #### Query each CSW catalog for revery model_name_filter constructed above

# <codecell>

from owslib.csw import CatalogueServiceWeb

model_results = []

for x in range(len(model_name_filters)):
    model_name          = known_model_strings[x]
    single_model_filter = model_name_filters[x]
    for url in known_csw_servers:
        try:
            csw = CatalogueServiceWeb(url, timeout=20)
            csw.getrecords2(constraints=[single_model_filter], maxrecords=1000, esn='full')
            for record, item in csw.records.items():
                for d in item.references:
                    result = dict(model=model_name,
                                  scheme=d['scheme'],
                                  url=d['url'],
                                  server=url)
                    model_results.append(result)
        except BaseException as e:
            print "- FAILED: %s - %s" % (url, e.msg)

# <markdowncell>

# <div class="error"><strong>Paginating CSW Records</strong> - Some servers have a maximum amount of records you can retrieve at once. See: https://github.com/ioos/system-test/issues/126</div>

# <markdowncell>

# #### Load results into a Pandas DataFrame

# <codecell>

%matplotlib inline
import pandas as pd
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', 50)

from IPython.display import HTML

df = pd.DataFrame(model_results)
df = df.drop_duplicates()

# <markdowncell>

# #### Total number of services

# <codecell>

total_services = pd.DataFrame(df.groupby("scheme").size(), columns=("Number of services",))
#HTML(total_services.to_html())
total_services.sort('Number of services', ascending=False).plot(kind="barh", figsize=(10,8,))

# <markdowncell>

# <div class="error"><strong>Service Types</strong> - URNs for the same service type are being identified differently.  There should be a consistent way of representing each service, or a complete mapping needs to be made available. See: https://github.com/ioos/system-test/issues/57</div>

# <markdowncell>

# #### Attempt to normalize the services manually

# <codecell>

from utilities import normalize_service_urn
normalized_urns = df.copy(deep=True)
normalized_urns["scheme"] = normalized_urns["scheme"].map(lambda x: normalize_service_urn(x))

# <codecell>

normalized_urns_summary = pd.DataFrame(normalized_urns.groupby("scheme").size(), columns=("Number of services",))
normalized_urns_summary.sort('Number of services', ascending=False).plot(kind="barh", figsize=(10,6,))

# <markdowncell>

# #### The number of service types for each model type

# <codecell>

import math

model_service_summary = pd.DataFrame(normalized_urns.groupby(["model", "scheme"], sort=True).size(), columns=("Number of services",))
#HTML(model_service_summary.to_html())
model_service_plotter = model_service_summary.unstack("model")
model_service_plot = model_service_plotter.plot(kind='barh', subplots=True, figsize=(12,35,), sharey=True)

# <markdowncell>

# #### Models per CSW server

# <codecell>

records_per_csw = pd.DataFrame(normalized_urns.groupby(["model", "server"]).size(), columns=("Number of services",))
#HTML(records_per_csw.to_html())
model_csw_plotter = records_per_csw.unstack("model")
model_csw_plot = model_csw_plotter.plot(kind='barh', subplots=True, figsize=(12,20,), sharey=True)

# <markdowncell>

# #### Services per CSW server

# <codecell>

records_per_csw = pd.DataFrame(normalized_urns.groupby(["scheme", "server"]).size(), columns=("Number of services",))
#HTML(records_per_csw.to_html())
model_csw_plotter = records_per_csw.unstack("server")
model_csw_plot = model_csw_plotter.plot(kind='barh', subplots=True, figsize=(12,30,), sharey=True)

# <codecell>


