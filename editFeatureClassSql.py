# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 14:26:56 2020
@author: mwooten3

PURPOSE: To edit a feature class (shp or gdb) using SQL

For whatever reason editing fields or stuff in a .gdb table is very hard
I've only had success with the Python/GDAL API

This script is set up to edit a file based on SQL, and includes examples

"""

from osgeo import gdal

# Path to feature class
gdb = '/att/gpfsfs/briskfs01/ppl/mwooten3/3DSI/GLAS_naBoreal.gdb'



#import pdb; pdb.set_trace()
ds = gdal.OpenEx(gdb, gdal.OF_VECTOR | gdal.OF_UPDATE)


"""
EXAMPLES
  https://gdal.org/user/ogr_sql_dialect.html

# Calculate an existing field -> update the GLAS_naBoreal table; calculate uniqueID column to = fid
statement = 'UPDATE GLAS_naBoreal SET uniqueID = fid' 

# Remove a column
statement = "ALTER TABLE <tableName> DROP COLUMN <columnName>"
"""

statement = "ALTER TABLE GLAS_naBoreal DROP COLUMN SHAPE_Area"



# Execute the SQL statement:
ds.ExecuteSQL(statement)


# Release dataset
ds = None