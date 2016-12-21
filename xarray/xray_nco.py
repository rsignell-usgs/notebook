# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# # Using Xray like NCO

# <markdowncell>

# Select a specific OPeNDAP variable to subset and stride, then write the result to a NetCDF file

# <codecell>

import xray

# <codecell>

xray.__version__

# <markdowncell>

# specify the opendap data url endpoint

# <codecell>

url ='http://ecowatch.ncddc.noaa.gov/thredds/dodsC/hycom_sfc/20151007/hycom_glb_sfc_2015100700_t000.nc'

# <markdowncell>

# create the xray dataset from an opendap endpoint, but drop the 'tau' variable because it's units are invalid:

# <codecell>

ds = xray.open_dataset(url,drop_variables=['tau'])

# <codecell>

ds['water_temp']

# <markdowncell>

# subsample the xray dataarray object and promote to a dataset

# <codecell>

ds_wt = ds['water_temp'][0,0,::12,::12].to_dataset()

# <markdowncell>

# save subsetted data to netcdf, includes coordinate values as well

# <codecell>

ds_wt.to_netcdf('water_temp.nc')

