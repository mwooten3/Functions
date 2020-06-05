# -*- coding: utf-8 -*-
"""
Created on Wed May 20 12:25:28 2020
@author: mwooten3

Purpose:
  Create the footprints shapefile for an AOI so that it can be used in
   featureCountToRaster.py

Inputs: 
  AOI shp [siteName.shp]; nga footprints shp; output directory
Output:
  Site-specific footprints shapefile ready for density map code
  
Process:
  Intersect AOI shp with Footprints
  Find UTM zone, project to UTM
  Create stripName field
  Import field map for dissolve and
  dissolve on stripName
  add "one" column
  return final output shp
  
# 6/5: Adding an option to process for DG footprints:
  DG footprints are already strips, so no need to add stripName field or Dissolve

  Think about making input be footprintType:
      if fprntype == 'inHouse': nga_canon scenes
      if fprntype == 'DG': DigitalGlobeStrips
    Then use fprntype to determine steps
 
  
  
"""

import arcpy
import os#, sys
import argparse

arcpy.env.overwriteOutput = True # Overwrite outputs (at least while testing)

"""
# Input variables (as CL inputs):
areaShp = sys.argv[1]
footprintShp = sys.argv[2]
outputDir = sys.argv[3] # final destination of site footprint strips
"""

def createField(inShp, fieldName, fieldType, expression):

    print "   Adding and creating field {} with expression {}\n".format(fieldName, expression)
    
    # Add the field to shp
    arcpy.AddField_management(inShp, fieldName, fieldType, "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

    # Calculate the field
    arcpy.CalculateField_management(inShp, fieldName, expression, "PYTHON_9.3", "")

    return inShp # Edits shapefile, does not return a new one

def createStripsShp(inShp, outShp, fieldMap, field = '"stripName"'):

    print "   Dissolving on {} field to get output strips shp {}\n".format(field, outShp)

    # Dissolve on stripName field
    arcpy.Dissolve_management(inShp, outShp, field, fieldMap, "SINGLE_PART", "DISSOLVE_LINES")

    return outShp
                 
def findUtmZone(inShp, ddir):

    # Get UTM zone of AOI and return an arcpy SR object
    
    bname = os.path.basename(inShp).replace('.shp', '')
    
    UTM = 'E:\MaggieData\General Reference Data\UTM_Zone_Boundaries\UTM_Zone_Boundaries.shp'
    
    # Clip input with UTM
    outUtmClip = os.path.join(ddir, '{}__clippedUTM.shp'.format(bname))
    arcpy.Clip_analysis(UTM, inShp, outUtmClip, "")

    # Add area column and calculate it
    arcpy.AddGeometryAttributes_management(outUtmClip, "AREA_GEODESIC", "", "", "")

    # Now find clipped UTM zone polygon with largest area
    maxArea = 0
    features = arcpy.SearchCursor(outUtmClip)
    for feat in features:
        area = feat.getValue("AREA_GEO")
        if area > maxArea:
            maxArea = area
            zone, hemi = feat.getValue('Zone_Hemi').split(',')

    # Now configure the EPSG code 
    if hemi.upper() == 'N': # 326 + zone for N
        epsgCode = '326{}'.format(zone.zfill(2))
    else:                   # 327 + zone for S
        epsgCode = '327{}'.format(zone.zfill(2))

    """ If usine proj4 string:
        proj4 = '+proj=utm +zone={} +ellps=WGS84 +datum=WGS84 +units=m +no_defs'.format(zone)
        if hemi.upper() == 'S': proj4 += ' +south'
    """
    
    #print " UTM Zone: EPSG:{}".format(epsgCode)
    
    # And create SR object to return for project
    return arcpy.SpatialReference(int(epsgCode))
    
def selectFootprintsForAOI(areaShp, fprintFc, ddir):
    
    areaName = os.path.basename(areaShp).replace('.shp', '')

    print "   Selecting footprints from {} for {}\n".format(fprintFc, areaShp)
    
    # Make selection shp a feature layer
    arcpy.MakeFeatureLayer_management(fprintFc, 'fprintLayer')#, "", "", "SHAPE SHAPE VISIBLE NONE;OBJECTID OBJECTID VISIBLE NONE;STRIP_ID STRIP_ID VISIBLE NONE;SCENE_ID SCENE_ID VISIBLE NONE;STATUS STATUS VISIBLE NONE;SENSOR SENSOR VISIBLE NONE;CATALOG_ID CATALOG_ID VISIBLE NONE;ORDER_ID ORDER_ID VISIBLE NONE;PROD_CODE PROD_CODE VISIBLE NONE;COUNTRY COUNTRY VISIBLE NONE;SPEC_TYPE SPEC_TYPE VISIBLE NONE;ACQ_TIME ACQ_TIME VISIBLE NONE;CLOUDCOVER CLOUDCOVER VISIBLE NONE;CENT_LAT CENT_LAT VISIBLE NONE;CENT_LONG CENT_LONG VISIBLE NONE;BANDS BANDS VISIBLE NONE;COLUMNS COLUMNS VISIBLE NONE;ROWS ROWS VISIBLE NONE;BITS_PIXEL BITS_PIXEL VISIBLE NONE;FILE_FMT FILE_FMT VISIBLE NONE;OFF_NADIR OFF_NADIR VISIBLE NONE;SUN_ELEV SUN_ELEV VISIBLE NONE;EXPOSURE EXPOSURE VISIBLE NONE;SCAN_DIR SCAN_DIR VISIBLE NONE;COLL_GSD COLL_GSD VISIBLE NONE;PROD_GSD PROD_GSD VISIBLE NONE;DET_PITCH DET_PITCH VISIBLE NONE;LINE_RATE LINE_RATE VISIBLE NONE;REF_HEIGHT REF_HEIGHT VISIBLE NONE;ABSCALFACT ABSCALFACT VISIBLE NONE;BANDWIDTH BANDWIDTH VISIBLE NONE;TDI TDI VISIBLE NONE;XTRACKVA XTRACKVA VISIBLE NONE;INTRACKVA INTRACKVA VISIBLE NONE;O_FILENAME O_FILENAME VISIBLE NONE;O_FILEPATH O_FILEPATH VISIBLE NONE;O_DRIVE O_DRIVE VISIBLE NONE;S_FILENAME S_FILENAME VISIBLE NONE;S_FILEPATH S_FILEPATH VISIBLE NONE;PREVIEWJPG PREVIEWJPG VISIBLE NONE;PREVIEWURL PREVIEWURL VISIBLE NONE;ADDED_DATE ADDED_DATE VISIBLE NONE;MOD_DATE MOD_DATE VISIBLE NONE;RCVD_DATE RCVD_DATE VISIBLE NONE;NGA_NAME NGA_NAME VISIBLE NONE;FILE_SZ FILE_SZ VISIBLE NONE;avsunazim avsunazim VISIBLE NONE;avtargetaz avtargetaz VISIBLE NONE;stereopair stereopair VISIBLE NONE;pairname pairname VISIBLE NONE;ACQ_DATE ACQ_DATE VISIBLE NONE;acq_year acq_year VISIBLE NONE;prod_short prod_short VISIBLE NONE;SHAPE_Length SHAPE_Length VISIBLE NONE;SHAPE_Area SHAPE_Area VISIBLE NONE")

    # Select footprints that intersect with AOI
    selection = arcpy.SelectLayerByLocation_management('fprintLayer', "INTERSECT", areaShp, "", "NEW_SELECTION", "NOT_INVERT")

    # Save selection as shapefile
    outSelectShp = os.path.join(ddir, '{}__ngaFootprints.shp'.format(areaName))
    arcpy.CopyFeatures_management(selection, outSelectShp)
    
    return outSelectShp

def projectToUtm(inFc, srObj):

    outProjShp = inFc.replace(".shp", "__UTM.shp")#os.path.join(tempDir, '{}__UTM.shp'.format(areaName))

    print "   Projecting selected to output {} with {} projection\n".format(outProjShp, srObj.name)
    
    # Project to UTM
    arcpy.Project_management(inFc, outProjShp, srObj, "", "", "PRESERVE_SHAPE")#.exportToString().split(';')[0], "PRESERVE_SHAPE")

    return outProjShp

def main(args):
    
    # Unpack args:
    areaShp = args['areaShp']
    footprintFc = args['footprints']
    outputDir = args['outputDir']    
    
    """
    # Input variables (hardcoded):
    areaShp = r'E:\MaggieData\ProposalStuff\Biodiversity_2020\Sites\siteShapefiles\Lambir.shp'
    footprintFc = r'E:\MaggieData\NGA_footprints\nga_inventory_canon.gdb\nga_inventory_canon'
    outputDir = r'E:\MaggieData\ProposalStuff\Biodiversity_2020\DensityMaps\siteFootprints'
    """

    # To create shapefiles with strips for featureCount, read in the text file for the field mapping (may be edited from time to time):
    fieldMapTxt = r'E:\Code\Functions\DataManagement\nga_canon__fieldMap.txt'
    with open(fieldMapTxt, 'r') as t:
        fieldMap = t.read().strip()

    
    # Get area name and set up temp dir
    areaName = os.path.basename(areaShp).replace('.shp', '')
    tempDir = os.path.join(outputDir, 'temp', areaName) 
    
    if not os.path.exists(tempDir):
        os.makedirs(tempDir)

    outputShp = os.path.join(outputDir, '{}__ngaStrips.shp'.format(areaName))
    print "\nCreating site footprints shapefile {} \n".format(outputShp)
    
    # First get the footprints that intersect with the AOI
    selectedShp = selectFootprintsForAOI(areaShp, footprintFc, tempDir)

    # And get UTM zone SR for shapefile
    utmSrObj = findUtmZone(areaShp, tempDir)

    # Project selection to AOI's UTM zone:
    selectedShpProj = projectToUtm(selectedShp, utmSrObj)

    # Add and calculate 2 text fields: dateStr and stripName to projected selection shapefile
    createField(selectedShpProj, "dateStr", "TEXT", "!SCENE_ID!.split('_')[1][0:8]") # To get date column i.e. '20120127'
    createField(selectedShpProj, "stripName", "TEXT", "'{}_{}_{}_{}'.format(!SENSOR!, !dateStr!, !PROD_CODE!, !CATALOG_ID!)") # To get strip ID i.e. 'WV02_20120127_M1BS_020937774213'

    # Dissolve on new stripName column to get strips shp
    createStripsShp(selectedShpProj, outputShp, fieldMap)

    # And finally add "one" column for featureCount
    createField(outputShp, "one", "SHORT", "1")

    print "\nCreated output {}\n".format(outputShp)

    return outputShp

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--areaShp", type=str, required=True, help="Input AOI shp")
    parser.add_argument("-f", "--footprints", type=str, required=True, help="Input footprints shp/gdb")
    parser.add_argument("-o", "--outputDir", type=str, required=True, help="Output dir")

    args = vars(parser.parse_args())

    main()
            
