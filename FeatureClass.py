#!/usr/bin/env python
"""
Created on Tue Mar 24 02:03:17 2020
@author: mwooten3

FeatureClass describes a polygon .shp or .gdb
"""

import os
import tempfile

from osgeo import ogr, gdal

from SpatialHelper import SpatialHelper

#------------------------------------------------------------------------------
# class FeatureClass
#------------------------------------------------------------------------------
class FeatureClass(object):
    
    #--------------------------------------------------------------------------
    # __init__
    #--------------------------------------------------------------------------
    def __init__(self, filePath):

        # Check that the file exists - must use .exists not .isfile in case FC is GDB
        if not os.path.exists(filePath):
            raise RuntimeError("Feature class {} does not exist".format(filePath))
            
        # Check that the file is SHP or GDB
        extension = os.path.splitext(filePath)[1]       
        
        if extension != '.gdb' and extension != '.shp' and extension != '.gpkg':
            raise RuntimeError('{} is not a SHP or GDB file'.format(filePath))

        self.filePath = filePath
        self.extension = extension

        self.baseName = os.path.basename(self.filePath).replace(extension, '')     
        self.baseDir = os.path.dirname(self.filePath)

        # Set self.driver depending on the extention
        if self.extension == '.gdb':
            self.driver = ogr.GetDriverByName("FileGDB")
        elif self.extension == '.gpkg': 
            self.driver = ogr.GetDriverByName("GPKG")
        elif self.extension == '.shp':
            self.driver = ogr.GetDriverByName("ESRI Shapefile")
        else:
            raise RuntimeError("Could not find driver from {}".format(self.extension))
            
        #import pdb; pdb.set_trace()        
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
    # addToFeatureClass() - Append self to output GDB/GPKG/SHP. If output 
    #                       already exists, the fields must match
    #--------------------------------------------------------------------------  
    def addToFeatureClass(self, outFcPath, outEPSG = 4326, moreArgs = None):

        # Get output driver based off output extension
        ext = os.path.splitext(outFcPath)[1]   
        if ext == '.gdb':
            outDrv = 'FileGDB'
        elif ext == '.gpkg':
            outDrv = 'GPKG'
        elif ext == '.shp':
            outDrv = 'ESRI Shapefile' #**CHECK THIS**
        else:
            print("\nUnrecognized output extension '{}'".format(ext))
            return None
                
        print("\nUpdating/creating {} with {}".format(outFcPath, self.filePath))
                
        layerName = os.path.basename(outFcPath).replace(ext, '')
        cmd = 'ogr2ogr -nln {} -a_srs EPSG:4326 -t_srs EPSG:4326'.format(layerName)
                
        if os.path.exists(outFcPath):
            	
            # If output file exists, confirm that field names are the same
            outFc = FeatureClass(outFcPath)
            if outFc.fieldNames() != self.fieldNames():
                
                stmt = "Field names for output feature class ({}) do not match field names for input ({})".format(outFc.fieldNames(), self.fieldNames())
                print(stmt)
                
                outFc = None
                return None
            
            cmd += ' -update -append'
            outFc = None
            
        if moreArgs: # Right now just a string but eventually be list
            cmd += ' {}'.format(moreArgs)
                    
        cmd += ' -f "{}" {} {}'.format(outDrv, outFcPath, self.filePath) 
                
        print('', cmd)
        os.system(cmd)
            
        return None
    
    #--------------------------------------------------------------------------
    # clipToExtent() - must supply the target extent and that extents' epsg
    #                  projecting output to new EPSG is optional 
    #--------------------------------------------------------------------------    
    def clipToExtent(self, clipExtent, extentEpsg, tEpsg = None, 
                                         outClip = None, sqlQuery = None):
        
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

        cmd = 'ogr2ogr -clipsrc {} -spat {} -f '.format(extent, extent) +  \
                    '"ESRI Shapefile" --config PG_USE_COPY YES '        +  \
                        '{} {}'.format(clipFile, self.filePath)
                    
        # Set output projection if targetEpsg is supplied
        if tEpsg: cmd += ' -t_srs EPSG:{}'.format(tEpsg)
        
        # Set SQL query on src if statement is supplied:
        if sqlQuery: cmd += ' -clipsrcsql "{}"'.format(sqlQuery)
        print('', cmd) # for now
        os.system(cmd)
        
        if not os.path.isfile(clipFile):
            raise RuntimeError('Could not perform clip of input zonal feature class')
        
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
    
    #--------------------------------------------------------------------------
    # removeField()
    #--------------------------------------------------------------------------
    def removeField(self, fieldName):
        
        # This does not seem to work all the time. Still leave it here for now
        
        # Open dataset this way for this:
        ds = gdal.OpenEx(self.filePath, gdal.OF_VECTOR | gdal.OF_UPDATE)
        
        ds.ExecuteSQL("ALTER TABLE {} DROP COLUMN {}".format(self.baseName, fieldName))

        ds = None
        
        return None
