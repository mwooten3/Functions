# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 14:50:10 2019

@author: mwooten3

Pansharpen VHR MS data to even high resolution Pan data

Requirements: 
    Pan and MS data should be in same/similar location ie:
      Pan dir/files must be accessible via replacing M1BS with P1BS
    Every MS strip should have corresponding Pan strip

    MS filename must match *M1BS*toa.tif search key
    
Process:
    For each MS file in list/directory:
        Get corresponding Pan file
        Pan-sharpen
        Copy and rename the associated xml as well
"""
import os, sys
import glob


# Get input MS dir:
msDir = sys.argv[1]
#msDir = '/att/gpfsfs/briskfs01/ppl/mwooten3/MCC/VHR/Di/M1BS' # test

outDir = os.path.join(msDir, 'pansharpen')
os.system('mkdir -p {}'.format(outDir))


# Iterate through MS data and pan-sharpen:
for msTif in glob.glob(os.path.join(msDir, '*M1BS*toa.tif')):
#    print msTif    
    bname = os.path.basename(msTif)
    
    panTif = msTif.replace('M1BS', 'P1BS')
#    print panTif
#    sys.exit()
    if not os.path.isfile(panTif):
        print "Pan file ({}) for MS file ({}) does not exist\n".format(panTif, msTif)
        continue
    
    print "Pansharpening {} with {}...".format(bname, panTif)
    
    psTif = os.path.join(outDir, bname.replace('.tif', '_pansharpen.tif'))
    
    # for now, hardcode nodata value of -9999
    cmd = 'gdal_pansharpen.py {} {} {} -nodata -9999 -co COMPRESS=LZW -co BIGTIFF=YES'.format(panTif, msTif, psTif)
    print cmd
    os.system(cmd)
    
    # copy and rename the .xml as well 
    msXml = msTif.replace('.tif', '.xml')
    psXml = psTif.replace('.tif', '.xml')
    if os.path.isfile(msXml):
        os.system('cp {} {}'.format(msXml, psXml))
        
    print ''
