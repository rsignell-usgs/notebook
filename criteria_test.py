# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import pandas as pd
import numpy as np
%matplotlib inline

# <codecell>

a = np.arange(10)
d = {'t1':a,'t2':-a}
df = pd.DataFrame(d)

# <codecell>

df.plot()

# <codecell>

df

# <codecell>

# find rows in table where:   1 < t1 <5 &  -6 < t2 < -2
a=np.logical_and(df['t1']>1,df['t1']<5)
b=np.logical_and(df['t2']>-6,df['t2']<-2)
criteria_satisfied = np.logical_and(a,b)            

# <codecell>

criteria_satisfied

# <codecell>

criteria_satisfied.sum()

# <codecell>


