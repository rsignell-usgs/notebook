# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

#Python hacker
import sys
def fact(x, acc=1):
    if x: return fact(x.__sub__(1), acc.__mul__(x))
    return acc
sys.stdout.write(str(fact(6)) + '\n')

# <codecell>


