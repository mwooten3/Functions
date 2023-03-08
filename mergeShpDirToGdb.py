# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 14:37:42 2020
@author: mwooten3

merge a directory of shapefiles --> output gdb
"""

import os, sys
import arcpy
import time

indir = raw_input("Enter input shapefile directory: ")
outgdb = raw_input("Enter output *.gdb: ")


start = time.time()

# Set output to WGS_84 GCS and env to indir
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(4326)
arcpy.env.workspace = indir

if not arcpy.Exists(outgdb):
    arcpy.CreateFileGDB_management(os.path.dirname(outgdb), os.path.basename(outgdb))
    
if outgdb.endswith('.gdb'):
    gdbname = os.path.basename(outgdb).replace('.gdb', '')
    outgdb = os.path.join(outgdb, gdbname)

    
print "Input directory: {}".format(indir)
print "Output geodatabase: {}".format(outgdb)

# Get list from input shp dir
fcs = arcpy.ListFeatureClasses()

print "\nProcessing {} input files to create output .gdb\n".format(len(fcs))

out = arcpy.Merge_management(fcs, outgdb) 
#print out

print "Made {} in {} minutes".format(out, round((time.time()-start)/60, 4))
