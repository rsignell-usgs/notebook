# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import iris
iris.FUTURE.netcdf_promote = True
print(iris.__version__)

import os.path

os.path.abspath(iris.__file__)

# <codecell>

%load_ext pymatbridge

# <codecell>

import iris.plot as iplt
import matplotlib.pyplot as plt


def plot_profile(c):
    coord = c.coord('sea_surface_height_above_reference_ellipsoid')
    lon = c.coord(axis='X').points.squeeze()
    lat = c.coord(axis='Y').points.squeeze()
    depth = coord.points.min()
    
    fig, ax = plt.subplots(figsize=(5, 6))
    kw = dict(linewidth=2,  color=(.3, .4, .5),
              alpha=0.75, marker='o', label='iris')
    iplt.plot(c, coord, **kw)
    ax.grid()
    ax.set_ylabel('{} ({})'.format(coord.standard_name, coord.units))
    ax.set_xlabel('{} ({})'.format(c.name(), c.units))
    ax.set_title('lon: %s\nlat: %s\nMax depth = %s' % (lon, lat, depth))
    return fig, ax

# <codecell>

a=2

# <codecell>

%%matlab -i a -o b
b=a^3;

# <codecell>

print b

# <codecell>

%%matlab
peaks;
colorbar;

# <codecell>


