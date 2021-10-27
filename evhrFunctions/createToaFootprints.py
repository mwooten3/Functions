#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Stand-alone script to make a footprints .shp using a text list of input rasters
Will also accept a directory and use all tifs in there (though easiest to just use wildcards at that point)

This may eventually go in EVHR

For now it's in Functions (and EVHR_API/otherCode) on ADAPT

"""

import os, sys
import glob

from collections import OrderedDict

from osgeo import ogr

Input = sys.argv[1] # input text list or dir
Output = sys.argv[2] # output shp path/name

# Validate inputs
if os.path.isdir(Input):
    inTifs = [f for f in glob.glob(os.path.join(Input, '*tif'))] # TEST
elif os.path.isfile(Input) and Input.endswith('.txt'):
    with open(Input, 'r') as inf:
       inTifs = [f.strip() for f in inf.readlines() if f.strip().endswith('.tif')]
else: print("Input must be a directory or text file")

if len(inTifs) == 0:
    sys.exit("Input {} had 0 .tifs. Please try again".format(Input))

if not Output.endswith('.shp'):
    sys.exit("Output file must be a .shp")


pathFieldName = 'filePath'
newFields = OrderedDict([('fileName', [ogr.OFTString, 100]), ('sensor', [ogr.OFTString, 4]), 
             ('specType', [ogr.OFTString, 4]), ('catalogID', [ogr.OFTString, 35]),
             ('date', [ogr.OFTString, 8]), ('year', [ogr.OFTInteger, None]), 
             ('month', [ogr.OFTString, 2]), ('day', [ogr.OFTString, 2])])
    
    
# Create .shp from list of input .tif files
print("BUILDING .SHP for {} inputs\n".format(len(inTifs)))
cmd = 'gdaltindex -t_srs "EPSG:4326" -src_srs_name SRS -write_absolute_path -tileindex {} {} {}'.format(pathFieldName, Output,' '.join(inTifs))
print(" {}".format(cmd))
os.system(cmd)

# Now edit the shapefile 

# Not using FeatureClass class here (two reasons: weird stuff about layer/adding fields this way, and might eventually add to EVHR)
# Open output file:
src = ogr.Open(Output, 1)
layer = src.GetLayer()

#* Might be good practice here to check existing fields but oh well for now

# Create new fields:
for field in newFields:
    
    fieldSpecs = newFields[field] # first entry is type, second is size/length
    
    fieldDefn = ogr.FieldDefn(field, fieldSpecs[0])
    if fieldSpecs[1]: fieldDefn.SetWidth(fieldSpecs[1]) # Text fields might have a length we want to set

    layer.CreateField(fieldDefn)
    
# Lastly, populate the fields
for feature in layer: 
    
    fullpath = feature.GetField(pathFieldName)
    bname = os.path.basename(fullpath).strip('-toa.tif')
    imgDate = bname.split('_')[1]

    feature.SetField('fileName', '{}-toa.tif'.format(bname))
    feature.SetField('sensor', bname[0:4]) 
    feature.SetField('specType', bname.split('_')[2])
    feature.SetField('catalogID', bname.split('_')[3])
    feature.SetField('date', imgDate)
    feature.SetField('year', int(imgDate[0:4]))
    feature.SetField('month', imgDate[4:6])
    feature.SetField('day', imgDate[6:8])
    
    layer.SetFeature(feature)
    feature = None
    
layer = None
