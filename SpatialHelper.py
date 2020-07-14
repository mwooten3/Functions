# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 16:23:55 2020
@author: mwooten3

SpatialHelper.py

Functions associated with Gdal/OGR

Not the best organization, should definitely put these functions into classes
that actually make sense, but whatever for now

Code that uses SpatialHelper():
    - FeatureClass.py
    - Raster.py
    - something i cant remember/multiple 3DSI zonal stats scripts
    - prepareTrainingData.py
    - others probably

# TO DO:
# make spatial helper be a class for a point or polygon feature aka OGR geometry!!!!

# Change it to GeometryFeature()

# can be point, line, polygon, multipolygon -- self.geometryType

# can convert a point to a different coordinate system (convertPoint instead of convertCoords)
    # OR just combine convertCoords with reprojectPoint
# calls to SH.convertCoords in other scripts can be replaced with reprojectPoint()
    # point objects would have to be passed instead of lat/lon
# in all functions, shape becomes self
# can reprojectShape() based on shape type (init)

# can determine UTM zone of feature point polygon, multipolygon



# NOTES (for GDAL classes later):

# import time
# start = time.time()
# round((time.time()-start)/60, 4)
    
"""
import os
import tempfile

from osgeo import osr, ogr

#------------------------------------------------------------------------------
# class SpatialHelper
#------------------------------------------------------------------------------
class SpatialHelper(object):
    
    #--------------------------------------------------------------------------
    # __init__
    #--------------------------------------------------------------------------
    
    # no init for now
    
     #--------------------------------------------------------------------------
    # convertCoords()
    #--------------------------------------------------------------------------
    def convertCoords(self, coords, sourceEpsg, targetEpsg):
        
        # Coords expected = (lon, lat)
        (x, y) = coords
                
        sourceSrs = osr.SpatialReference()
        sourceSrs.ImportFromEPSG(int(sourceEpsg)) 
    
        targetSrs = osr.SpatialReference()
        targetSrs.ImportFromEPSG(int(targetEpsg))
    
        coordTrans = osr.CoordinateTransformation(sourceSrs, targetSrs)
        xOut, yOut = coordTrans.TransformPoint(x, y)[0:2]
    
        return (xOut, yOut)   
    
   #def determineUtmZone(self, coords, utmShp = ''): 
   
    #--------------------------------------------------------------------------
    # determineUtmEpsg()
    
    # Determine the UTM (WGS84) zone for a polygon/point objects
    # Must supply the SRS of the input shape
    #--------------------------------------------------------------------------
    def determineUtmEpsg(self, shape, shapeSrs):   
        
        UTM_FILE = '/att/gpfsfs/briskfs01/ppl/mwooten3/GeneralReference/UTM_Zone_Boundaries.shp'
        
        # First, if the SRS of geometry object is not 4326, convert it
        if int(shapeSrs) != 4326:
            shape = self.reprojectShape(shape, int(shapeSrs), 4326)
            
        # Get the extent of the shape (for irregular shapes, this may
        # simplify things too much but for most, it should be fine)
        (xmin, xmax, ymin, ymax) = shape.GetEnvelope()
        
        # Now that coords are in WGS84, we can...
        
        # If lat/lon coords are outside of UTM extent
        if ymax >= 84.0:
            
            return 32661 # Universal Polar (UPS) North
        
        if ymin <= -80.0:
            
            return 32761 # UPS South
        
        # If shape is point type, we must buffer it by a small amount
        if shape.GetGeometryName() == 'POINT':
            xmin = xmin - 0.01 # hundredth of a degree
            ymin = ymin - 0.01
            xmax = xmax + 0.01
            ymax = ymax + 0.01
            
        # If within extent, determine UTM epsg by clipping shp
        # Clip the UTM Shapefile for this bounding box.
        clipFile = tempfile.mkdtemp()

        cmd = 'ogr2ogr'                        + \
              ' -clipsrc'                      + \
              ' ' + str(xmin)                   + \
              ' ' + str(ymin)                   + \
              ' ' + str(xmax)                   + \
              ' ' + str(ymax)                   + \
              ' -f "ESRI Shapefile"'           + \
              ' -select "Zone_Hemi"'           + \
              ' "' + clipFile   + '"'          + \
              ' "' + UTM_FILE + '"'

        os.system(cmd)

        # Read clipped shapefile
        driver = ogr.GetDriverByName("ESRI Shapefile")
        ds = driver.Open(clipFile, 0)
        layer = ds.GetLayer()

        maxArea = 0
        for feature in layer:
            area = feature.GetGeometryRef().GetArea()
            if area > maxArea:
                maxArea = area
                zone, hemi = feature.GetField('Zone_Hemi').split(',')

        """
        # Configure proj.4 string
        proj4 = '+proj=utm +zone={} +ellps=WGS84 +datum=WGS84 +units=m +no_defs'.format(zone)
        if hemi.upper() == 'S': proj4 += ' +south'
        """
        
        # Configure EPSG from zone/hemisphere
        epsg = '326'
        if hemi.upper() == 'S':
            epsg = '327'
        epsg += '{}'.format(zone.zfill(2))        
        
        # Remove temporary clipFile and its auxiliary files
        driver.DeleteDataSource(clipFile)

        return epsg
        
    #--------------------------------------------------------------------------
    # reprojectShape()
    # reprojects a OGR geometry object
    #--------------------------------------------------------------------------    
    def reprojectShape(self, shape, sEpsg, tEpsg):
    
        shapeType = shape.GetGeometryName()
        
        if shapeType == 'POINT':
            outShape = self.reprojectPoint(shape, sEpsg, tEpsg)
            
        elif shapeType == 'POLYGON':
            outShape = self.reprojectPolygon(shape, sEpsg, tEpsg)
            
        elif shapeType == 'MULTIPOLYGON':
            outShape = self.reprojectMultiPolygon(shape, sEpsg, tEpsg)
            
        else:
            raise RuntimeError("Input shape must be (MULTI)POLYGON or POINT")
            
        return outShape

    def reprojectPoint(self, point, sEpsg, tEpsg):
        
        # OGR point object --> projected OGR point object
        
        lon, lat = point.GetX(), point.GetY() 
        
        outLon, outLat = self.convertCoords((lon, lat), sEpsg, tEpsg)
        
        # Reconstruct OGR point geometry with projected coords:
        outPoint = ogr.Geometry(ogr.wkbPoint)
        outPoint.AddPoint(outLon, outLat)
        
        return outPoint
    
    def reprojectPolygon(self, polygon, sEpsg, tEpsg):
        
        # OGR polygon object --> projected OGR polygon object
    
        # Set up output polygon
        outRing = ogr.Geometry(ogr.wkbLinearRing)
        outPolygon = ogr.Geometry(ogr.wkbPolygon)
    
        # Iterate through points and reproject, then add to new polygon feature
        ring = polygon.GetGeometryRef(0)
        
        for pt in range(ring.GetPointCount()):
            
            lon, lat, z = ring.GetPoint(pt)
            
            # Construct OGR point to call reprojectPoint()
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(lon, lat)
            
            outPoint = self.reprojectPoint(point, sEpsg, tEpsg)
            
            # Then add projected point to output polyon ring:
            outRing.AddPoint(outPoint.GetX(), outPoint.GetY())
            
        # Then add projected ring coords to output polygon    
        outPolygon.AddGeometry(outRing)
        
        return outPolygon
    
    def reprojectMultiPolygon(self, multiPolygon, sEpsg, tEpsg):
        
        # OGR multipolygon object --> projected OGR multipolygon object
    
        # Set up output multipolygon
        outMultiPolygon = ogr.Geometry(ogr.wkbMultiPolygon)
    
        # Iterate through polygons and reproject, then add to new multipolygon feature
        for part in range(multiPolygon.GetGeometryCount()):
            
            polygon = multiPolygon.GetGeometryRef(part)
            
            outPolygon = self.reprojectPolygon(polygon, sEpsg, tEpsg)
              
            outMultiPolygon.AddGeometry(outPolygon)
        
        return outMultiPolygon   
    
    
    
    
    