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
import time

from FeatureClass import FeatureClass

    
def main(args):
    
    # Unpack args
    inputList  = args['inputList']
    outputGDB  = args['outGDB']

    # Start clock
    start = time.time()
    print "BEGIN: {}\n".format(time.strftime("%m-%d-%y %I:%M:%S"))
    
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
    
    elapsedTime = round((time.time()-start)/60, 4)
    print "\nEND: {}\n".format(time.strftime("%m-%d-%y %I:%M:%S"))
    print "Completed in {} minutes".format(elapsedTime)
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("inputList", type=str,
                                help="Text file with list of paths to inputs")    
    parser.add_argument("outGDB", type=str, 
                                help="Path to output GDB")


    args = vars(parser.parse_args())

    main(args)
    