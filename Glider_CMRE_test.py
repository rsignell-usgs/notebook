# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# # Testing Glider CMRE access in Python
# 
# This is a url from NATO CMRE "grid" format, where glider data are stored as profiles. These follow the GROOM convention, and in contrast the the IOOS Glide DAC 2.0 format, instead of one combined profile for the down and up paths,  down and up are split into separate profiles.   
# 
# In addition to the "grid" files, there are also "raw" and "processed" glider netcdf files:
# 
# http://comt.sura.org/thredds/catalog/comt_2_full/testing/glider_cmre/catalog.html

# <codecell>


# <codecell>

import iris

url = 'http://comt.sura.org/thredds/dodsC/comt_2_full/testing/glider_cmre/GL-20140621-elettra-MEDREP14depl005-grid-R.nc'
# adding coordinates attribute so that Iris can find the coordinates
url = 'http://comt.sura.org/thredds/dodsC/comt_2_full/testing/glider_cmre/foo2.ncml'

cubes = iris.load_raw(url)

print(cubes)

# <codecell>

cube = cubes.extract('sea_water_salinity')[0]  #<- it always returns a list!
print(cube)

# <codecell>

import numpy as np
import numpy.ma as ma
import seawater as sw
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

%matplotlib inline

# <codecell>

def plot_glider(cube, mask_topo=False, **kw):
    """Plot glider cube."""
    cmap = kw.pop('cmap', plt.cm.rainbow)
    
    lon = cube.coord(axis='X').points.squeeze()
    lat = cube.coord(axis='Y').points.squeeze()
    z = cube.coord(axis='Z').points.squeeze()
    data = cube.data
    data = ma.masked_invalid(data,copy=True)
    z = ma.masked_invalid(z,copy=True)
    t = cube.coord(axis='T')
    t = t.units.num2date(t.points)
    
    dist, pha = sw.dist(lat, lon, units='km')
    dist = np.r_[0, np.cumsum(dist)]
    
    dist, z = np.broadcast_arrays(dist[..., None], z)
    
    fig, ax = plt.subplots(figsize=(9, 3.75))
    cs = ax.pcolor(dist, z, data, cmap=cmap, snap=True, **kw)
    plt.colorbar(cs)
    if mask_topo:
        h = z.max(axis=1)
        x = dist[:, 0]
        ax.plot(x, h, color='black', linewidth='0.5', zorder=3)
        ax.fill_between(x, h, y2=h.max(), color='0.9', zorder=3)
    ax.invert_yaxis()
    ax.set_title('Glider track from {} to {}'.format(t[0], t[-1]))
    fig.tight_layout()
    return fig, ax, cs

# <codecell>

c = cube[:,:]
fig, ax, cs = plot_glider(c, mask_topo=True)

# <codecell>


