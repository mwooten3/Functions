# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 17:17:29 2021
@author: mwooten3

PURPOSE: To clean up after EVHR run

PROCESS: Given an input request name and destination directory:
         - Find all dirs for request, print n strips and prompt user to continue
         - Combine toa .tif and .xml into temp dir, make text list
         - Move content to dest dir (.tif, .xml, .txt file)
         - if .vrt option is indicated, run .vrt process

NOTE That this code will not distinguish between Pan and MS if theyre together in dir
     
 TO DO:
     - make vrt if option selected
     - option to run create/update footprints (need to figure out if update works)
     - use arguments not hardcode
"""

import os, sys
import glob
import argparse


# Static vars:
reqBase = '/adapt/nobackup/people/mwooten3/EVHR_API/evhrDevelopment/Output/requests'

def main(args):
#def main():

    # TEMP hardcode for now
    #reqName = 'Amhara-Pan-3'
    #destDir = '/att/gpfsfs/briskfs01/ppl/mwooten3/Ethiopia_Woubet/VHR/P1BS'
    
    # Unpack arguments   
    reqName  = args['requestName']
    destDir = args['outDir']
    makeVrt = args['vrt']
    
    nDest = len(glob.glob(os.path.join(destDir, '*toa.tif')))
    print("Number of toa.tif files in {} before move: {}\n".format(destDir, nDest))
    
    # First find all toa files from request
    dirs = glob.glob(os.path.join(reqBase, reqName + '*'))
    print("Found {} dirs for request {}:".format(len(dirs), reqName))
    print(dirs)
    print(" ")
    
    srchTif = os.path.join(reqBase, reqName + '*', '5-toas', '*0-toa.tif')
    tifs = glob.glob(srchTif)
    nTifs = len(tifs)
    srchXml = os.path.join(reqBase, reqName + '*', '5-toas', '*0-toa.xml')
    xmls = glob.glob(srchXml)
    nXmls = len(xmls)
    
    if nTifs == 0:
        print("No toa .tif files exist for {}".format(reqName))
        return None
    
    if nTifs != nXmls:
        print("Number of toa .tifs ({}) and .xmls ({}) doesn't match. Exiting".format(nTifs, nXmls))
        return None
        
    # Quick thing to check for duplicates
    uniqueToa = []
    duplicates = []
    for tif in tifs:
        b = os.path.basename(tif)
        if b not in uniqueToa:
            uniqueToa.append(b)
        else:
            duplicates.append(tif)
    print("Duplicates ({}):".format(len(duplicates)))
    for d in duplicates: print(d)
    print("")

    ans = input("Found {} toa .tifs for {}. Continue? yes or no ".format(nTifs, reqName))
    
    if ans == 'yes':
        pass
    elif ans == 'no':
        return None
    else:
        print("{} is not a valid answer. Exiting".format(ans))
        return None
        
    # Create tempdir and move tif/xml
    tmpDir = os.path.join(reqBase, reqName + '__allToa', '5-toas')
    if os.path.exists(tmpDir):
        ans2 = input("Warning! Dir {} already exists. Are you sure you want to continue? ".format(tmpDir))
        if ans2 == 'yes':
            pass
        elif ans2 == 'no':
            return None
        else:
            print("{} is not a valid answer. Exiting".format(ans2))
            return None
    os.system('mkdir -p {}'.format(tmpDir))
    
    print("Moving {} .tif and .xml to {}".format(nTifs, tmpDir))
    os.system('mv {} {}'.format(srchTif, tmpDir))
    os.system('mv {} {}'.format(srchXml, tmpDir))
    
    # cd to new dir and make list
    #os.system('cd {}'.format(tmpDir))
    os.chdir(tmpDir)
    os.system('ls *tif >> {}.txt'.format(reqName))
    
    # Move content to destination dir
    print("Moving toa .tif/.xml files to {}\n".format(destDir))
    
    os.system('mv * {}'.format(destDir)) 
    
    nDestPost = len(glob.glob(os.path.join(destDir, '*toa.tif')))
    print("Number of toa.tif files in {} after move: {}".format(destDir, nDestPost))

    print(" Checks out? [{} + {} = {}] --> {} ".format(nDest, nTifs, nDest+nTifs, nDest+nTifs == nDestPost))


    #* TD: OPTION to make .vrt
    if makeVrt:
        pass # TEMP
    
    # OPT to mak/update footprints ?



if __name__ == "__main__":
    
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-r", "--requestName", required=True, type=str, 
                        help="Name of EVHR request")
    parser.add_argument("-o", "--outDir", required=True, type=str, 
                        help="Destination directory")
    parser.add_argument("-v", "--vrt", required=False, action='store_true',
                        default = False, help="Use flag to create .vrt")
    
    args = vars(parser.parse_args())
    
    main(args)
    
    #main() # TEMP

