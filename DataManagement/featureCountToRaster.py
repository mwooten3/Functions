"""
featureCountToRaster.py

Purpose: Convert a .gdb/.shp to count raster
    i.e. Footprints.gdb to Footprint density map
    ***Shp MUST have a field "one" where every feature = 1. So that sum works***

Process:
    - For each feature:
    -- Convert single feature to feature layer
    -- Convert to temp raster, add path to list
    - Sum rasters tool
    
    - If n features > 1000: run multiple iterations and sum the outputs
    
NOTES!: - This will count scenes within a strip that overlap one another twice.
          In order to count by strip, the input .shp should have those features
          merged into one before running through script
           Example: 
               1. Create dateStr field = !SCENE_ID!.split('_')[1][0:8]
               2. Create a stripName (sensor_dateStr_spectype_catID) field =
                   '{}_{}_{}_{}'.format( !SENSOR!, !dateStr!, !PROD_CODE!, !CATALOG_ID!)
               3. Dissolve based on stripName
           DO THIS BEFORE adding "one" column
        - ALSO: .shp projection unit must match outRes unit i.e. UTM for res in meters
        - AND:  .shp MUST have an int column "one" where every row = 1
    
Optional (later):
    An optional dictionary argument with fieldname:argument to use in where clause
    
5/20: Adding block to provide option for command line inputs

"""
# TO DO: 
## test with > 1000 features


import os, sys
import shutil
import math
import arcpy
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

# Apply search terms to shapefile --> feature layer
# Does not support float values
def applySearchTerms(shp, searchTerms):
    
    whereClause = ''
    for st in searchTerms:
        
        # Check to see if term value (3rd part) is an integer
        try:
            int(st.split(':')[2]) # If successful, addWhere with no ' '
            addWhere =  '("{}"{}{}) AND'.format(*st.split(':')) 
        except ValueError: # Not a number. Add with ' ' around
            addWhere =  '("{}"{}\'{}\') AND'.format(*st.split(':'))

        whereClause += addWhere
        
    whereClause = whereClause.strip(' AND')

    inFeatLayer = arcpy.MakeFeatureLayer_management(shp, "features", whereClause)    
    
    return inFeatLayer
    
# This function takes a featureLayer with everything we want to sum and 
# returns a raster. Input should have where clause already applied
def featuresToRaster(featureLayer, tempdir, outRes, outSumRaster):
  
    rastersList = [] # To store the one-feature rasters
    
    features = arcpy.SearchCursor(featureLayer)
    for feat in features:
        fid = feat.getValue("FID")
        outRast = os.path.join(tempdir, '{}.tif'.format(fid))
        
        # Isolate feature and save as feature layer --> raster
        arcpy.SelectLayerByAttribute_management(featureLayer, "NEW_SELECTION", '"FID"={}'.format(fid))                    
        arcpy.FeatureToRaster_conversion(featureLayer, "one", outRast, outRes)
#        # temporarily convert FL to shp to check:
        #arcpy.CopyFeatures_management(featureLayer, outRast.replace('tif', 'shp'))
        rastersList.append(outRast)      

    # Sum all the features
    sumRasters(rastersList, outSumRaster)
    
    return outSumRaster 
    
# In some cases we need a list of unique FIDs (in order) from a feature layer
def getUniqueFIDs(featureLayer):
    
    uniqueFIDs = []
    features = arcpy.SearchCursor(featureLayer)
    for feat in features:
        uniqueFIDs.append(feat.getValue("FID"))
        
    return sorted(uniqueFIDs)
        
# Use Arc's sum raster tool to sum rasters
def sumRasters(rastersList, outSumRaster):
    
    arcpy.gp.CellStatistics_sa(";".join(rastersList), outSumRaster, "SUM", "DATA")

    return outSumRaster


# UNCOMMENT THIS BLOCK TO USE HARDCODED INPUTS
"""
#####################################################
# Process here - VARIABLES:
outname = 'WV-2017to2020_Senegal-AOI2' # for example

inputShp = 'E:\MaggieData\ProposalStuff\Senegal_LCLUC\Shapefiles\Footprints\WV_strips__SenegalAOI2__UTM.shp'
outdir =   'E:\\MaggieData\\ProposalStuff\\Senegal_LCLUC\\densityRasters'
tempdir = os.path.join(outdir, 'temp')

outRes = 50 # in m

"""
#searchTerms examples:
#   None - no filters, Denity of all features in input shp
#  ['STEREOPAIR:<>:NONE'] # stereo pair not None (if we want stereo)
#  ['FIRST_PROD:=:P1BS', 'FIRST_ster:<>: '] # P1BS, stereo yes # or maybe 'FIRST_ster:<>:NONE'
#  ['FIRST_ac_1:>=:2005', 'FIRST_ac_1:<=:2010', 'FIRST_PROD:=:P1BS', 'FIRST_seas:=:dry']
"""
searchTerms = ['FIRST_acq1:>=:2017']#, 'FIRST_acq1:<=:2016']
#####################################################
"""

# UNCOMMENT THIS BLOCK TO USE COMMAND LINE INPUTS
"""
#####################################################
outname = #'WV-2017to2020_Senegal-AOI2' # for example

inputShp = 'E:\MaggieData\ProposalStuff\Senegal_LCLUC\Shapefiles\Footprints\WV_strips__SenegalAOI2__UTM.shp'
outdir =   'E:\\MaggieData\\ProposalStuff\\Senegal_LCLUC\\densityRasters'
tempdir = os.path.join(outdir, 'temp')

outRes = 50 # in m

"""
#searchTerms examples:
#   None - no filters, Denity of all features in input shp
#  ['STEREOPAIR:<>:NONE'] # stereo pair not None (if we want stereo)
#  ['FIRST_PROD:=:P1BS', 'FIRST_ster:<>: '] # P1BS, stereo yes # or maybe 'FIRST_ster:<>:NONE'
#  ['FIRST_ac_1:>=:2005', 'FIRST_ac_1:<=:2010', 'FIRST_PROD:=:P1BS', 'FIRST_seas:=:dry']
"""
searchTerms = ['FIRST_acq1:>=:2017']#, 'FIRST_acq1:<=:2016']
#####################################################
"""

outSumRaster = os.path.join(outdir, '{}__count.tif'.format(outname))
print "Creating {}...\n".format(outSumRaster)

print "Input footprints shp: {}".format(inputShp)
if searchTerms: print " Filters: {}".format(searchTerms)

maxFeatures = 1000 # there is a 1000 raster limit for sumRasters. must split into iters based off that

for d in [outdir, tempdir]:
    if not os.path.isdir(d): os.mkdir(d)

# Get the input feature layer: Apply search terms to input shp/gdb if specified
if searchTerms:
    inFeatLayer = applySearchTerms(inputShp, searchTerms)
else:
    inFeatLayer = arcpy.MakeFeatureLayer_management(inputShp, "features")

nFeatures = int(arcpy.GetCount_management(inFeatLayer).getOutput(0))
if nFeatures == 0:
    print '\nThere were 0 features for this input shp/filter combination'
    sys.exit()
print "\n Number of features: {}".format(nFeatures)
    
if nFeatures > maxFeatures:
   
    # For each iteration, featuresToRaster, then sum outputs from FTR
    FIDs = getUniqueFIDs(inFeatLayer) # get FIDs from feature layer. len should = nFeatures
    if len(FIDs) != nFeatures: 
        print "Number of unique FIDs do not match number of features in layer. Please try again"
        sys.exit()
        
    nIterations = int(math.ceil(nFeatures/float(maxFeatures)))
    print " Number of iterations: {}\n".format(nIterations)
   
    a = 0 # initial bounds = (0, maxFeatures)
    b = maxFeatures
    iterationRasters = [] # list to store the output sum rasters from each iteration
    for i in range(0, nIterations):
        
        print "  iteration {}...".format(i+1)

        if i == (nIterations-1):
            b = nFeatures # if we are in the last iteration, b = end of list

        # Get feature layer for iteration subset - Apply FID bounds to get feature layer
        whereClause = '("FID" >= {}) AND ("FID" <= {})'.format(FIDs[a], FIDs[b-1])
        print "   where clause: {}".format(whereClause)
        iterFeatLayer = arcpy.MakeFeatureLayer_management(inFeatLayer, "features", whereClause)
        
        # Get the count/sum raster for the iteration subset
        outIterSumRaster = os.path.join(tempdir, '{}-i{}.tif'.format(outname, i))
        featuresToRaster(iterFeatLayer, tempdir, outRes, outIterSumRaster)
        iterationRasters.append(outIterSumRaster)

        # get the new bounds for the next iteration by adding maxFeatures 
        a += maxFeatures
        b += maxFeatures       
    
    # Lastly, sum all iteration rasters to final output
    sumRasters(iterationRasters, outSumRaster) # Sum all the iterations
    
else: # If we are under 1000 features, just run usual
    featuresToRaster(inFeatLayer, tempdir, outRes, outSumRaster)

# Clean up:
shutil.rmtree(tempdir)    
arcpy.CheckInExtension("Spatial")






