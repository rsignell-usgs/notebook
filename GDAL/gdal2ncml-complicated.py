
# coding: utf-8

# In[25]:

from osgeo import gdal,ogr,osr


# In[ ]:

raster = r'/usgs/data0/bathy/sandy/zip3/big.tif'
ofile =  r'/usgs/data2/notebook/data/big.ncml'


# In[ ]:

def GetExtent(gt,cols,rows):
    ''' Return list of corner coordinates from a geotransform

        @type gt:   C{tuple/list}
        @param gt: geotransform
        @type cols:   C{int}
        @param cols: number of columns in the dataset
        @type rows:   C{int}
        @param rows: number of rows in the dataset
        @rtype:    C{[float,...,float]}
        @return:   coordinates of each corner
    '''
    ext=[]
    xarr=[0,cols]
    yarr=[0,rows]

    for px in xarr:
        for py in yarr:
            x=gt[0]+(px*gt[1])+(py*gt[2])
            y=gt[3]+(px*gt[4])+(py*gt[5])
            ext.append([x,y])
            print x,y
        yarr.reverse()
    return ext


# In[ ]:

def ReprojectCoords(coords,src_srs,tgt_srs):
    ''' Reproject a list of x,y coordinates.

        @type geom:     C{tuple/list}
        @param geom:    List of [[x,y],...[x,y]] coordinates
        @type src_srs:  C{osr.SpatialReference}
        @param src_srs: OSR SpatialReference object
        @type tgt_srs:  C{osr.SpatialReference}
        @param tgt_srs: OSR SpatialReference object
        @rtype:         C{tuple/list}
        @return:        List of transformed [[x,y],...[x,y]] coordinates
    '''
    trans_coords=[]
    transform = osr.CoordinateTransformation( src_srs, tgt_srs)
    for x,y in coords:
        x,y,z = transform.TransformPoint(x,y)
        trans_coords.append([x,y])
    return trans_coords


# In[3]:

ds=gdal.Open(raster)

gt=ds.GetGeoTransform()
cols = ds.RasterXSize
rows = ds.RasterYSize
ext=GetExtent(gt,cols,rows)

src_srs=osr.SpatialReference()
src_srs.ImportFromWkt(ds.GetProjection())
#tgt_srs=osr.SpatialReference()
#tgt_srs.ImportFromEPSG(4326)
tgt_srs = src_srs.CloneGeogCS()

geo_ext=ReprojectCoords(ext,src_srs,tgt_srs)


# In[5]:

ext


# In[14]:

ncml = '''<netcdf xmlns="http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2"
    location="/usgs/data0/bathy/srtm30plus_v1.nc">
    <variable name="lon" shape="lon" type="double">
     <attribute name="units" value="degrees_east"/>
     <values start="-180.00" increment="+0.008333333333333333"/>
    </variable>
    <variable name="lat" shape="lat" type="double">
     <attribute name="units" value="degrees_north"/>
     <values start="90.00" increment="-0.008333333333333333"/>
    </variable>
    <variable name="topo">
     <attribute name="units" value="meters"/>
     <attribute name="long_name" value="Topography"/>
    </variable>
    <attribute name="Conventions" value="CF-1.0"/>
    <attribute name="title" value="SRTM30_v1"/>
   </netcdf>'''


# In[15]:

print(ncml)


# In[16]:

gt


# In[22]:

#replace lon_min
ncml = ncml.replace('-180.00',str(gt[0]))

#replace lon_increment
ncml = ncml.replace('+0.008333333333333333',str(gt[1]))

#replace lat_max
ncml = ncml.replace('90.00',str(gt[3]))

#replace lat_increment
ncml = ncml.replace('-0.008333333333333333',str(gt[5]))

#replace file location
ncml = ncml.replace(r'/usgs/data0/bathy/srtm30plus_v1.nc',raster)

print(ncml)


# In[ ]:




# In[ ]:



