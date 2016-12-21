
# coding: utf-8

# In[1]:

get_ipython().magic(u'matplotlib inline')
from pyseidon import FVCOM


# In[2]:

fvcomOD=FVCOM('http://ecoii.acadiau.ca/thredds/dodsC/ecoii/test/FVCOM3D_dngrid_BF_20130619_20130621.nc')


# In[13]:

from pydap.client import open_url
url='http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/mwra/fvcom'
nc = open_url(url)


# In[17]:

import pyugrid
try:
    ug = pyugrid.UGrid.from_ncfile(url)
    lon = ug.nodes[:,0]
    lat = ug.nodes[:,1]
    nv = ug.faces
except:
    pass


# In[20]:

ug.nodes


# In[ ]:

ug.nodes


# In[4]:

fvcomWQ=FVCOM(url)


# In[6]:

import netCDF4 
nc = netCDF4.Dataset(url)
nc.variables


# In[6]:

get_ipython().magic(u'time')
ax=[-65.77, -65.75, 44.675, 44.685]
tx1=['2013-06-20 12:00:00', '2013-06-21 12:00:00']
tx2=['2013-06-21 12:00:00', '2013-06-21 18:00:00']
fvcomPartial1=FVCOM('http://ecoii.acadiau.ca/thredds/dodsC/ecoii/test/FVCOM3D_dngrid_BF_20130619_20130621.nc', ax=ax, tx=tx1)


# In[ ]:




# In[7]:

whos


# In[8]:

import sys


# In[12]:

get_ipython().magic(u'time')
fvcomPartial1.Plots.colormap_var(fvcomPartial1.Grid.h, title='Bathymetry (m)', mesh=False)


# In[ ]:



