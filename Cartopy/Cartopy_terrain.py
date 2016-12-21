# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

# -*- coding: utf-8 -*-
"""
Map tile acquisition
--------------------

Demonstrates cartopy's ability to draw map tiles which are downloaded on
demand from the MapQuest tile server. Internally these tiles are then combined
into a single image and displayed in the cartopy GeoAxes.

"""
import matplotlib.pyplot as plt
from matplotlib.transforms import offset_copy

import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
%matplotlib inline


def main():
    # Create a Stamen Terrain instance.
    terrain = cimgt.StamenTerrain()

    # Create a GeoAxes in the tile's projection.
    plt.figure(figsize=(10,10))
    ax = plt.axes(projection=terrain.crs)

    # Limit the extent of the map to a small longitude/latitude range.
    ax.set_extent([-122.3, -122, 46.1, 46.3])

    # Add the MapQuest data at zoom level 8.
    ax.add_image(terrain, 12)

    # Add a marker for the Mount Saint Helens volcano.
    plt.plot(-122.189611,46.205868, marker='o', color='yellow', markersize=12,
             alpha=0.7, transform=ccrs.Geodetic())

    # Use the cartopy interface to create a matplotlib transform object
    # for the Geodetic coordinate system. We will use this along with
    # matplotlib's offset_copy function to define a coordinate system which
    # translates the text by 25 pixels to the left.
    geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax)
    text_transform = offset_copy(geodetic_transform, units='dots', x=-25)

    # Add text 25 pixels to the left of the volcano.
    plt.text(-122.189611,46.205868, u'Mount Saint Helens Volcano',
             verticalalignment='center', horizontalalignment='right',
             transform=text_transform,
             bbox=dict(facecolor='wheat', alpha=0.5, boxstyle='round'))
    gl=ax.gridlines(draw_labels=True)
    gl.xlabels_top = False
    gl.ylabels_right = False
    plt.show()


if __name__ == '__main__':
    main()

# <codecell>


# <codecell>


# <codecell>


