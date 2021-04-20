# Print min/max and values for all .tifs in a directory

import os
import glob


indir = '/att/gpfsfs/briskfs01/ppl/mwooten3/EVHR_API/evhrDevelopment/Output/requests/redo-kassassaTilesMS-fFv8JlhtjYOvWog_dXCLTGWelqf9Cnui5CaZhMjB/5-toas'
gdir = glob.glob(os.path.join(indir, '*tif'))


for tif in gdir:

    print '{}:'.format(os.path.basename(tif))

    cmd = 'gdalinfo {} -mm | grep "Min/Max"'.format(tif)
    os.system(cmd)

    print ''
