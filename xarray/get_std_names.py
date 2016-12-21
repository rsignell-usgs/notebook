# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import xray

# <codecell>

url = 'http://geoport.whoi.edu/thredds/dodsC/usgs/data2/emontgomery/stellwagen/CF-1.6/RCNWR/9541aqd-cal.nc'

# <codecell>

ds = xray.open_dataset(url)

# <codecell>

def get_std_name_vars(ds,std_name):
    return {k: v for k, v in ds.data_vars.iteritems() if 'standard_name' in v.attrs.keys() and std_name in v.standard_name}

# <codecell>

std_name = 'eastward_sea_water_velocity'
get_std_name_vars(ds,std_name)

# <codecell>


