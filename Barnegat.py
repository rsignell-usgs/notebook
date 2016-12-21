# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import numpy as np
import pandas as pd
from ulmo.usgs import nwis
%matplotlib inline

# <codecell>

#barnegat
sta_id='394540074062901'

# <codecell>

# download and cache site data (this will take a long time the first time)
# currently downloads all available parameters
nwis.hdf5.update_site_data(sta_id)

# <codecell>

sit = nwis.hdf5.get_site_data(sta_id, parameter_code='00035')

# <codecell>


# <codecell>


# wind speed and direction
vars=['00035','00036']

# <codecell>

sit

# <codecell>

#Try reading discharge data from another site

# <codecell>

sta_id='06043500'
nwis.hdf5.update_site_data(sta_id)
# read daily mean discharge data from cache (statistics code 00003)

# <codecell>

data = nwis.hdf5.get_site_data(sta_id, parameter_code='00060:00003')['00060:00003']
 
# convert data to a pandas dataframe
df = pd.DataFrame(data['values']).drop(['last_checked','last_modified','qualifiers'], axis=1).set_index('datetime')
df.value = df.value.apply(np.float)
df.index = pd.to_datetime(df.index).to_period('D')
 
# mark bad data as NaN
df[df.values == -999999] = np.nan

# <codecell>

# group the data by month, day & calculate means
daily_groups = df.groupby((lambda d: d.month, lambda d: d.day))
means = daily_groups.mean()
 
print 'historic daily mean on March 23rd is %s' % means.ix[3,23].value

# <codecell>

df.plot()

# <codecell>


