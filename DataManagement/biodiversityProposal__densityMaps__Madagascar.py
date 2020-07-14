# -*- coding: utf-8 -*-
"""
Created on Tue May 26 10:07:28 2020
@author: mwooten3

Purpose:
  To take sites shp for Biodiversity Madagascar proposal and make density maps
   for each site (M1BS, P1BS, Stereo, maybe SWIR?)
   
Inputs (hard-coded as this is specific to one task):
  Sites shp, nga shp, outputdir
  
Output:
  Density maps, 1 for WV MS, the other for WV Stereo
  
Process:
  Iterate through sites shapefiles:
    They are already exported into buffered shapefiles 
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
doDG = True # Run DG footprints in stead of nga_canon/inventory

ddir            = r'E:\MaggieData\ProposalStuff\Biodiversity_Madagascar'
#sitesGdb        = os.path.join(ddir, 'Sites', 'Sites.gdb')
#polygonSites    = os.path.join(sitesGdb, 'Sites_Buffer')
sitesDir        = os.path.join(ddir, 'Parks')
footprintsFc    = r'E:\MaggieData\NGA_footprints\nga_inventory_canon.gdb\nga_inventory_canon' # initial footprints

siteFprintDir   = os.path.join(ddir, 'siteFootprints') # where site strip footprint shps will go, to send to CSF.py
mapOutDir       = os.path.join(ddir, 'Density') # Final outputdir for maps, to send to feature count

# To record the number of features for each site/search combo:
recordCsv = r'E:\MaggieData\ProposalStuff\Biodiversity_Madagascar\nResults_inHouse.csv'



# Dictionary for output name and search string list:
#searchOptions = {'WV-M1BS': ['LAST_PROD_:=:M1BS', 'LAST_SENSO: LIKE :WV%'],
#                 'WV-Stereo': ['LAST_stere:<>: ']} # for nga_canon
searchOptions = {'WV-M1BS': ['LAST_PROD_:=:M1BS', 'LAST_SENSO: LIKE :WV%'],
                 'WV-Stereo': ['LAST_stere:<>: '],
                 'WV-P1BS': ['LAST_PROD_:=:P1BS', 'LAST_SENSO: LIKE :WV%']}
        
# Get vars if running DG:
if doDG:
    footprintsFc  = r'E:\MaggieData\NGA_footprints\DG_footprints__to2018.gdb\DG_footprints'
    siteFprintDir = os.path.join(siteFprintDir, 'DG')
    mapOutDir     = os.path.join(mapOutDir, 'DG')
    recordCsv     = recordCsv.replace('_inHouse.csv', '_DG.csv')
    
    # *NOTE, i made PAN, MS1, MS2 and MS columns on .gdb by hand
    # see biodiversity proposal notes and consider implementing in CSF instead if runDG is True
    searchOptions = {'WV-M1BS': ["MS:=:yes"],
                 'WV-Stereo': ["STEREOPAIR:<>:NONE"],
                 'WV-P1BS': ["PAN:=:yes"]} # for DG footprints

if not os.path.isfile(recordCsv):
    with open(recordCsv, 'w') as rc:
        rc.write('Site,FilterName,nFeat\n')
        
# Create directories
for d in [siteFprintDir, mapOutDir]:
    if not os.path.exists(d): os.makedirs(d)

# Hardcoded for Madagascar proposal:
parks = ['MasoalaNP_Buffer.shp',
         'RanomafanaNP_Buffer.shp',
         'SambavaNP_Buffer.shp',
         'Taolagnaro_Buffer.shp',
         'ZahamenaNP_buffer.shp']

# Iterate through sites
for park in parks:
    
    siteName = park.strip('_buffer.shp').strip('_Buffer.shp')
    
    print "\n\n==========================================================="
    print "PROCESSING {}\n".format(siteName)
    
    srch = "SITENAME = '{}'".format(siteName)
    lyr = '{}-lyr'.format(siteName)
    
    sitePolyFc = os.path.join(sitesDir, park) # i.e site shp
 
    # Call create footprints
    #   Create an arg dict to mimic argparse and send to main because nothing else is working
    argDict1 = {'areaShp': sitePolyFc,
               'footprints': footprintsFc,
               'outputDir': siteFprintDir,
               'doDG': doDG}
    #import pdb; pdb.set_trace()    
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
                  
    
