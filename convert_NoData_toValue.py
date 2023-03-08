# Purpose: to take an input tif, and convert its NoData pixels to 100 (or another value as specified after imports)



import os, sys, glob
import numpy as np
from timeit import default_timer as timer
import datetime

import gdal
from osgeo.gdal import *
gdal.UseExceptions() # enable exceptions to report errors
drvtif = gdal.GetDriverByName("GTiff")

# Paramaters to change:
inputFile = sys.argv[1] #'/att/gpfsfs/briskfs01/ppl/mwooten3/MEaSURES/BenPoulter/MEaSURES-ocean_2000-2015_global/MEaSURES-percentOcean_2000-2015_global__1km-WGS84.tif'
outputFile = inputFile.replace('.tif', '__fixNoData.tif')
value = 100

def find_elapsed_time(start, end): # example time = round(find_elapsed_time(start, end),3) where start and end = timer()
    elapsed_min = (end-start)/60
    return float(elapsed_min)

def tif_to_array(inTif): # open raster, get paramaters, read as array

    ds = gdal.Open(inTif)

    dt = ds.GetRasterBand(1).DataType
    gt = ds.GetGeoTransform()
    proj = ds.GetProjection()
    ncols = ds.RasterXSize
    nrows = ds.RasterYSize

    arr = ds.GetRasterBand(1).ReadAsArray()
    ndval = ds.GetRasterBand(1).GetNoDataValue()

    return (arr, dt, gt, proj, ncols, nrows, ndval)

def array_to_tif(outfile, inarr, gt, proj, ncols, nrows, dtype, ndval=None): # if we don't want to give output a no data value, don't supply it

    drv = drvtif.Create(outfile, ncols, nrows, 1, dtype, options = [ 'COMPRESS=LZW' ])
    drv.SetGeoTransform(gt)
    drv.SetProjection(proj)
    if ndval: drv.GetRasterBand(1).SetNoDataValue(ndval)
    drv.GetRasterBand(1).WriteArray(inarr)

    return outfile

print "Converting {} to {}...\n".format(inputFile, outputFile)

(arr, dt, gt, proj, ncols, nrows, ndval) = tif_to_array(inputFile)

outArr = np.copy(arr)
outArr[arr == ndval] = value

array_to_tif(outputFile, outArr, gt, proj, ncols, nrows, dt, ndval=None)