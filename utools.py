import numpy as np
from netCDF4 import Dataset, num2date, date2num

class ugrid:
    """
    A class for dealing with unstructured grid model output and converting to GNOME format
    Although I use variable names consistent with FVCOM, by passing in a var_map dict the 
    variable names can be customized for SELFE or ADCIRC
    Right now the attribute specifying whether the elements are orderd clockwise or counter
    clockwise needs to be manually added before writing to GNOME format (GNOME requres this, 
    but its not often specified in the model output)
    
    This uses the Python netCDF4 library which can access local files or use OPeNDAP urls
    (if its built with OPeNDAP enabled) -- for Windows Christopher Gohlke's site has binaries: 
    http://www.lfd.uci.edu/~gohlke/pythonlibs/
        

    """
    def __init__(self,FileName=None):
            
        if FileName is not None:
            self.FileName = FileName
            self.Dataset = Dataset(FileName)
            
    def get_data(self,var_map,tindex=None):
    
        ''' 
        var_map is a dict mapping model variable names to common names
        tindex can be used to subset in time --> tindex = [start,stop,step]
        '''
        
        self.data = dict()
        self.atts = dict()
        
        t = self.Dataset.variables[var_map['time']]
        if not tindex:
            tindex=[0,len(t),1]
        self.atts['time'] = t.__dict__ 
        self.data['time'] = t[tindex[0]:tindex[1]:tindex[2]]
        
        lat = self.Dataset.variables[var_map['latitude']]
        self.atts['lat'] = lat.__dict__
        self.data['lat'] = lat[:]
        
        lon = self.Dataset.variables[var_map['longitude']]
        self.atts['lon'] = lon.__dict__
        self.data['lon'] = lon[:]
        
        u = self.Dataset.variables[var_map['u_velocity']]
        self.atts['u'] = u.__dict__

        if len(np.shape(u))==3:
            self.data['u'] = u[tindex[0]:tindex[1]:tindex[2],0,:]
        elif len(np.shape(u))==2:
            self.data['u'] = u[tindex[0]:tindex[1]:tindex[2],:]
        else:
            print "Error:velocity is not 2 or 3 dimensional"
            raise
 
        v = self.Dataset.variables[var_map['v_velocity']]
        self.atts['v'] = v.__dict__
        if len(np.shape(v))==3:
            self.data['v'] = v[tindex[0]:tindex[1]:tindex[2],0,:]
        elif len(np.shape(v))==2:
            self.data['v'] = v[tindex[0]:tindex[1]:tindex[2],:]
        else:
            print "Error:velocity is not 2 or 3 dimensional"
            raise       

        nbe = self.Dataset.variables[var_map['eles_surrounding_ele']]
        self.atts['nbe'] = nbe.__dict__
        self.data['nbe'] = nbe[:]
        
        nv = self.Dataset.variables[var_map['nodes_surrounding_ele']]
        self.atts['nv'] = nv.__dict__
        self.data['nv'] = nv[:]
        
        
    def get_bndry(self,bnd_file): #read in boundary file into att['bnd']
        bnd = []
        f = open(bnd_file,'r')
        for line in f:
            vals = [int(val) for val in line.split()]
            bnd.append(vals)
        
        self.data['bnd'] = np.array(bnd)
        self.atts['bnd'] = {'long_name':'Boundary segment information required for GNOME model'}
        
        
    def adjust_time(self):
        model_time = num2date(self.data['time'],units=self.atts['time']['units'])
        new_units = 'days since 1980-1-1 00:00:00'
        new_model_time = date2num(model_time,units=new_units)
        self.data['time'] = new_model_time
        self.atts['time']['units'] = new_units
        
    def write_unstruc_grid(self,ofn):
        
        """
        
        Write GNOME compatible netCDF file (netCDF3) from unstructured (triangular) grid data
        
        """  
        nc = Dataset(ofn,'w',format='NETCDF3_CLASSIC')
        
        # Global Attributes
        setattr(nc,'grid_type','Triangular')
        
        # add Dimensions
        nc.createDimension('node',len(self.data['lon']))
        nc.createDimension('nele',np.shape(self.data['nbe'])[1])
        nc.createDimension('nbnd',len(self.data['bnd']))
        nc.createDimension('nbi',4)
        #nc.createDimension('sigma',1) #coming soon?
        nc.createDimension('time',None)
        nc.createDimension('three',3)
        
        # create variables
        nc_time = nc.createVariable('time','f4',('time',))
        nc_lon = nc.createVariable('lon','f4',('node'))
        nc_lat = nc.createVariable('lat','f4',('node'))
        nc_nbe = nc.createVariable('nbe','int32',('three','nele'))
        nc_nv = nc.createVariable('nv','int32',('three','nele'))
        nc_bnd = nc.createVariable('bnd','int32',('nbnd','nbi'))
        if self.data['u'].shape[-1] == len(self.data['lon']): #velocities on nodes
            nc_u = nc.createVariable('u','f4',('time','node'))
            nc_v = nc.createVariable('v','f4',('time','node'))
        else: #velocities on elements
            nc_u = nc.createVariable('u','f4',('time','nele'))
            nc_v = nc.createVariable('v','f4',('time','nele'))
        
        #u = np.squeeze(u); v = np.squeeze(v)
        
        #add data to netcdf file
        nc_time[:] = self.data['time']
        nc_lon[:] = self.data['lon']
        nc_lat[:] = self.data['lat']
        nc_u[:] = self.data['u']
        nc_v[:] = self.data['v']
        nc_bnd[:] = self.data['bnd']
        nc_nbe[:] = self.data['nbe']
        nc_nv[:] = self.data['nv']
        
        #add variable attributes to netcdf file
        for an_att in self.atts['time'].iteritems():
           setattr(nc_time,an_att[0],an_att[1])
        
        for an_att in self.atts['lon'].iteritems():
            setattr(nc_lon,an_att[0],an_att[1])
        
        for an_att in self.atts['lat'].iteritems():
            setattr(nc_lat,an_att[0],an_att[1])
        
        for an_att in self.atts['bnd'].iteritems():
            setattr(nc_bnd,an_att[0],an_att[1])

        for an_att in self.atts['nbe'].iteritems():
            setattr(nc_nbe,an_att[0],an_att[1])

        for an_att in self.atts['nv'].iteritems():
            setattr(nc_nv,an_att[0],an_att[1])
        
        for an_att in self.atts['u'].iteritems():
           setattr(nc_u,an_att[0],an_att[1])
        
        for an_att in self.atts['v'].iteritems():
           setattr(nc_v,an_att[0],an_att[1])
        
        nc.close()
    
        
            

