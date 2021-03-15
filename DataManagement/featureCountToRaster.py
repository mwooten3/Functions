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
           DO THIS BEFORE adding "one" and "uId" columns
        - ALSO: .shp projection unit must match outRes unit i.e. UTM for res in meters
        - AND:  .shp MUST have an int column "one" where every row = 1 AND a "uId" column where uId = FID (or FID+1)
    
Optional (later):
    An optional dictionary argument with fieldname:argument to use in where clause
    
5/20: Adding block to provide option for command line inputs
        Order of inputs for CL: siteFootprintsShp searchTerms outputName outputDir

6/2/2020: Moving input arguments to argparse. Can still hardcode parts after unpacking if necessary

11/23/2020: Changing FID usage to our new uId 
"""



import os#, sys
import shutil
import math
import arcpy
import argparse

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
#from arcpy import sa

# because arc is being fucking stupid
iterFeatLayer = None
inFeatLayer = None

# Apply search terms to shapefile --> feature layer
# Does not support float values
def applySearchTerms(shp, searchTerms):
    #import pdb;pdb.set_trace()

    whereClause = ''
    for st in searchTerms:
        
        # Check to see if term value (3rd part) is an integer
        try:
            int(st.split(':')[2]) # If successful, addWhere with no ' '
            addWhere =  '("{}"{}{}) AND '.format(*st.split(':')) 
        except ValueError: # Not a number. Add with ' ' around
            
            # First, check if it is a list (in Arc, we do "'columnX' In (1, 2, 3)" ,
            # if we wanna select all items in columnX that are in a list (represented as a tuple here))
            # This only works for multiple items in list/tuple
            if "(" and ")" in st.split(':')[2]:
                addWhere = '("{}" {} {}) AND '.format(*st.split(':'))
            else: # Assume the search value is a string
                addWhere =  '("{}"{}\'{}\') AND '.format(*st.split(':'))

        whereClause += addWhere
        
    whereClause = whereClause.strip(' AND ')

    
    inFeatLayer = arcpy.MakeFeatureLayer_management(shp, "features", whereClause)
    
    return inFeatLayer
    
# This function takes a featureLayer with everything we want to sum and 
# returns a raster. Input should have where clause already applied
def featuresToRaster(featureLayer, tempdir, outRes, outSumRaster):
  
    rastersList = [] # To store the one-feature rasters
    
    features = arcpy.SearchCursor(featureLayer)
    for feat in features:
        fid = feat.getValue("uId")
        outRast = os.path.join(tempdir, '{}.tif'.format(fid))
        
        # Isolate feature and save as feature layer --> raster
        arcpy.SelectLayerByAttribute_management(featureLayer, "NEW_SELECTION", '"uId"={}'.format(fid))                    
        arcpy.FeatureToRaster_conversion(featureLayer, "one", outRast, outRes)
#        # temporarily convert FL to shp to check:
        #arcpy.CopyFeatures_management(featureLayer, outRast.replace('tif', 'shp'))
        rastersList.append(outRast)      

    # Sum all the features
    arcpy.CheckOutExtension("Spatial")
    sumRasters(rastersList, outSumRaster)
    
    return outSumRaster 
    
# In some cases we need a list of unique FIDs (in order) from a feature layer
# 11/23 uId now
def getUniqueFIDs(featureLayer):
    
    uniqueFIDs = []
    features = arcpy.SearchCursor(featureLayer)
    for feat in features:
        uniqueFIDs.append(feat.getValue("uId"))
        
    return sorted(uniqueFIDs)
        
# Use Arc's sum raster tool to sum rasters
def sumRasters(rastersList, outSumRaster):

    arcpy.gp.CellStatistics_sa(";".join(rastersList), outSumRaster, "SUM", "DATA")
    #sa.CellStatistics(";".join(rastersList), outSumRaster, "SUM", "DATA")
    return outSumRaster


def main(args):
    
    # Unpack args
    inputShp    = args['inputStrips']
    searchTerms = args['searchTerms'] 
    outname     = args['outputName']
    outdir      = args['outputDir']
    outRes      = args['outputRes']

    tempdir = os.path.join(outdir, 'temp', outname)
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)
        
    # Sometimes, if running stand-alone from CL or another .py, we need to
    #  convert searchTerms from a string (i.e. "[FIRST_SENS:=:WV01]") to an actual list
    if isinstance(searchTerms, basestring):
        import ast
        searchTerms = ast.literal_eval(searchTerms)        
        
    """    
    #####################################################
    # If you want to hard-code arguments, do it here:
    outname = 'del' # for example
    
    inputShp = 'E:\MaggieData\Vietnam_LCLUC\Density\Vietnam_DongThap_AnGiang__ngaStrips.shp'
    outdir =   'E:\MaggieData\Vietnam_LCLUC\Density'
    tempdir = os.path.join(outdir, 'temp')
    
    outRes = 20 # in m
    
    #searchTerms examples:
    #   None - no filters, Denity of all features in input shp
    #  ['STEREOPAIR:<>:NONE'] # stereo pair not None (if we want stereo)
    #  ['FIRST_PROD:=:P1BS', 'FIRST_ster:<>: '] # P1BS, stereo yes # or maybe 'FIRST_ster:<>:NONE'
    #  ['FIRST_ac_1:>=:2005', 'FIRST_ac_1:<=:2010', 'FIRST_PROD:=:P1BS', 'FIRST_seas:=:dry']
    
    searchTerms = ['LAST_SENSO: LIKE :WV%']#, 'FIRST_acq1:<=:2016']
    #####################################################    
    """
    
    outSumRaster = os.path.join(outdir, '{}__count.tif'.format(outname))
    print "Creating {}...\n".format(outSumRaster)
    
    print "Input footprints shp: {}".format(inputShp)
    print "Output name: {}".format(outname)
    if searchTerms: print " Filters: {}".format(searchTerms)
    
    maxFeatures = 1000 # there is a 1000 raster limit for sumRasters. must split into iters based off that
    
    for d in [outdir, tempdir]:
        if not os.path.isdir(d): os.mkdir(d)

    # Get the input feature layer: Apply search terms to input shp/gdb if specified
    if searchTerms:
        inFeatLayer = applySearchTerms(inputShp, searchTerms)
    else:
        inFeatLayer = arcpy.MakeFeatureLayer_management(inputShp, "features")
    #import pdb;pdb.set_trace()
    nFeatures = int(arcpy.GetCount_management(inFeatLayer).getOutput(0))
    if nFeatures == 0:
        print '\nThere were 0 features for this input shp/filter combination'
        return 0
        #sys.exit()
    print "\n Number of features: {}".format(nFeatures)
        
    if nFeatures > maxFeatures:
       
        # For each iteration, featuresToRaster, then sum outputs from FTR
        # These are actually from uId column now
        FIDs = getUniqueFIDs(inFeatLayer) # get FIDs from feature layer. len should = nFeatures
        if len(FIDs) != nFeatures: 
            print "Number of unique uIds do not match number of features in layer. Please try again"
            return None
            #sys.exit()
            
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
            whereClause = '("uId" >= {}) AND ("uId" <= {})'.format(FIDs[a], FIDs[b-1])
            print "   where clause: {}".format(whereClause)
            iterFeatLayer = arcpy.MakeFeatureLayer_management(inFeatLayer, "features{}".format(i+1), whereClause)
            
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
    
    return nFeatures

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--inputStrips", type=str, required=True, help="Input shp with footprint strips")
    parser.add_argument("-st", "--searchTerms", type=str, required=False, help="List of search terms")
    parser.add_argument("-o", "--outputName", type=str, required=True, help="Output name for density maps")
    parser.add_argument("-od", "--outputDir", type=str, required=True, help="Output dir for density maps")
    parser.add_argument("-r", "--outputRes", type=int, required=False, help="Output resolution (default = 50m)", default=50)

    
    args = vars(parser.parse_args())

    main(args)




