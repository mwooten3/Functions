# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 14:00:35 2021
@author: mwooten3

Remove duplicates from a .gdb or .shp

PURPOSE:
    Given input feature class, write a new output .gdb (__removedDuplicates.gdb)
    that contains only one version of each feature 

PROCESS:
    Iterate through features in input FC
        Get geometry from attributes/feature
        Get other specified field names that the user inputs
        Use info to apply filter to input dataset
        Record only the first feature result in search/filter
    Also record n of duplicates, etc.
"""

