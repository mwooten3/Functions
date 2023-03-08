# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 12:07:53 2021
@author: mwooten3

Create overviews for .tif files in a given directory or text file
"""

import os
import glob
import argparse

def main(args):
    
    # Unpack arguments   
    inDir  = args['directory']
    
    # Check input
    if not os.path.isdir(inDir) and (not os.path.exists(inDir) or not inDir.endswith('.txt')):
        raise RuntimeError("Input {} is not a directory, text file, or does not exist".format(inDir))
    
    # Get list of input .tif files
    if os.path.isdir(inDir):
        inTifs = glob.glob(os.path.join(inDir, '*tif'))
    else:
        with open(inDir, 'r') as it:
            inTifs = [f.strip() for f in it.readlines()]

    nTifs  = len(inTifs)
    
    if nTifs == 0:
        print("0 .tif files exist in/from {}".format(inDir))
        return None
    else:
        print("Adding overviews for {} .tifs...\n".format(nTifs))
        
    for tif in inTifs:
        
        # Check existence (only works for external overviews):
        ovr = '{}.ovr'.format(tif)
        if not os.path.exists(ovr):
            # Create overview:
            cmd = 'gdaladdo -ro --config COMPRESS_OVERVIEW LZW --config BIGTIFF_OVERVIEW YES {} 2 4 8 16 32 64'.format(tif)
            #print cmd
            os.system(cmd)
        else:
            print('{} exists'.format(ovr))
        
    return None

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=str, 
                        help="Directory with .tifs to create overviews for")
    
    # Maybe add other options later such as: 
    #   search term (ie if we only want to run inDir/*searchTerm*tif instead of inDir/*tif)
    #   internal ovr (external is default)
    #   different pyramids (default 2 4 8 16)
    #   quiet (suppress output, default is False)
    #   different resampling method

    
    args = vars(parser.parse_args())

    main(args)
