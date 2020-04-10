# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 18:16:48 2019

DG footprints files are separated by sensor and year

For a group of individual DG footprint files, select by intersect with 
    an input shapefile and output the results
    
    Add to list
Merge shapefiles in list


"""

import arcpy
import os, glob, sys

#######################################################################
# VARIABLES #
indir = 'E:\MaggieData\NGA_footprints\DigitalGlobeFootprints' # Where input DG files are kept
ddir = 'E:\\MaggieData\\ProposalStuff\\Eric' # main dir
outdir = os.path.join(ddir, 'footprints', 'individual_DigitalGlobe')
tempdir = os.path.join(outdir, 'temp')
if not os.path.isdir(tempdir): os.mkdir(tempdir)

areaShp = os.path.join(ddir, 'shp', 'allSites.shp') # shp used for selection
areaName =  os.path.splitext(os.path.basename(areaShp))[0]
if not os.path.isfile(areaShp):
    sys.exit("Area shp {} does not exist. Try again".format(areaShp))

outMerge = os.path.join(ddir, 'footprints', 'DG_WVstrips__{}.shp'.format(areaName))
#######################################################################

mergeList = []
for inShp in glob.glob(os.path.join(indir, 'WV*shp')):
    print "Processing {}".format(inShp)
    bname = os.path.splitext(os.path.basename(inShp))[0]
    featureLayer = os.path.join(tempdir, '{}_layer'.format(bname))   
    outShp = os.path.join(outdir, '{}__{}.shp'.format(bname, areaName))

    if os.path.isfile(outShp):
        print " Output already exists\n"
        mergeList.append(outShp)
        continue

    print "Selecting features..."
    # Process: Make Feature Layer
    arcpy.MakeFeatureLayer_management(inShp, featureLayer)#, "", "", "FID FID VISIBLE NONE;Shape Shape VISIBLE NONE;CATALOGID CATALOGID VISIBLE NONE;ACQDATE ACQDATE VISIBLE NONE;MNOFFNADIR MNOFFNADIR VISIBLE NONE;MXOFFNADIR MXOFFNADIR VISIBLE NONE;AVOFFNADIR AVOFFNADIR VISIBLE NONE;MNSUNAZIM MNSUNAZIM VISIBLE NONE;MXSUNAZIM MXSUNAZIM VISIBLE NONE;AVSUNAZIM AVSUNAZIM VISIBLE NONE;MNSUNELEV MNSUNELEV VISIBLE NONE;MXSUNELEV MXSUNELEV VISIBLE NONE;AVSUNELEV AVSUNELEV VISIBLE NONE;MNTARGETAZ MNTARGETAZ VISIBLE NONE;MXTARGETAZ MXTARGETAZ VISIBLE NONE;AVTARGETAZ AVTARGETAZ VISIBLE NONE;MNPANRES MNPANRES VISIBLE NONE;MXPANRES MXPANRES VISIBLE NONE;AVPANRES AVPANRES VISIBLE NONE;MNMULTIRES MNMULTIRES VISIBLE NONE;MXMULTIRES MXMULTIRES VISIBLE NONE;AVMULTIRES AVMULTIRES VISIBLE NONE;STEREOPAIR STEREOPAIR VISIBLE NONE;BROWSEURL BROWSEURL VISIBLE NONE;CLOUDCOVER CLOUDCOVER VISIBLE NONE;PLATFORM PLATFORM VISIBLE NONE;x1 x1 VISIBLE NONE;y1 y1 VISIBLE NONE;x2 x2 VISIBLE NONE;y2 y2 VISIBLE NONE;x3 x3 VISIBLE NONE;y3 y3 VISIBLE NONE;x4 x4 VISIBLE NONE;y4 y4 VISIBLE NONE;IMAGEBANDS IMAGEBANDS VISIBLE NONE")

    # Process: Select Layer By Location
    arcpy.SelectLayerByLocation_management(featureLayer, "INTERSECT", areaShp, "", "NEW_SELECTION", "NOT_INVERT")
  
    # Process: Copy Features
    arcpy.CopyFeatures_management(featureLayer, outShp, "", "0", "0", "0")

    mergeList.append(outShp)
    print ''

if os.path.isfile(outMerge):
    sys.exit('Output merge file {} already exists. Try again'.format(outMerge))
                        
print "Merging {} inputs into {}".format(len(mergeList), outMerge)
arcpy.Merge_management(";".join(mergeList), outMerge)
                                         
    










