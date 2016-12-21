# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from IPython.lib.kernel import find_connection_file
from IPython.kernel import BlockingKernelClient
import os

# <codecell>

cf = '/home/epilib/Envs/env1/.ipython/profile_default/security/kernel-c5bd6be3-7df6-4b6f-8289-4d54908e39db.json'

# <codecell>

cf = '/home/usgs/.ipython/profile_default/security/kernel-632e13a5-00f5-422c-9588-34b195bc2349.json'

# <codecell>

km = BlockingKernelClient(connection_file=cf)

# <codecell>

km.load_connection_file()

# <codecell>

km.start_channels()

# <codecell>

def run_cell(km, code):
    # now we can run code.  This is done on the shell channel
    shell = km.shell_channel
    print
    print "running:"
    print code
    # execution is immediate and async, returning a UUID
    msg_id = shell.execute(code)
    # get_msg can block for a reply
    reply = shell.get_msg()

    status = reply['content']['status']
    if status == 'ok':
        print 'succeeded!'
    elif status == 'error':
        print 'failed!'
        for line in reply['content']['traceback']:
            print line

# <codecell>

run_cell(km, 'a=5')

# <codecell>

print len(good_data2)

# <codecell>

run_cell()

