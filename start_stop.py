
# coding: utf-8

# In[6]:

import netCDF4


# In[7]:

def start_stop(url,tvar):
    nc = netCDF4.Dataset(url)
    ncv = nc.variables
    time_var = ncv[tvar]
    first = netCDF4.num2date(time_var[0],time_var.units)
    last = netCDF4.num2date(time_var[-1],time_var.units)

    print first.strftime('%Y-%b-%d %H:%M')
    print last.strftime('%Y-%b-%d %H:%M')


# In[8]:

url='http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc'
tvar='time'
start_stop(url,tvar)


# In[4]:

url='http://geoport-dev.whoi.edu/thredds/dodsC/usgs/data2/emontgomery/stellwagen/CF-1.6/MONTEREY_CAN/4231-a.cdf'
tvar = 'time'
start_stop(url,tvar)


# In[5]:

url='http://omgsrv1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/sabgom/SABGOM_Forecast_Model_Run_Collection_best.ncd'
tvar = 'time'
start_stop(url,tvar)


# In[ ]:

url='http://omgarch1.meas.ncsu.edu:8080/thredds/dodsC/fmrc/sabgom/SABGOM_Forecast_Model_Run_Collection_best.ncd'
tvar = 'time3'
start_stop(url,tvar)


# In[ ]:

url='http://geoport-dev.whoi.edu/thredds/dodsC/estofs/atlantic'
tvar = 'time'
start_stop(url,tvar)


# In[ ]:

url='http://ecowatch.ncddc.noaa.gov/thredds/dodsC/hycom/hycom_reg1_agg/HYCOM_Region_1_Aggregation_best.ncd'
tvar='time'
start_stop(url,tvar)


# In[ ]:

url='http://geoport-dev.whoi.edu/thredds/dodsC/estofs/atlantic'
tvar='time'
start_stop(url,tvar)


# In[ ]:

url='http://mrtee.europa.renci.org:8080/thredds/dodsC/ASGS/sandy/27/nc6b/blueridge.renci.org/ncfs/nhcConsensus/00_dir.ncml'
tvar='time'
start_stop(url,tvar)


# In[ ]:

url='http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc'
tvar='time'
start_stop(url,tvar)


# In[ ]:

url='http://cida.usgs.gov/thredds/dodsC/prism_v2'
tvar='time'
start_stop(url,tvar)


# In[ ]:

netCDF4.__version__


# In[ ]:

url='http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/archives/necofs_gom3_wave'
tvar = 'time'
start_stop(url,tvar)


# In[ ]:

url='http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/archives/necofs_mb'
tvar='time'
start_stop(url,tvar)


# In[ ]:

url='http://crow.marine.usf.edu:8080/thredds/dodsC/FVCOM-Nowcast-Agg.nc'
tvar='time'
start_stop(url,tvar)


# In[ ]:



