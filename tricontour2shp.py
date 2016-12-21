""" Testing tricontourf -> shapefile conversion
"""

import numpy as np
import collections

from matplotlib import tri

####################
# Testing
Npnts = 5000
pnts = np.random.random((Npnts,2))

mt = tri.Triangulation( pnts[:,0],pnts[:,1])

# fabricate some data:
point_vals = (pnts[:,0]-0.5)**2 + (pnts[:,1]-0.5)**2

# make an island by masking a few triangles
island = ((mt.x[mt.triangles].mean(axis=1) - 0.75)**2 + (mt.y[mt.triangles].mean(axis=1) - 0.75)**2) < 0.03
mt.set_mask( island )


import pylab
pylab.figure()
contour=tri.tricontourf(pylab.gca(),mt , point_vals)
pylab.axis('equal')

from shapely import geometry
import wkb2shp

geoms = []
vals = [] # tuples of vmin,vmax

for colli,coll in enumerate(contour.collections):
    vmin,vmax = contour.levels[colli:colli+2]
    
    for p in coll.get_paths():
        p.simplify_threshold = 0.0
        polys = p.to_polygons()
        
        geoms.append( geometry.Polygon(polys[0],polys[1:] ) )
        vals.append( (vmin,vmax) )

            
            
wkb2shp.wkb2shp("contour-output.shp",
                geoms,
                overwrite=True,
                fields =array( vals, dtype=[('min',float64),
                                            ('max',float64)] ))
