# -*- coding: utf-8 -*-
"""
Stand-alone script to make a VRT from list of strips or directory of .tifs
VRT will be ordered with least cloudy on top

Parts taken from VRT script in EVHR

Tifs in list or directory must have .xml file beside them or they won't be included in output

!!NOTE!!: Right now this code...
            () Converts .vrt to .tif and makes overviews on the .tif, but not on the .vrt
            (x) Leaves the .vrt as is and makes overviews on the .vrt
            () Converts .vrt to .tif and makes overviews for both the .vrt and .tif
            
            Edit comments in bottom of code to change this 

Call: <inputDirOrList> <outputVrtLocation>
"""
import os, sys
import glob
import operator

Input = sys.argv[1]
Output = sys.argv[2]



def getCloudScore(inTif):
    import xml.etree.ElementTree as ET

    inXml = inTif.replace('.tif', '.xml')
    if not os.path.isfile(inXml):
        print "{} does not exist. Please try again".format(inXml)
        return None

    
    try:
        tree = ET.parse(inXml)
        tag = tree.getroot().find('IMD').find('IMAGE')
        cloudScore = float(tag.find('CLOUDCOVER').text)        

    except Exception as e:
        print "Error in getting cloud score. Not using tif {}".format(inTif)
        print " {}".format(e)
        return None
    
    return cloudScore

# Test inputs
if os.path.isdir(Input):
    inTifs = [f for f in glob.glob(os.path.join(Input, '*tif'))]
elif os.path.isfile(Input) and Input.endswith('.txt'):
    with open(Input, 'r') as inf:
       inTifs = [f.strip() for f in inf.readlines() if f.strip().endswith('.tif')]
else: print "Input must be a directory or text file"

if len(inTifs) == 0:
    sys.exit("Input {} had 0 .tifs. Please try again".format(Input))

if not Output.endswith('.vrt'):
    sys.exit("Output file must be a .vrt")
    
# Iterate over list of inputs and build dictionary
ccDict = {}

print "Processing {} inputs".format(len(inTifs))
for tif in inTifs:
    
#    if tif == 'M1BS/2016-2019/WV02_20171206_M1BS_1030010074416B00-toa.tif':
#        import pdb; pdb.set_trace()
    
    cloudScore = getCloudScore(tif)
    if cloudScore == None: # If we could not get score, don't include in output
        print " Not adding {}".format(tif)
        continue
    ccDict[tif] = cloudScore
#    print tif, cloudScore
    sortedTifs = [key for (key, value) in sorted(ccDict.items(), 
                           key=operator.itemgetter(1), reverse=True)]
    
    
#import pdb; pdb.set_trace()
#print sorted(ccDict.items(), key=operator.itemgetter(1))
#print ''
#print ' '.join(sortedTifs)
    
# Create vrt from ordered tifs
print "BUILDING VRT for {} inputs\n".format(len(sortedTifs))
cmd = 'gdalbuildvrt -q -overwrite {} {}'.format(Output,' '.join(sortedTifs))
print " {}".format(cmd)
os.system(cmd)

# Make overviews on output .vrt
print ''
cmd = 'gdaladdo {} 2 4 8 16'.format(Output)
print " {}".format(cmd)
os.system(cmd)

## Convert to .tif
#print ''
#cmd = 'gdal_translate -co COMPRESS=LZW -co BIGTIFF=YES {} {}'.format(Output, Output.replace('.vrt', '.tif'))
#print " {}".format(cmd)
#os.system(cmd)
#
## Make overviews on .tif
#print ''
#cmd = 'gdaladdo -ro --config COMPRESS_OVERVIEW LZW --config BIGTIFF_OVERVIEW YES {} 2 4 8 16'.format(Output.replace('.vrt', '.tif'))
#print " {}".format(cmd)
#os.system(cmd)
