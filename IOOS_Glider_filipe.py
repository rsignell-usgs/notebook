# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# # Testing Glider DAC access in Python
# 
# This is a url from Kerfooot's TDS server, using the multidimensional NetCDF datasets created by a private ERDDAP instance.  These multidimensonal datasets are also available from ERDDAP, along with a flattened NetCDF representation and a ragged NetCDF representation.
# 
# The glider ERDDAP is here:
# http://erddap.marine.rutgers.edu/erddap
# 
# The glider TDS is here: http://tds.marine.rutgers.edu:8080/thredds/catalog/cool/glider/all/catalog.html

# <codecell>

import iris

url = 'http://tds.marine.rutgers.edu:8080/thredds/dodsC/cool/glider/all/ru22-20130924T2010.ncCFMA.nc3.nc'

cubes = iris.load_raw(url)

print(cubes)

# <codecell>

cube = cubes.extract('sea_water_temperature')[0]  #<- it always returns a list!
print(cube)

# <codecell>

import numpy as np
import numpy.ma as ma
import seawater as sw
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

%matplotlib inline

# <codecell>

def gen_topomask(h, lon, lat, dx=1., kind='linear'):
    """
    generate bottom contour, dx in km
    """
    h, lon, lat = map(np.asanyarray, (h, lon, lat))
    x = np.append(0, np.cumsum(sw.dist(lon, lat, units='km')[0]))
    Ih = interp1d(x, h, kind=kind, bounds_error=False, fill_value=h[-1])
    xm = np.arange(0, x.max() + dx, dx)
    hm = Ih(xm)
    return xm, hm

# <codecell>

def plot_glider(cube, mask_topo=False, **kw):
    """Plot glider cube."""
    cmap = kw.pop('cmap', plt.cm.rainbow)
    
    lon = cube.coord(axis='X').points.squeeze()
    lat = cube.coord(axis='Y').points.squeeze()
    z = cube.coord(axis='Z').points.squeeze()
    data = cube.data
    t = cube.coord(axis='T')
    t = t.units.num2date(t.points)
    
    dist, pha = sw.dist(lat, lon, units='km')
    dist = np.r_[0, np.cumsum(dist)]
    
    dist, z = np.broadcast_arrays(dist[..., None], z)

    z_range = cube.coord(axis='Z').attributes['actual_range']
    data_range = cube.attributes['actual_range']
    
    condition = np.logical_and(data >= data_range[0], data <= data_range[1])
    data = ma.masked_where(~condition, data)
    
    condition = np.logical_and(z >= z_range[0], z <= z_range[1])
    z = ma.masked_where(~condition, z)
    
    from matplotlib import rcParams
    rcParams['xtick.direction'] = 'in'
    rcParams['ytick.direction'] = 'in'
    
    fig, ax = plt.subplots()
    cs = ax.pcolor(dist, z, data, cmap=cmap, **kw)
    if mask_topo:
        h = z.max(axis=1)
        xm, hm = gen_topomask(h, lon, lat, dx=1., kind='linear')
        ax.plot(xm, hm, color='black', linewidth='1', zorder=3)
        ax.fill_between(xm, hm, y2=hm.max(), color='0.8', zorder=3)
    ax.invert_yaxis()
    ax.set_title('Glider track from {} to {}'.format(t[0], t[-1]))
    ax.set_ylabel('depth (m)')
    ax.set_xlabel('alongtrack distance (km)')

    return fig, ax, cs

# <codecell>

c = cube[0, ::5, ::2]

fig, ax, cs = plot_glider(c, mask_topo=False)

# FIXME: Masking topo needs some work!
#fig, ax, cs = plot_glider(c, mask_topo=True)

# <codecell>

np.shape(cube)

# <codecell>

print cube

# <codecell>


