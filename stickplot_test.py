# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
%matplotlib inline

# <codecell>

index = pd.date_range(start='1990-11-01 00:00', end='1991-2-1 00:00')

# <codecell>

df = pd.DataFrame(index=index)

# <codecell>

df['u'] = np.sin(0.1*index.to_julian_date()).values**2 - 0.5
df['v'] = np.cos(0.1*index.to_julian_date()).values

# <codecell>

df.plot(figsize=(10,2));

# <codecell>


