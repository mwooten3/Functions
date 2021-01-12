# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 14:29:37 2020
@author: mwooten3

To create the footprint maps for CSS proposal in two steps:
  A) createSiteFootprints.py and B) featureCountToRaster.py
    
"""
import arcpy
import os

import createSiteFootprints
import featureCountToRaster

#arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True



####################################################################
## INPUT ARGUMENTS THAT STAY THE SAME:
ddir = r'E:\MaggieData\ProposalStuff\CCS_2020'

aoiShp = os.path.join(ddir, 'Shapefiles', 'east_coast_w_50km_buffer.shp')#, 'Coastal_SE_US.shp')
siteName = 'Coastal-SE-US'

# ***NGA footprints. doDG = True will override this with MAXAR footprints***
footprintsFc    = r'E:\MaggieData\NGA_footprints\nga_inventory_canon.gdb\nga_inventory_canon'

footprintsOutDir = os.path.join(ddir, 'Shapefiles', 'Footprints') # Output footprint subsets for different combos
mapOutDir = os.path.join(ddir, 'DensityMaps') # Final outputdir for maps, arg for FCTR

doDG = False # Unless explicitly set to True


## INPUT ARGUMENTS FOR THE DIFFERENT OUTPUTS:

# 1. On NGA footprints:
    # Map types: All Stereo, Leaf-Off Stereo, Leaf-On Stereo

"""
searchOptions = {'wvStereoLeafOn': ['LAST_pairn:<>: ',  'LAST_SENSO: LIKE :WV%', 'LAST_month:In:(4, 5, 6, 7, 8, 9, 10)'],
                 'wvStereoLeafOff': ['LAST_pairn:<>: ',  'LAST_SENSO: LIKE :WV%', 'LAST_month:In:(11, 12, 1, 2, 3)'],
                 'wvStereoAll': ['LAST_pairn:<>: ',  'LAST_SENSO: LIKE :WV%']
                 }
"""

# 2. On MAXAR footprints:
    # Map types: All stereo, Leaf-Off Stereo, Leaf-On Stereo
#"""
doDG = True # Run DG footprints in stead of nga_canon/inventory
searchOptions = {'wvStereoAll_DG': ["STEREOPAIR:<>:NONE", "PLATFORM: LIKE :WV%"]}
# After fields added, apply month filters for leaf on leaf off
#"""


####################################################################

# If using DG/MAXAR footprints 
if doDG:
    #* CHECK FC
    footprintsFc     = r'E:\MaggieData\NGA_footprints\DG_footprints__toNov2020.gdb\DG_footprints__toNov2020'
    footprintsOutDir = os.path.join(footprintsOutDir, 'DG')
    mapOutDir        = os.path.join(mapOutDir, 'DG')   


# Create directories
for d in [footprintsOutDir, mapOutDir]:
    if not os.path.exists(d): os.makedirs(d)

# Call create footprints ONLY IF output shapefile does not exist
# Create an arg dict to mimic argparse and send to main because nothing else is working
argDict1 = {'areaShp': aoiShp,
            'footprints': footprintsFc,
            'outputDir': footprintsOutDir,
            'doDG': doDG}

footprintsName = os.path.basename(aoiShp).replace('.shp', '__ngaStrips.shp') # From CSF code
footprintsOutShp = os.path.join(footprintsOutDir, footprintsName)

#print footprintsOutShp
#print argDict1

if not os.path.isfile(footprintsOutShp):   
    footprintsOutShp = createSiteFootprints.main(argDict1)
else:
    print "\nNot running CSF. Output {} exists".format(footprintsOutShp)
    

# Call FCTR.py
arcpy.CheckOutExtension("Spatial")

# For each map type (i.e. could be WV-Stereo, could be Leaf-Off, whatever you 
# want to define your search terms as), filter and get map. Could just be list of one

for nameBase, searchTerms in searchOptions.items():

    mapOutName = '{}_{}'.format(siteName, nameBase)
  
    # Create another argdict for FCTR.py:
    argDict2 = {'inputStrips': footprintsOutShp,
                'searchTerms': searchTerms,
                'outputName': mapOutName,
                'outputDir': mapOutDir,
                'outputRes': 150}
        
    nFeat = featureCountToRaster.main(argDict2)
    
    print "  N features = {}".format(nFeat)

    arcpy.CheckInExtension("Spatial")
