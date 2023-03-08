# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 02:03:17 2020
@author: mwooten3

Raster describes a raster geoTIFF or VRT
"""

import os
import tempfile

from osgeo import gdal, osr, gdal_array

from SpatialHelper import SpatialHelper

import numpy as np

#------------------------------------------------------------------------------
# class Raster
#------------------------------------------------------------------------------
class Raster(object):
    
    #--------------------------------------------------------------------------
    # __init__
    #--------------------------------------------------------------------------
    def __init__(self, filePath):
        
        # Check that the file exists
        if not os.path.isfile(filePath):
            raise RuntimeError("Raster {} does not exist".format(filePath))
        
        # Check that the file is TIF or VRT
        extension = os.path.splitext(filePath)[1]       
        
        if extension != '.vrt' and extension != '.tif':
            raise RuntimeError('{} is not a VRT or TIF file'.format(filePath))

        self.filePath  = filePath
        self.extension = extension
         
        self.baseName = os.path.basename(self.filePath).replace(extension, '')       
        self.baseDir  = os.path.dirname(self.filePath)
        
        self.dataset = gdal.Open(self.filePath, gdal.GA_ReadOnly)
        
        self.noDataValue     = self.dataset.GetRasterBand(1).GetNoDataValue()
        self.ogrDataType     = self.dataset.GetRasterBand(1).DataType        
        self.ogrGeotransform = self.dataset.GetGeoTransform()
        self.ogrProjection   = self.dataset.GetProjection()
        self.nColumns        = int(self.dataset.RasterXSize)
        self.nRows           = int(self.dataset.RasterYSize)
        self.nLayers         = int(self.dataset.RasterCount)

    #--------------------------------------------------------------------------
    # convertExtent()
    #--------------------------------------------------------------------------
    def convertExtent(self, targetEpsg):
        
        (ulx, lry, lrx, uly) = self.extent()

        ulxOut, ulyOut = SpatialHelper().convertCoords((ulx, uly), 
                                                       self.epsg(), targetEpsg)
        lrxOut, lryOut = SpatialHelper().convertCoords((lrx, lry), 
                                                       self.epsg(), targetEpsg)
    
        return (ulxOut, lryOut, lrxOut, ulyOut)

    
    #--------------------------------------------------------------------------
    # epsg() [projection]
    #--------------------------------------------------------------------------
    def epsg(self):            

        prj = self.dataset.GetProjection()
        srs = osr.SpatialReference(wkt=prj)
        
        return srs.GetAuthorityCode(None)
            
    #--------------------------------------------------------------------------
    # extent()
    #--------------------------------------------------------------------------
    def extent(self):
        
        ulx, xres, xskew, uly, yskew, yres  = self.dataset.GetGeoTransform()
        lrx = ulx + (self.dataset.RasterXSize * xres)
        lry = uly + (self.dataset.RasterYSize * yres)
        
        return (ulx, lry, lrx, uly)

    #--------------------------------------------------------------------------
    # extractBand()
    #--------------------------------------------------------------------------
    def extractBand(self, bandN, outTif = None):

        if not outTif:
            outTif = '{}.tif'.format(tempfile.mkdtemp())

        if not os.path.isfile(outTif):

            cmd = 'gdal_translate'                      + \
                  ' -b {}'.format(bandN)                + \
                  ' ' + self.filePath                   + \
                  ' ' + outTif

            os.system(cmd)
            
        return outTif

    #--------------------------------------------------------------------------
    # resolution()
    #--------------------------------------------------------------------------
    def resolution(self):
        
        resX = self.ogrGeotransform[1]
        resY = -self.ogrGeotransform[5]
        
        if resX != resY:
            print("Warning. X pixel size ({}) is different from Y ({})" \
                                                           .format(resX, resY))
        
        return float(resX), float(resY)
        
    #--------------------------------------------------------------------------
    # toArray() # Read raster into numpy array
    #--------------------------------------------------------------------------      
    def toArray(self):
        
        """ Read data stack into numpy array """
        typeCode = gdal_array.GDALTypeCodeToNumericTypeCode(self.ogrDataType)
        arr = np.zeros((self.nRows, self.nColumns, self.nLayers), typeCode)
        
        for b in range(self.nLayers): # For each band
            
            arr[:, :, b] = self.dataset.GetRasterBand(b + 1).ReadAsArray() 
            
        return arr  

    #--------------------------------------------------------------------------
    # utmZone()
    
    # Determine the UTM (WGS84) Zone for a Raster object    
    #--------------------------------------------------------------------------
    def utmEpsg(self):   
        
        # First, if the SRS of the Raster is not 4326, convert extent
        if int(self.epsg()) != 4326:
            (xmin, ymin, xmax, ymax) = self.convertExtent(4326)
            
        # Otherwise, just unpack it
        else:
            (xmin, ymin, xmax, ymax) = self.extent()

        # Now that coords are in Lat/Lon WGS84, we can pass to main function
        extent = (xmin, xmax, ymin, ymax)
        
        return SpatialHelper().determineUtmEpsg(extent)
        
        