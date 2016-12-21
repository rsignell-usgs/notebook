# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Plotting a CF-1.6 Time Series file with Iris

# <codecell>

import iris
import matplotlib.pyplot as plt
import iris.quickplot as qplt
%matplotlib inline

# <codecell>

url='http://comt.sura.org/thredds/dodsC/comt_1_archive_full/inundation_tropical/observations/tropical/netcdf/Ike/NOAA/8729108_Panama_City_Ike_WL.nc'

# <codecell>

cl = iris.load(url)

# <codecell>

print cl

# <codecell>

fig, ax = plt.subplots(figsize=(12, 3.5))
qplt.plot(cl[2], label=cl[2].name())
plt.grid()

# <headingcell level=2>

# You can also convert Iris cube object to a Pandas Series object

# <codecell>

from iris.pandas import as_cube, as_series, as_data_frame
df = as_series(cl[2])
df.head()

# <codecell>

df.plot(figsize=(12,3.5));

# <codecell>

df.describe()

# <codecell>


