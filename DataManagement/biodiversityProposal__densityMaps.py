# -*- coding: utf-8 -*-
"""
Created on Tue May 26 10:07:28 2020
@author: mwooten3

Purpose:
  To take sites shp for Biodiversity 2020 proposal and make density maps
   for each site (M1BS and Stereo)
   
Inputs (hard-coded as this is specific to one task):
  Sites shp, nga shp, outputdir
  
Output:
  Density maps, 1 for WV MS, the other for WV Stereo
  
Process:
  Iterate through sites shapefile (buffered sites or polygon site outlines):
    Export site to temp Shp and call createSiteFootprints
    For each output type (M1BS and Stereo):
      Set: search terms (based on fields in output); output name; output tif
      Call featureCountToRaster.py with siteFootprints.shp
      
      siteStripsShp = createSiteFootprints.py sitePolyFc footprintsFc siteFprintDir
      featureCountToRaster.py siteStripsShp searchTerms mapOutName mapOutDir
      
      
# 6/3: Added an option to process for DG footprints:

        if this var is True:
            Search terms will be different 
            Output dir/names will be different
            Passed along to createSiteFootprints
"""

import arcpy
import os

import createSiteFootprints
import featureCountToRaster

#arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# Hardcoded inputs (for now)
ddir            = r'E:\MaggieData\ProposalStuff\Biodiversity_2020'
sitesGdb        = os.path.join(ddir, 'Sites\Sites.gdb')
polygonSites    = os.path.join(sitesGdb, 'Sites_Buffer')
footprintsFc    = r'E:\MaggieData\NGA_footprints\nga_inventory_canon.gdb\nga_inventory_canon'
siteFprintDir   = os.path.join(ddir, 'Sites\siteFootprints') # where site strip footprint shps will go, to send to CSF.py

mapOutDir       = os.path.join(ddir, 'DensityMaps') # Final outputdir for maps, to send to feature count

# Dictionary for output name and search string list:
#searchOptions = {'WV-M1BS': ['LAST_PROD_:=:M1BS', 'LAST_SENSO: LIKE :WV%'],
#                 'WV-Stereo': ['LAST_stere:<>: ']} # for nga_canon
searchOptions = {'WV-M1BS': ['LAST_PROD_:=:M1BS', 'LAST_SENSO: LIKE :WV%'],
                 'WV-Stereo': ['LAST_stere:<>: ']} # for DG footprints

# MAYBE WE WANT TO USE THE DG STRIPS LIBRARY INSTEAD OF NGA_CANON:
# 

# To record the number of features for each site/search combo:
recordCsv = r'E:\MaggieData\ProposalStuff\Biodiversity_2020\nResults.csv'
if not os.path.isfile(recordCsv):
    with open(recordCsv, 'w') as rc:
        rc.write('Site,FilterName,nFeat\n')

# Iterate through sites
features = arcpy.SearchCursor(polygonSites)
for feat in features:
    
    siteName = feat.getValue("SITENAME").strip()
    
    print "\n\n==========================================================="
    print "PROCESSING {}\n".format(siteName)
    
    srch = "SITENAME = '{}'".format(siteName)
    lyr = '{}-lyr'.format(siteName)
    
    sitePolyFc = os.path.join(sitesGdb, siteName) # i.e Sites.gdb/SERC
    
    # Select by attribute and save to sitePolyFc
    arcpy.MakeFeatureLayer_management(polygonSites, lyr, where_clause = srch)
    arcpy.CopyFeatures_management(lyr, sitePolyFc)
 
    # Call create footprints
    #   Create an arg dict to mimic argparse and send to main because nothing else is working
    argDict1 = {'areaShp': sitePolyFc,
               'footprints': footprintsFc,
               'outputDir': siteFprintDir}
    
    siteStripsShp = createSiteFootprints.main(argDict1)
    
   
    # for each map type, call FCTR.py
    for nameBase, searchTerms in searchOptions.items():
        
        arcpy.CheckOutExtension("Spatial")
        
        mapOutName = '{}_{}'.format(siteName, nameBase)
        
        print "\n{}...\n".format(mapOutName)
  
        # Create another argdict for FCTR.py:
        argDict2 = {'inputStrips': siteStripsShp,
                    'searchTerms': searchTerms,
                    'outputName': mapOutName,
                    'outputDir': mapOutDir,
                    'outputRes': 10}
        
        nFeat = featureCountToRaster.main(argDict2)

        arcpy.CheckInExtension("Spatial")
        
        # record the number of features that were found for filter
        with open(recordCsv, 'a') as rc:
            rc.write('{},{},{}\n'.format(siteName, nameBase, nFeat))
                  
    
