# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import os
with open('/tmp/foo2.txt', 'w') as ff: ff.write(str(os.environ['PATH']))

# <codecell>

os.path

# <codecell>

import sys
with open('/tmp/foo2.txt', 'w') as ff: ff.write(str(sys.path))

# <codecell>


