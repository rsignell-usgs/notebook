# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# #Calculate the total amount of tracer in old ECOM-si Mass Bay runs
# Mike Mickelson wanted to how the total mass of effluent within Mass Bay differs between the four scenarios of stratification and outfall location in this report:
# [Section 5: Effluent Dilution Simulations in Massachusetts Bay: An Evaluation of Relocating Greater Boston’s Sewage Outfall](http://pubs.usgs.gov/circ/2007/1302/sections/CIRC1302_Section5.SewageOutfall.pdf)
# 
# So I found the old netCDF files, updated them to be CF-Compliant, put them on our THREDDS server, and this notebook computes the amount of tracer in each of the 4 seasons (winter, spring, summer, fall) for both the Boston Harbor outfall location and the Mass Bay location

# <codecell>

import netCDF4

# <codecell>

def plot_var(url,var='conc',layer=0,tind=0):
    nc = netCDF4.Dataset(url)
    ncv = nc.variables
    lon = ncv['lon'][:]
    lat = ncv['lat'][:]
    h = ncv['depth'][:]
    c = ncv[var][tind,layer,:,:]
    c = ma.masked_where(h==-99999.,c)
    pcolormesh(lon,lat,c)

# <codecell>

def ctotal(url,var,tind):
    '''
    compute the total amount of ECOM variable 'var' at a specified time step
    '''
    nc = netCDF4.Dataset(url)
    ncv = nc.variables
    lon = ncv['lon'][:]
    lat = ncv['lat'][:]
    dx = ncv['h1'][:]
    dy = ncv['h2'][:]
    h = ncv['depth'][:]
    sigma = ncv['zpos'][:]
    dz = -diff(sigma)
    # get all but bottom layer (bottom is dummy layer in ECOM)
    c = ncv[var][tind,0:-1,:,:]
    # multiply 3D array of C by dz, then sum in the vertical to get 2D array
    ctot = sum(rollaxis(c,0,3)*dz,axis=2)
    c2d = ma.masked_where(h==-99999.,ctot)
    ctot = sum((c2d*h*dx*dy).ravel())
    return ctot

# <codecell>

url='http://geoport.whoi.edu/thredds/dodsC/mbay/nonc/deer'
for i in arange(4):
    print ctotal(url,'conc',i)
    
plot_var(url,var='conc',layer=0,tind=0)

# <codecell>

url='http://geoport.whoi.edu/thredds/dodsC/mbay/nonc/bb'
for i in arange(4):
    print ctotal(url,'conc',i)
    
plot_var(url,var='conc',layer=0,tind=0)

