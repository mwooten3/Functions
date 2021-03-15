# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 13:37:14 2021
@author: mwooten3

Given a list of feature IDs, delete them from a .gdb
"""

from osgeo import ogr#, gdal


# INPUTS:
inFC = "/att/gpfsfs/briskfs01/ppl/mwooten3/3DSI/ATL08/eu/ATL08_eu_v3__crane101.gdb"#'/att/gpfsfs/briskfs01/ppl/mwooten3/3DSI/ATL08/eu/ATL08_eu_v003.gdb'

# THIS LIST MUST BE the actual object IDs, not necessarily the fid column but ie the number you use to get the feature when you do layer.Getfeature(Number)
#features = [i for i in range(119733678, 137166346)]
featureList = [1466960, 2696627, 14990904, 16901829, 18302930]

print "Deleting {} features from {}...".format(len(featureList), inFC)

driver = ogr.GetDriverByName('FileGDB')
fc = driver.Open(inFC, 1)
fcLayer = fc.GetLayer()


for f in featureList:

    fcLayer.DeleteFeature(f)
    
    fc.ExecuteSQL('REPACK ' + fcLayer.GetName())
    fc.ExecuteSQL('RECOMPUTE EXTENT ON ' + fcLayer.GetName())
    