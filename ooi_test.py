
# coding: utf-8

# In[1]:

get_ipython().magic(u'matplotlib inline')


# In[2]:

import pandas as pd


# In[3]:

import xray


# In[4]:

url = 'http://opendap-devel.ooi.rutgers.edu:8090/thredds/dodsC/eov-1/Coastal_Pioneer/CP05MOAS/02-FLORTM000/recovered_host/CP05MOAS-GL388-02-FLORTM000-flort_m_glider_recovered-recovered_host/CP05MOAS-GL388-02-FLORTM000-recovered_host-flort_m_glider_recovered-20141207T213258-20141208T190652.nc'


# In[5]:

ds = xray.open_dataset(url)


# In[6]:

ds


# In[7]:

#Create a Pandas time series


# In[8]:

vts = pd.Series(ds['flort_m_bback_total'].values,index=ds['time'])


# In[9]:

vts_1h = vts.resample('1min', how='mean')
vts_1h.plot(figsize=(12,4))


# In[ ]:




# In[ ]:



