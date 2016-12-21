# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

flags=[]

# <codecell>

timestep_count=12
count=10

# <codecell>

if timestep_count*11./12. < count < timestep_count:
    flags.append('missing a little data')
elif timestep_count < count <= timestep_count*11./12.:
    flags.append('missing some data')
elif timestep_count/12. <= count <= timestep_count/2.:
    flags.append('missing lots of data')
elif count == 0:
    flags.append('no data')

# <codecell>

timestep_count

# <codecell>


