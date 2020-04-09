# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 02:03:17 2020
@author: mwooten3

Raster describes a raster geoTIFF or VRT
"""

import os
import tempfile

from osgeo import gdal, osr, gdal_array
#from osgeo.osr import CoordinateTransformation

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
        
        # Check that the file is TIF or VRT
        extension = os.path.splitext(filePath)[1]       
        
        if extension != '.vrt' and extension != '.tif':
            raise RuntimeError('{} is not a VRT or TIF file'.format(filePath))

        self.filePath = filePath
        self.extension = extension
         
        self.baseName = os.path.basename(self.filePath).strip(extension)       
        self.baseDir = os.path.dirname(self.filePath)
        
        self.dataset = gdal.Open(self.filePath, gdal.GA_ReadOnly)
        
        self.noDataValue = self.dataset.GetRasterBand(1).GetNoDataValue()
        self.ogrDataType = self.dataset.GetRasterBand(1).DataType        
        self.ogrGeotransform = self.dataset.GetGeoTransform()
        self.ogrProjection = self.dataset.GetProjection()
        self.nColumns = int(self.dataset.RasterXSize)
        self.nRows = int(self.dataset.RasterYSize)
        self.nLayers = int(self.dataset.RasterCount)


    """
    #--------------------------------------------------------------------------
    # convertExtent()
    #--------------------------------------------------------------------------
    def convertExtent(self, targetEpsg):
                
        sourceSrs = osr.SpatialReference()
        sourceSrs.ImportFromEPSG(int(self.epsg())) 
    
        targetSrs = osr.SpatialReference()
        targetSrs.ImportFromEPSG(int(targetEpsg))
        
        (ulx, lry, lrx, uly) = self.extent()
    
        coordTrans = osr.CoordinateTransformation(sourceSrs, targetSrs)
        ulxOut, ulyOut = coordTrans.TransformPoint(ulx, uly)[0:2]
        lrxOut, lryOut = coordTrans.TransformPoint(lrx, lry)[0:2]
    
        return (ulxOut, lryOut, lrxOut, ulyOut)
    """

    #--------------------------------------------------------------------------
    # convertExtent()
    #--------------------------------------------------------------------------
    def convertExtent(self, targetEpsg):
        
        (ulx, lry, lrx, uly) = self.extent()

        ulxOut, ulyOut = SpatialHelper().convertCoords((ulx, uly), self.epsg(), targetEpsg)
        lrxOut, lryOut = SpatialHelper().convertCoords((lrx, lry), self.epsg(), targetEpsg)
    
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

    #---------------------------------------------------------------------------
    # extractBand()
    #---------------------------------------------------------------------------
    def extractBand(self, bandN, outTif = None):

        if not outTif:
            outTif = '{}.tif'.format(tempfile.mkdtemp())

        if not os.path.exists(outTif):

            cmd = 'gdal_translate'                      + \
                  ' -b {}'.format(bandN)        + \
                  ' ' + self.filePath                   + \
                  ' ' + outTif

            os.system(cmd)
            
        return outTif


    """ moved to init
    #--------------------------------------------------------------------------
    # nLayers()
    #--------------------------------------------------------------------------      
    def nLayers(self):
        
        try:
            nLayers = self.dataset.RasterCount
        except:
            nLayers = None
            
        return nLayers
    """
    
    #--------------------------------------------------------------------------
    # toArray() # Read raster into numpy array
    #--------------------------------------------------------------------------      
    def toArray(self):
        
        """ Read data stack into numpy array """
        typeCode = gdal_array.GDALTypeCodeToNumericTypeCode(self.ogrDataType)
        arr = np.zeros((self.nRows, self.nColumns, self.nLayers), typeCode)
        for b in range(self.nLayers): # For each band
            arr[:, :, b] = self.dataset.GetRasterBand(b + 1).ReadAsArray() # GDAL is 1-based while Python is 0-based
            
        return arr  
        
        
        