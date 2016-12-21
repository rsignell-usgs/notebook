
# coding: utf-8

# # Testing out Iris with OPeNDAP

# In[6]:

get_ipython().magic(u'matplotlib inline')
import matplotlib.pyplot as plt
from IPython.core.display import HTML
HTML('<iframe src=http://scitools.org.uk/iris/ width=800 height=350></iframe>')


# In[7]:

import numpy
import matplotlib.pyplot as plt

import iris
import iris.quickplot as qplt


# In[8]:

# load up some Gulf of Maine DEM data
bathy = iris.load_cube('http://geoport.whoi.edu/thredds/dodsC/bathy/gom15')


# In[9]:

# create a custom color map
# from http://colorbrewer2.org/index.php?type=sequential&scheme=Greens&n=9
earth_colors = [(247, 252, 245),
                (229, 245, 224), (199, 233, 192), (161, 217, 155),
                (116, 196, 118), (65, 171, 93), (35, 139, 69),
                (0, 109, 44), (0, 68, 27)]

# from http://colorbrewer2.org/index.php?type=sequential&scheme=Blues&n=7
sea_colors = [(239, 243, 255), (198, 219, 239), (158, 202, 225), (107, 174, 214), (66, 146, 198), (33, 113, 181), (8, 69, 148)]

colors = numpy.array(sea_colors[:1:-1] + earth_colors[2:], dtype=numpy.float32)
colors /= 256

# pick some contour levels
levels = [-4000, -2500, -400, -145, -10, 0, 10, 145, 400, 800, 1200, 1600, 2000]


# In[11]:

# make the plot
plt.figure(figsize=(10,10))
qplt.contourf(bathy, levels, colors=colors, extend='both');


# In[ ]:



