# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import numpy as np
import matplotlib.pyplot as plt
%matplotlib inline

import iris

# <codecell>

# 1D example
x = np.array([1, 2, 3])
y = np.array([1, 2])
c = np.array([[1, 2, 3], [4, 5, 6]])
xx = np.r_[x[0], 0.5*(x[0:-1] + x[1:]), x[-1]]
yy = np.r_[y[0], 0.5*(y[0:-1] + y[1:]), y[-1]]
x2d,y2d = meshgrid(xx,yy)
plt.pcolormesh(x2d, y2d, c)

# <codecell>

print shape(c)
print shape(x2d)
print shape(y2d)

# <codecell>

a = [m n] = size(x);
x = [ x(:,1)  0.5*(x(:,1:n-1) + x(:,2:n))  x(:,n)];
y = [ y(:,1)  0.5*(y(:,1:n-1) + y(:,2:n))  y(:,n)];
x = [ x(1,:); 0.5*(x(1:m-1,:) + x(2:m,:)); x(m,:)];
y = [ y(1,:); 0.5*(y(1:m-1,:) + y(2:m,:)); y(m,:)];

