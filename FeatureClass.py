#!/usr/bin/env python
"""
Created on Tue Mar 24 02:03:17 2020
@author: mwooten3

FeatureClass describes a polygon .shp or .gdb
"""

import os
import tempfile

from osgeo import ogr

from SpatialHelper import SpatialHelper

#------------------------------------------------------------------------------
# class FeatureClass
#------------------------------------------------------------------------------
class FeatureClass(object):
    
    #--------------------------------------------------------------------------
    # __init__
    #--------------------------------------------------------------------------
    def __init__(self, filePath):
        
        # Check that the file is SHP or GDB
        extension = os.path.splitext(filePath)[1]       
        
        if extension != '.gdb' and extension != '.shp':
            raise RuntimeError('{} is not a SHP or GDB file'.format(filePath))

        self.filePath = filePath
        self.extension = extension

        self.baseName = os.path.basename(self.filePath).strip(extension)     
        self.baseDir = os.path.dirname(self.filePath)

        # Set self.driver depending on the extention
        if self.extension == '.gdb':
            self.driver = ogr.GetDriverByName("FileGDB")
        else:
            self.driver = ogr.GetDriverByName("ESRI Shapefile")     
        
        self.dataset = self.driver.Open(self.filePath)
        self.layer = self.dataset.GetLayer()
        self.layerDefn = self.layer.GetLayerDefn()
        
        self.nFields = self.layerDefn.GetFieldCount()
        self.nFeatures = self.layer.GetFeatureCount()

   
    """ maybe could be generalized for FC but the 3dsi nd mask is funky,
        so, kept in ZFC 
    #--------------------------------------------------------------------------
    # applyNoDataMask()
    #--------------------------------------------------------------------------    
    def applyNoDataMask(self, mask):
    """
    
    #--------------------------------------------------------------------------
    # clipToExtent()
    #--------------------------------------------------------------------------    
    def clipToExtent(self, clipExtent, extentEpsg, outClip = None):
        
        # Expect extent to be tuple = (xmin, ymin, xmax, ymax)

        if not outClip:
            clipFile = '{}.shp'.format(tempfile.mkdtemp())
        else:
            clipFile = outClip

        # If EPSG of given coords is different from the EPSG of the feature class
        if str(extentEpsg) != str(self.epsg()):
            
            # Then transform coords to correct epsg
            (ulx1, lry1, lrx1, uly1) = clipExtent
            ulx, uly = SpatialHelper().convertCoords((ulx1, uly1), extentEpsg, self.epsg())
            lrx, lry = SpatialHelper().convertCoords((lrx1, lry1), extentEpsg, self.epsg())
            
            clipExtent = (ulx, lry, lrx, uly)
        
        extent = ' '.join(map(str,clipExtent))
    
        cmd = 'ogr2ogr -clipsrc {} -spat {} -f '.format(extent, extent) + \
                    '"ESRI Shapefile" {} {}'.format(clipFile, self.filePath)
        os.system(cmd)
        
        return clipFile

    #--------------------------------------------------------------------------
    # convertExtent()
    #--------------------------------------------------------------------------
    def convertExtent(self, targetEpsg):
        
        (ulx, lry, lrx, uly) = self.extent()

        ulxOut, ulyOut = SpatialHelper().convertCoords((ulx, uly), self.epsg(), targetEpsg)
        lrxOut, lryOut = SpatialHelper().convertCoords((lrx, lry), self.epsg(), targetEpsg)
    
        return (ulxOut, lryOut, lrxOut, ulyOut)
    
    #--------------------------------------------------------------------------
    # createCopy()
    #--------------------------------------------------------------------------    
    def createCopy(self, copyName):
        
        cmd = 'ogr2ogr {} {}'.format(copyName, self.filePath)
        os.system(cmd)
        
        return copyName  
        
    #--------------------------------------------------------------------------
    # epsg()
    #--------------------------------------------------------------------------
    def epsg(self):         

        srs = self.layer.GetSpatialRef()
        
        return srs.GetAuthorityCode(None)    
    
    #--------------------------------------------------------------------------
    # extent()
    #--------------------------------------------------------------------------
    def extent(self):
        
        (ulx, lrx, lry, uly) = self.layer.GetExtent()
        
        return (ulx, lry, lrx, uly)    

    #--------------------------------------------------------------------------
    # fieldNames()
    #--------------------------------------------------------------------------
    def fieldNames(self):
        
        fields = []
    
        for n in range(self.nFields):
            fieldDefn = self.layerDefn.GetFieldDefn(n)
            fields.append(fieldDefn.name)
                
        return fields
