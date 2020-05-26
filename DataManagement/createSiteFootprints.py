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
  
"""

import arcpy
import os, sys


# Input variables (hardcoded):
areaShp = 'E:\MaggieData\ProposalStuff\Biodiversity_2020\Sites\siteShapefiles\MichiganBigWoods.shp'
footprintsShp = 'E:\MaggieData\NGA_footprints\nga_inventory_canon.gdb\nga_inventory_canon'
outputDir = 'E:\MaggieData\ProposalStuff\Biodiversity_2020\createDensityMaps'

"""
# Input variables (as CL inputs):
areaShp = sys.argv[1]
footprintsShp = sys.argv[2]
outputDir = sys.argv[3]
"""

# Set up temp dir
areaName = os.path.basename(areaShp).replace('.shp', '')
tempDir = os.path.join(outputDir, 'temp', areaName)


def findUtmZone(inShp):
    
    UTM = 'E:\MaggieData\General Reference Data\UTM_Zone_Boundaries\UTM_Zone_Boundaries.shp'
    
    # Clip input with UTM
    outUtmClip = os.path.join(tempDir, '{}__clippedUTM.shp'.format(areaName))
    arcpy.Clip_analysis(UTM, areaName, outUtmClip, "")
