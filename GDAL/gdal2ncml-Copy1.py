
# coding: utf-8

# In[39]:

from osgeo import gdal


# In[40]:

raster = r'/usgs/data0/bathy/sandy/zip3/big.nc'
ofile =  r'/usgs/data2/notebook/data/sandy_3sb.ncml'
title = 'sandy3s'


# In[41]:

ds=gdal.Open(raster)

gt=ds.GetGeoTransform()
print(gt)


# In[42]:

ncml = '''<netcdf xmlns="http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2"
    location="/usgs/data0/bathy/srtm30plus_v1.nc">
    <dimension name="lon" orgName="x"/>
    <dimension name="lat" orgName="y"/>
    <variable name="lon" shape="lon" type="double">
     <attribute name="units" value="degrees_east"/>
     <values start="-180.00" increment="+0.008333333333333333"/>
    </variable>
    <variable name="lat" shape="lat" type="double">
     <attribute name="units" value="degrees_north"/>
     <values start="90.00" increment="-0.008333333333333333"/>
    </variable>
    <variable name="topo" orgName="Band1">
     <attribute name="units" value="meters"/>
     <attribute name="long_name" value="elevation"/>
     <attribute name="standard_name" value="height_above_geopotential_surface"/>
     <attribute name="grid_mapping" value="crs"/>
    </variable>
    <variable name="crs">
     <attribute name="grid_mapping_name" value="latitude_longitude"/>
     <attribute name="longitude_of_prime_meridian" type="float" value="0.0"/>
     <attribute name="semi_major_axis" type="float" value="6378137.0"/>
     <attribute name="inverse_flattening" type="float" value="298.257223563"/>
     <attribute name="geopotential_datum_name" value="NAVD88"/>
     <attribute name="crs_wkt" value="COMPD_CS[\\\"NAD83 + NAVD88 height\\\",GEOGCS[\\\"NAD83\\\",DATUM[\\\"North_American_Datum_1983\\\",SPHEROID[\\\"GRS 1980\\\",6378137,298.257222101,AUTHORITY[\\\"EPSG\\\",\\\"7019\\\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\\\"EPSG\\\",\\\"6269\\\"]],PRIMEM[\\\"Greenwich\\\",0,AUTHORITY[\\\"EPSG\\\",\\\"8901\\\"]],UNIT[\\\"degree\\\",0.0174532925199433,AUTHORITY[\\\"EPSG\\\",\\\"9122\\\"]],AUTHORITY[\\\"EPSG\\\",\\\"4269\\\"]],VERT_CS[\\\"NAVD88 height\\\",VERT_DATUM[\\\"North American Vertical Datum 1988\\\",2005,AUTHORITY[\\\"EPSG\\\",\\\"5103\\\"],EXTENSION[\\\"PROJ4_GRIDS\\\",\\\"g2012a_conus.gtx,g2012a_alaska.gtx,g2012a_guam.gtx,g2012a_hawaii.gtx,g2012a_puertorico.gtx,g2012a_samoa.gtx\\\"]],UNIT[\\\"metre\\\",1,AUTHORITY[\\\"EPSG\\\",\\\"9001\\\"]],AXIS[\\\"Up\\\",UP],AUTHORITY[\\\"EPSG\\\",\\\"5703\\\"]],AUTHORITY[\\\"EPSG\\\",\\\"5498\\\"]]"/>
    </variable>
    <attribute name="Conventions" value="CF-1.0"/>
    <attribute name="title" value="SRTM30_v1"/>
   </netcdf>'''


# In[43]:

ncml = '''<netcdf xmlns="http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2"
   location="/usgs/data0/bathy/srtm30plus_v1.nc">
   <dimension name="lon" orgName="x"/>
   <dimension name="lat" orgName="y"/>
   <variable name="lon" shape="lon" type="double">
    <attribute name="units" value="degrees_east"/>
    <values start="-180.00" increment="+0.008333333333333333"/>
   </variable>
   <variable name="lat" shape="lat" type="double">
    <attribute name="units" value="degrees_north"/>
    <values start="90.00" increment="-0.008333333333333333"/>
   </variable>
   <variable name="topo" orgName="Band1">
    <attribute name="units" value="meters"/>
    <attribute name="long_name" value="elevation"/>
    <attribute name="standard_name" value="height_above_geopotential_surface"/>
    <attribute name="grid_mapping" value="crs"/>
   </variable>
   <variable name="crs" type="int">
    <attribute name="grid_mapping_name" value="latitude_longitude"/>
    <attribute name="longitude_of_prime_meridian" type="float" value="0.0"/>
    <attribute name="semi_major_axis" type="float" value="6378137.0"/>
    <attribute name="inverse_flattening" type="float" value="298.257223563"/>
    <attribute name="geopotential_datum_name" value="NAVD88"/>
    <attribute name="crs_wkt" value="COMPD_CS[&quot;NAD83 + NAVD88 height&quot;,GEOGCS[&quot;NAD83&quot;,DATUM[&quot;North_American_Datum_1983&quot;,SPHEROID[&quot;GRS 1980&quot;,6378137,298.257222101,AUTHORITY[&quot;EPSG&quot;,&quot;7019&quot;]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[&quot;EPSG&quot;,&quot;6269&quot;]],PRIMEM[&quot;Greenwich&quot;,0,AUTHORITY[&quot;EPSG&quot;,&quot;8901&quot;]],UNIT[&quot;degree&quot;,0.0174532925199433,AUTHORITY[&quot;EPSG&quot;,&quot;9122&quot;]],AUTHORITY[&quot;EPSG&quot;,&quot;4269&quot;]],VERT_CS[&quot;NAVD88 height&quot;,VERT_DATUM[&quot;North American Vertical Datum 1988&quot;,2005,AUTHORITY[&quot;EPSG&quot;,&quot;5103&quot;],EXTENSION[&quot;PROJ4_GRIDS&quot;,&quot;g2012a_conus.gtx,g2012a_alaska.gtx,g2012a_guam.gtx,g2012a_hawaii.gtx,g2012a_puertorico.gtx,g2012a_samoa.gtx&quot;]],UNIT[&quot;metre&quot;,1,AUTHORITY[&quot;EPSG&quot;,&quot;9001&quot;]],AXIS[&quot;Up&quot;,UP],AUTHORITY[&quot;EPSG&quot;,&quot;5703&quot;]],AUTHORITY[&quot;EPSG&quot;,&quot;5498&quot;]]"/>
   </variable>
   <attribute name="Conventions" value="CF-1.0"/>
   <attribute name="title" value="SRTM30_v1"/>
  </netcdf>'''


# In[44]:

#replace title
ncml = ncml.replace('SRTM30_v1',title)

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


# In[45]:

with open(ofile, "w") as text_file:
    text_file.write("{}".format(ncml))

netcdf big {
dimensions:
        x = 4212 ;
        y = 3912 ;

variables:
        char GDAL_Geographics ;
                GDAL_Geographics:Northernmost_Northing = 39.755 ;
                GDAL_Geographics:Southernmost_Northing = 36.49500000000011 ;
                GDAL_Geographics:Easternmost_Easting = -70.24500000000012 ;
                GDAL_Geographics:Westernmost_Easting = -73.755 ;
                GDAL_Geographics:spatial_ref = "GEOGCS[\"GCS_North_American_1983\",DATUM[\"D_North_American_1983\",SPHEROID[\"GRS_1980\",6378137,298.257222101]],PRIMEM[\"Greenwich\",0],UNIT[\"Degree\",0.017453292519943295],VERTCS[\"Instantaneous Water Level height\",VERT_DATUM[\"Instantaneous Water Level\",2005],UNIT[\"Meter\",1]]]" ;
                GDAL_Geographics:GeoTransform = "-73.755 0.000833333 0 39.755 0 -0.000833333 " ;
                GDAL_Geographics:grid_mapping_name = "Geographics Coordinate System" ;
                GDAL_Geographics:long_name = "Grid_latitude" ;
        float Band1(y, x) ;
                Band1:_FillValue = -1.e+10f ;
                Band1:grid_mapping = "GDAL_Geographics" ;
                Band1:long_name = "GDAL Band Number 1" ;

// global attributes:
                :Conventions = "CF-1.0" ;

# In[46]:

value="COMPD_CS[\\\"NAD83 + NAVD88 height\\\",GEOGCS[\\\"NAD83\\\",DATUM[\\\"North_American_Datum_1983\\\",SPHEROID[\\\"GRS 1980\\\",6378137,298.257222101,AUTHORITY[\\\"EPSG\\\",\\\"7019\\\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\\\"EPSG\\\",\\\"6269\\\"]],PRIMEM[\\\"Greenwich\\\",0,AUTHORITY[\\\"EPSG\\\",\\\"8901\\\"]],UNIT[\\\"degree\\\",0.0174532925199433,AUTHORITY[\\\"EPSG\\\",\\\"9122\\\"]],AUTHORITY[\\\"EPSG\\\",\\\"4269\\\"]],VERT_CS[\\\"NAVD88 height\\\",VERT_DATUM[\\\"North American Vertical Datum 1988\\\",2005,AUTHORITY[\\\"EPSG\\\",\\\"5103\\\"],EXTENSION[\\\"PROJ4_GRIDS\\\",\\\"g2012a_conus.gtx,g2012a_alaska.gtx,g2012a_guam.gtx,g2012a_hawaii.gtx,g2012a_puertorico.gtx,g2012a_samoa.gtx\\\"]],UNIT[\\\"metre\\\",1,AUTHORITY[\\\"EPSG\\\",\\\"9001\\\"]],AXIS[\\\"Up\\\",UP],AUTHORITY[\\\"EPSG\\\",\\\"5703\\\"]],AUTHORITY[\\\"EPSG\\\",\\\"5498\\\"]]"



# In[47]:

value



# In[48]:

value="COMPD_CS[\"NAD83 + NAVD88 height\",GEOGCS[\"NAD83\",DATUM[\"North_American_Datum_1983\",SPHEROID[\"GRS 1980\",6378137,298.257222101,AUTHORITY[\"EPSG\",\"7019\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6269\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4269\"]],VERT_CS[\"NAVD88 height\",VERT_DATUM[\"North American Vertical Datum 1988\",2005,AUTHORITY[\"EPSG\",\"5103\"],EXTENSION[\"PROJ4_GRIDS\",\"g2012a_conus.gtx,g2012a_alaska.gtx,g2012a_guam.gtx,g2012a_hawaii.gtx,g2012a_puertorico.gtx,g2012a_samoa.gtx\"]],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"Up\",UP],AUTHORITY[\"EPSG\",\"5703\"]],AUTHORITY[\"EPSG\",\"5498\"]]"


# In[49]:

value


# In[ ]:



