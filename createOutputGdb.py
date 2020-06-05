# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 15:44:57 2020; @author: mwooten3

Purpose:
    Add a list of feature classes to one big feature class (most often GDB)

Inputs: 
    Path to list with input feature classes
    Output GDB name/location
    
Process:
    For each shapefile, add to output GDB
    
"""

#import os
#import glob
import argparse

from FeatureClass import FeatureClass

# Set up directories - these are kinda hardcoded according to current set-up in other code
#inDir = '/att/gpfsfs/briskfs01/ppl/mwooten3/3DSI/ZonalStats/_zonalStatsGdb'
#outDir = '/att/gpfsfs/briskfs01/ppl/mwooten3/3DSI/ZonalStats'
    
def main(args):
    
    # Unpack args
    inputList  = args['inputList']
    outputGDB  = args['outGDB']

    # Read input list into list. Assume all inputs exist. 
    # If they do not, FC should throw RuntimeError
    # Can add skip later if we want to avoid error due to shp not existing
    with open (inputList, 'r') as l:
        inFcs = [x.strip('\r\n') for x in l.readlines()]

    print "Adding {} feature classes to {}\n".format(len(inFcs), outputGDB)
        
    for inFc in inFcs:
        
        #zs.updateOutputGdb(outGdb, f)
        fc = FeatureClass(inFc)
        fc.addToFeatureClass(outputGDB)

    """
    bname = '{}__{}__ZonalStats'.format(zonalType, stackType)    
    outGdb = os.path.join(outDir, '{}.gdb'.format(bname))
    
    globDir = glob.glob(os.path.join(inDir, '{}*gpkg'.format(bname)))
    print "\nCreating {} from {} input files...\n".format(outGdb, len(globDir))
    import pdb; pdb.set_trace()
    for f in globDir:
        print f
        zs.updateOutputGdb(outGdb, f)
        
        
#    # Lastly, move the csv to its final directory
#    mvCsv = os.path.join(inDir, '{}.csv'.format(bname))
#    os.system('mv {} {}'.format(mvCsv, outDir))
    """
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("inputList", type=str,
                                help="Text file with list of paths to inputs")    
    parser.add_argument("outGDB", type=str, 
                                help="Path to output GDB")


    args = vars(parser.parse_args())

    main(args)
    