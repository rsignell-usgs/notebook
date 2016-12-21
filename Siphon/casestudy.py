# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# # netCDF File Visualization Case Study
# 
# I was asked by a colleague to visualize data contained within this [netCDF file](https://motherlode.ucar.edu/repository/entry/show/RAMADDA/Unidata/Staff/Julien+Chastang/netcdf-explore?entryid=c7239224-d3fe-45d8-b100-43ae043824c3) ([OPeNDAP link](https://motherlode.ucar.edu/repository/opendap/41f2b38a-4e70-4135-8ff8-dbf3d1dcbfc1/entry.das)) with Python. What follows is an exploration of how I achieved that objective. Because this exercise touches upon many technologies related to Unidata, it makes for an interesting case study. We will be meandering through,
# 
# - netCDF
# - WMO GRIB metadata
# - Map projections
# - xray data analysis library
# - cartopy visualization library

# <markdowncell>

# # Crack Open the File
# 
# To get our bearings let's see what there is inside our netCDF file. We will be using the [xray library](https://github.com/xray/xray) to dig inside our netCDF data. xray is similar to pandas, but for the [Common Data Model](http://www.unidata.ucar.edu/software/thredds/current/netcdf-java/CDM/). We could have just used the [netcdf4-python library](https://github.com/Unidata/netcdf4-python) but xray has output that is more nicely formatted. Let's first import xray and open the dataset.

# <codecell>

import xray
ds = xray.open_dataset('https://motherlode.ucar.edu/repository/opendap/41f2b38a-4e70-4135-8ff8-dbf3d1dcbfc1/entry.das', 
                       decode_times=False)
print(ds)

# <markdowncell>

# # Dimensions, Coordinates, Data Variables
# 
# As far as the dimensions and coordinates go, the most relevant and important coordinates variables are `x` and `y`. We can see the data variables, such as, temperature (`t`), mixing ratio (`mr`), and potential temperature (`th`), are mostly on a 1901 x 1801 grid. There is also the mysterious `nav` dimension and associated data variables which we will be examining later.
# 
# Let's set a goal of visualizing **potential temperature** with the [Cartopy](http://scitools.org.uk/cartopy/) plotting package.
# 
# The first step is to get more information concerning the variables we are interested in. For example, let's look at _potential temperature_ or `th`.

# <codecell>

print(ds['th'])

# <markdowncell>

# # potential temperature (`th`)
# 
# Let's grab the data array for potential temperature (`th`).

# <codecell>

th = ds['th'].values[0][0]
print(th)

# <markdowncell>

# # To Visualize the Data, We have to Decrypt the Projection
# 
# In order, to visualize the data that are contained within a two-dimensional array onto a map that represents a three-dimensional globe, we need to understand the projection of the data.
# 
# We can make an educated guess these are contained in the data variables with the `nav` cooridinate variable.
# 
# Specifically,
# 
# - `grid_type`
# - `grid_type_code`
# - `x_dim`
# - `y_dim`
# - `Nx`
# - `Ny`
# - `La1`
# - `Lo1`
# - `LoV`
# - `Latin1`
# - `Latin2`
# - `Dx`
# - `Dy`
# 
# **But what are these??**

# <headingcell level=1>

# For Grins, Let's Scrutinize the `grid_type_code`

# <codecell>

print(ds['grid_type_code'])

# <markdowncell>

# # Google to the Rescue
# 
# A simple Google search of `GRIB-1 GDS data representation type` takes us to
# [A GUIDE TO THE CODE FORM FM 92-IX Ext. GRIB Edition 1 from 1994](http://www.wmo.int/pages/prog/www/WMOCodes/Guides/GRIB/GRIB1-Contents.html "GRIB") document. Therein one can find an explanation of the variables needed to understand the map projection. Let's review these variables.

# <codecell>

print(ds['grid_type_code'].values[0])

# <markdowncell>

# # What is `grid_type_code` of `5`?
# 
# Let's look at [Table 6 ](http://www.wmo.int/pages/prog/www/WMOCodes/Guides/GRIB/GRIB1-Contents.html "GRIB Projection Definitions"). A `grid_type_code` of `5` corresponds to a projection of **Polar Stereographic**.

# <headingcell level=1>

# Next up `grid_type`

# <codecell>

grid_type = ds['grid_type'].values
print('The grid type is ', grid_type[0])

# <markdowncell>

# # Uh oh! Polar Stereographic or Lambert Conformal??
# 
# _Note that this newest piece of information relating to a Lambert Conformal projection disagrees with the  earlier projection information about a Polar Stereographic projection._ There is a **bug** in the metadata description of the projection.

# <markdowncell>

# # Moving on Anyway, next `Nx` and `Ny`
# 
# According to the grib documentation `Nx` and `Ny` represent the number grid points along the x and y axes. Let's grab those.

# <codecell>

nx, ny = ds['Nx'].values[0], ds['Ny'].values[0]
print(nx, ny)

# <markdowncell>

# # `La1` and `Lo1` 
# 
# Next let's get `La1` and `Lo1` which are defined as the "first grid points" These are probably the latitude and longitude for one of the corners of the grid.

# <codecell>

la1, lo1 = ds['La1'].values[0], ds['Lo1'].values[0]
print(la1, lo1)

# <markdowncell>

# # `Latin1` and `Latin2`
# 
# Next up are the rather mysteriously named `Latin1` and `Latin2` variables. When I first saw these identifiers, I thought they referred to a Unicode block, but in fact they relate to the secants of the projection cone. I do not know why they are called "Latin" and this name is confusing. **At any rate, we can feel comfortable that we are dealing with Lambert Conformal rather than Polar Stereographic.**
# 
# ![Lambert Conformal](http://www.geo.hunter.cuny.edu/~jochen/gtech201/Lectures/Lec6concepts/Map%20coordinate%20systems/Lambert%20Conformal%20Conic_files/image002.gif "Lambert Conformal")
# 
# Credit: http://www.geo.hunter.cuny.edu/~jochen   

# <codecell>

latin1, latin2 = ds['Latin1'].values[0], ds['Latin2'].values[0]
print(latin1, latin2)

# <markdowncell>

# # The Central Meridian for the Lambert Conformal Projection, `LoV`
# 
# If we are defining a Lambert Conformal projection, we will require the central meridian that the GRIB documentation refers to as `LoV`.

# <codecell>

lov = ds['LoV'].values[0]
print(lov)

# <markdowncell>

# # `Dx` and `Dy`
# 
# Finally, let's look at the grid increments. In particular, we need to find the units.

# <codecell>

print(ds['Dx'])
print(ds['Dy'])

# <markdowncell>

# # Units for `Dx` and `Dy`
# 
# The units for the deltas are in meters.

# <codecell>

dx,dy = ds['Dx'].values[0],ds['Dy'].values[0]
print(dx,dy)

# <markdowncell>

# # Let's Review What We Have
# 
# We now have all the information we need to understand the Lambert projection:
# 
# - The secants of the Lambert Conformal projection (`Latin1`, `Latin2`)
# - The central meridian of the projection (`LoV`)
# 
# Moreover, we have additional information that shows how the data grid relates to the projection:
#     
# - The number of grid points in x and y (`Nx`, `Ny`)
# - The delta in meters between grid point (`Dx`, `Dy`)
# - The first latitude and longitude of the data (`first latitude`, `first longitude`).

# <markdowncell>

# # We are Ready for Visualization (almost)!
# 
# Let's import **cartopy** and **matplotlib**.

# <codecell>

%matplotlib inline

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib as mpl

# <headingcell level=1>

# Define the Lambert Conformal Projection with Cartopy

# <codecell>

proj = ccrs.LambertConformal(central_longitude=lov,standard_parallels=(latin1,latin2))

# <markdowncell>

# # Lambert Conformal Grid Extents
# 
# - To plot the data we need the `left`,`right`,`bottom`,`top` extents of the grid **expressed in Lambert Conformal
# coordinates**.
# - __**Key point**: The projection coordinate systems have flat topology and Euclidean distance.__

# <markdowncell>

# #  Calculating the Extents
# 
# Remember, we have:
# 
# - The number of grid points in x and y (`Nx`, `Ny`)
# - The delta in meters between grid point (`Dx`, `Dy`)
# - The first latitude and longitude of the data (`first latitude`, `first longitude`).
# 
# We have one of the corners in latitude and longitude, but we need to convert it LC coordinates and derive the other corner.

# <markdowncell>

# # Platte Carrée Projection
# 
# The Platte Carrée Projection is a very simple X,Y/Cartesian projection. It is used a lot in Cartopy because it allows you to express coordinates in familiar Latitude and Longitudes. **Remember**: The projection coordinate systems have flat topology and Euclidean distance.

# <markdowncell>

# # Platte Carrée
# 
# ![Platte Carree](https://upload.wikimedia.org/wikipedia/commons/8/83/Equirectangular_projection_SW.jpg "Platte Carree")
# 
# Source: [Wikipedia Source](https://en.wikipedia.org/wiki/Equirectangular_projection)

# <headingcell level=1>

# Create the PlatteCarre Cartopy Projection

# <codecell>


pc = ccrs.PlateCarree()

# <markdowncell>

# # Convert Corner from Lat/Lon PlatteCarre to LC
# 
# The `transform_point` method translates coordinates from one projection coordinate system to the other.

# <codecell>

left,bottom = proj.transform_point(lo1,la1,pc)
print(left,bottom)

# <markdowncell>

# # Derive Opposite Corner
# 
# Derive the opposite corner from the number of points and the delta. **Again**, we can do this because the projection coordinate systems have flat topology and Euclidean distance.

# <codecell>

right,top = left + nx*dx,bottom + ny*dy
print(right,top)

# <markdowncell>

# # Plot It Up!
# 
# We now have the extents, we are ready to plot.

# <codecell>

#Define the figure
fig = plt.figure(figsize=(12, 12))

# Define the extents and add the data
ax = plt.axes(projection=proj)
extents = (left, right, bottom, top)
ax.contourf(th, origin='lower', extent=extents, transform=proj)

# Add bells and whistles
ax.coastlines(resolution='50m', color='black', linewidth=2)
ax.add_feature(ccrs.cartopy.feature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces_lines', scale='50m',facecolor='none'))
ax.add_feature(ccrs.cartopy.feature.BORDERS, linewidth='1', edgecolor='black')
ax.gridlines()

plt.show()

# <markdowncell>

# # Exercises for the Reader
# 
# - The extents are actually not perfect and snip the image. Why? Fix.
# - Add a colorbar and jazz up the plot.
# - Trick question: Can you label the axes with latitude and longitudes?
# - Try a different projection which should be fairly easy with Cartopy.

# <codecell>

th.shape

# <codecell>

th[0,0]

# <codecell>


