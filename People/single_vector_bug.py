# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Plot a single vector with quiver

# <codecell>

import matplotlib
matplotlib.__version__

# <codecell>

import matplotlib.pyplot as plt
%matplotlib inline

# <codecell>

plt.figure()
ax = plt.gca()
lim=2
ax.quiver(0,0,1,1,angles='xy',scale_units='xy',scale=1)
ax.set_xlim([-lim,lim])
ax.set_ylim([-lim,lim])
ax.grid()

# <codecell>


