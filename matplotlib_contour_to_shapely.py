# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import matplotlib.pyplot as plt
x = [1,2,3,4]
y = [1,2,3,4]
m = [[15,14,13,12],[14,12,10,8],[13,10,7,4],[12,8,4,0]]
cs = plt.contour(x,y,m)

# <codecell>

from shapely.geometry import polygon as sp
for i in range(len(cs.collections)):
    p = cs.collections[i].get_paths()[0]
    v = p.vertices
    x = v[:,0]
    y = v[:,1]
    if len(x)>2:
        poly = sp.Polygon([(i[0], i[1]) for i in zip(x,y)])
        print i, poly, poly.area

# <codecell>


