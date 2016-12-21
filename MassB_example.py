import utools
import netCDF4

reload(utools) #because I'm actively working on this module!

data_url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM2_FORECAST.nc'
bndry_file = 'MassB.bry'

nc = netCDF4.Dataset(data_url)
nc.variables.keys()

#I use a mapping of FVCOM variable names to common names so that the class methods can also
#work with SELFE and ADCIRC which have different var names
#This seemed easier than finding them by CF long_names etc
var_map = { 'longitude':'lon', \
            'latitude':'lat', \
            'time':'time', \
            'u_velocity':'u', \
            'v_velocity':'v', \
            'nodes_surrounding_ele':'nv',\
            'eles_surrounding_ele':'nbe',\
          }  

necofs = utools.ugrid(data_url)

print 'Downloading data'
#necofs.get_data(var_map,tindex=[0,1,1]) #First time step only
necofs.get_data(var_map) #All time steps in file

necofs.adjust_time() #GNOME can't handle pre 1980 start dates (in units)

necofs.get_bndry(bndry_file) 
#This file was pre-generated for this grid (somewhat manually as open water/land boundaries
#are not specified in the model output

necofs.atts['nbe']['order'] = 'cw'
#GNOME needs to know whether the elements are ordered clockwise (FVCOM) or counter-clockwise (SELFE)

print 'Writing to GNOME file'
necofs.write_unstruc_grid('TestforGNOME.nc')