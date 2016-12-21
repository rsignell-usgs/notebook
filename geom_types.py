from osgeo import ogr

# map geometry types to names:
ogr2text = {
    ogr.wkbGeometryCollection:'GeometryCollection',
    ogr.wkbGeometryCollection25D:'GeometryCollection25D',
    ogr.wkbLineString:'LineString',
    ogr.wkbLineString25D:'LineString25D',
    ogr.wkbLinearRing:'LinearRing',
    ogr.wkbMultiLineString:'MultiLineString',
    ogr.wkbMultiLineString25D:'MultiLineString25D',
    ogr.wkbMultiPoint:'MultiPoint',
    ogr.wkbMultiPoint25D:'MultiPoint25D',
    ogr.wkbMultiPolygon:'MultiPolygon',
    ogr.wkbMultiPolygon25D:'MultiPolygon25D',
    ogr.wkbPoint:'Point',
    ogr.wkbPoint25D:'Point25D',
    ogr.wkbPolygon:'Polygon',
    ogr.wkbPolygon25D:'Polygon25D',
    ogr.wkbUnknown:'Unknown',
}

text2ogr = dict( [ [ogr2text[k],k] for k in ogr2text.keys()] )
