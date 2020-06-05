# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# del.py
# Created on: 2020-06-03 12:20:57.00000
#   (generated by ArcGIS/ModelBuilder)
# Description: 
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy


# Local variables:
v47_tif = "E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\47.tif"
v49_tif = "E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\49.tif"
v51_tif = "E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\51.tif"
v53_tif = "E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\53.tif"
v55_tif = "E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\55.tif"
v57_tif = "E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\57.tif"
v59_tif = "E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\59.tif"
v61_tif = "E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\61.tif"
v63_tif = "E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\63.tif"
v65_tif = "E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\65.tif"
v66_tif = "E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\66.tif"
v69_tif = "E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\69.tif"
v71_tif = "E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\71.tif"
v73_tif = "E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\73.tif"
v75_tif = "E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\75.tif"
BCI_WV_M1BS__count_tif = "E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\BCI_WV-M1BS__count.tif"

# Process: Cell Statistics
arcpy.gp.CellStatistics_sa("E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\47.tif;E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\49.tif;E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\51.tif;E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\53.tif;E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\55.tif;E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\57.tif;E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\59.tif;E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\61.tif;E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\63.tif;E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\65.tif;E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\66.tif;E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\69.tif;E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\71.tif;E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\73.tif;E:\\MaggieData\\ProposalStuff\\Biodiversity_2020\\DensityMaps\\temp\\BCI\\75.tif", BCI_WV_M1BS__count_tif, "SUM", "DATA")

