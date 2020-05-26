# -*- coding: utf-8 -*-
"""
Created on Tue May 26 10:07:28 2020
@author: mwooten3

Purpose:
  To take sites shp for Biodiversity 2020 proposal and make density maps
   for each site (M1BS and Stereo)
   
Inputs (hard-coded as this is specific to one task):
  Sites shp, nga shp, outputdir
  
Output:
  Density maps
  
Process:
  Iterate through sites shapefile (buffered sites or polygon site outlines):
    Export site to temp Shp and call createSiteFootprints
    For each output type (M1BS and Stereo):
      Set: search terms (based on fields in output); output name; output tif
      Call featureCountToRaster.py with siteFootprints.shp
"""

