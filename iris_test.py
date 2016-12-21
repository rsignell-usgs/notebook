# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Using Iris to access NCEP CFSR 30-year Wave Hindcast

# <codecell>


# <codecell>

from IPython.core.display import HTML
HTML('<iframe src=http://scitools.org.uk/iris/ width=800 height=350></iframe>')

# <codecell>

import numpy
import matplotlib.pyplot as plt
import datetime as dt

import iris
import iris.plot as iplt
import cartopy.crs as ccrs

# <codecell>

def time_near(cube,start):
    timevar=cube.coord('time')
    itime = timevar.nearest_neighbour_index(timevar.units.date2num(start))
    return timevar.points[itime]

# <codecell>

# DAP URL: 30 year East Coast wave hindcast (Wave Watch 3 driven by CFSR Winds) 
#cubes = iris.load('http://geoport.whoi.edu/thredds/dodsC/fmrc/NCEP/ww3/cfsr/4m/best'); # 4 arc minute resolution
cubes = iris.load('http://geoport.whoi.edu/thredds/dodsC/fmrc/NCEP/ww3/cfsr/10m/best'); # 10 arc minute resolution

# <codecell>

print cubes

# <codecell>

hsig=cubes[0]

# <codecell>

# use contraints to select geographic subset and nearest time
mytime=dt.datetime(1991,10,31,12)  #specified time...   Nov 1, 1991 was the "Perfect Storm"
#mytime=dt.datetime.utcnow()      # .... or now
slice=hsig.extract(iris.Constraint(time=time_near(hsig,mytime),
    longitude=lambda cell: -71.5 < cell < -64.0,
    latitude=lambda cell: 40.0 < cell < 46.0))

# <codecell>

print slice

# <codecell>

slice.coord(axis='X').coord_system=iris.coord_systems.GeogCS(654321)
slice.coord(axis='Y').coord_system=iris.coord_systems.GeogCS(654321)
slice.add_aux_coord(iris.coords.DimCoord(0, standard_name='forecast_period', units='hours'))
slice.add_aux_coord(iris.coords.DimCoord(0, "height", units="m"))

# <codecell>

slice.dim_coords[0]

# <codecell>

print[coord.name() for coord in slice.coords()]

# <codecell>

#save slice as grib2
iris.save(slice,'hsig.grib2')

