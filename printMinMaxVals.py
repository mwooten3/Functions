# Print min/max and values for all .tifs in a directory

import os
import sys
import glob


indir = sys.argv[1]
gdir = glob.glob(os.path.join(indir, '*tif'))


for tif in gdir:

    print '{}:'.format(os.path.basename(tif))

    cmd = 'gdalinfo {} -mm | grep "Min/Max"'.format(tif)
    os.system(cmd)

    print ''
