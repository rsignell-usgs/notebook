# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import pandas as pd

# <codecell>

url='http://thredds.ucar.edu/thredds/ncss/grib/NCEP/NAM/CONUS_12km/Best?var=Temperature_height_above_ground&latitude=40.0343092&longitude=-105.2550532&time_start=2014-10-08T00%3A00%3A00Z&time_end=2014-10-25T18%3A00%3A00Z&vertCoord=&accept=csv'

# <codecell>

df = pd.read_csv(url,index_col=0,parse_dates=True,usecols=[0,4])

# <codecell>

df.tail()

# <codecell>

df.plot()

# <codecell>

df.columns

# <codecell>

df.columns = ['temp (C)']

# <codecell>

df['temp']-=272.15

# <codecell>

df.plot()

# <codecell>


