
# coding: utf-8

## pygridgen test

# conda install using phobson's binstar channel:
# ```
# conda create --name=grids python=2.7 nose pip ipython-notebook
# source activate grids
# conda install --channel=phobson nn csa gridutils gridgen pygridgen
# ```

# In[1]:

import matplotlib.pyplot as plt
import pygridgen
get_ipython().magic(u'matplotlib inline')


### Basic Example

# In[2]:

x = [0, 1, 2, 1, 0]
y = [0, 0, 1, 2, 2]
beta = [1, 1, 0, 1, 1]

grid = pygridgen.grid.Gridgen(x, y, beta, shape=(10, 5))

fig, ax = plt.subplots()
ax.plot(x, y, 'k-')
ax.plot(grid.x, grid.y, 'b.')
plt.show()


# ## Example with focus
# Note that `add_focus_x` means focus *along* the x axis, not
# *at* a specific x-postion.

# In[3]:

x = [0, 1, 2, 1, 0]
y = [0, 0, 1, 2, 2]
beta = [1, 1, 0, 1, 1]

focus = pygridgen.grid.Focus()
focus.add_focus_x(xo=0.5, factor=3, Rx=0.2)
focus.add_focus_y(yo=0.75, factor=5, Ry=0.1)
grid = pygridgen.grid.Gridgen(x, y, beta, shape=(20, 20), focus=focus)

fig, ax = plt.subplots()
ax.plot(x, y, 'k-')
ax.plot(grid.x, grid.y, 'b.')
plt.show()


# In[3]:



