
# coding: utf-8

# In[10]:

import ipywidgets as widgets
from IPython.display import display
from traitlets import CInt, link


# In[11]:

class Counter(widgets.DOMWidget):
    value = CInt(0, sync=True)


# In[12]:

def button_plus(counter, w):
    counter.increment(+1)  

def button_minus(counter, w):
    counter.increment(-1) 


# In[19]:

counter = Counter()
def button_plus(name):
    print name
    counter.value += 1 if counter.value < 10 else 0
def button_minus(name):
    counter.value -= 1 if counter.value > 0 else 0
    


# In[20]:

# 1 step forward button
wplus = widgets.Button(description='>')

# 1 step backward button
wminus = widgets.Button(description='<')

# integer slider
wpick = widgets.IntSlider(value=0,min=0,max=10,step=1,description="time step")
wplus.on_click(button_plus)
wminus.on_click(button_minus)


# In[21]:

link((wpick, 'value'), (counter, 'value'));


# In[22]:

display(wminus, wpick, wplus)


# In[23]:

name


# In[ ]:



