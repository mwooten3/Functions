"""
From an input shapefile that has a date columns, create date density plot

For now expect date column to be like yyyymmdd, but eventually allow for
other formats/columns names

Also create bar chart of counts per year (TODO make this optional)
-- can we show soil moisture distribution? like diff color for range
-- https://stackoverflow.com/questions/71560556/pandas-plot-histogram-of-column-with-color-indicating-the-fraction-of-counts-bel
"""



import geopandas as gpd
import pandas as pd

import numpy as np

import calendar
from collections import Counter

from datetime import datetime

import matplotlib.pyplot as plt

import os

# Input shapefile
# TODO: make input and output command line arguments
inShp = '/gpfsm/ccds01/nobackup/people/mwooten3/CI_partnership/SaloumDelta/nga20220812_WV_M1BS_strips__SaloumDelta__UTM.shp'

outPlotDir = '/gpfsm/ccds01/nobackup/people/mwooten3/CI_partnership/SaloumDelta'
outPlot = os.path.join(outPlotDir, 'SaloumDelta_WV-M1BS__dateDensityPlot.png')

# TODO: make date column be a command line option with date as default
# TODO: option to override expected format for date column - use dateFmt to extract info instead of hardcoding around defualt
dateCol = 'date' # yyyymmdd
dateFmt = '%Y%m%d' # yyyymmdd

# Function to convert one date into JD
def dateTojulianDay(dateStr, dateFmt = '%Y%m%d'):
    
    dt = datetime.strptime(dateStr, dateFmt)
    
    return dt.timetuple().tm_yday
    

# Func to create one plot for all rows in geodataframe
def createDateDensityPlot(shapefile):
    
    # Set some variables to make it easy to switch out if necessary:
    yearCol  = 'year'
    jdCol    = 'julianDay'
    jdBinCol = 'jd_bin'    
    
    title = 'Data Availability Over Time'
    
    gdf = gpd.read_file(shapefile)
    

    #print(gdf)
    cols = gdf.columns
    #print(cols)
    
    # Create year column if necessary
    # TODO: configure this to make year column with a date format that is not yyyymmdd
    #       can also be more efficient probably
    if yearCol not in cols:
        gdf[yearCol] = [s[0:4] for s in gdf[dateCol]]

    #* create JD col via datetime https://stackoverflow.com/a/13943108
    # TODO: remove hardcoding, use supplied date format instead aswell
    if jdCol not in cols:
        gdf[jdCol] = [dateTojulianDay(s) for s in gdf[dateCol]]

    #print(gdf)
            
    # Prep to bin julian days for plot purposes
    nBins = 73 # 37 for 10-day bins (36.5) or 73 for 5-day bins
    labels = [i for i in range(1, nBins+1)]

    # Create column wiht binned julian days
    if jdBinCol not in cols:
        gdf[jdBinCol] = pd.cut(gdf[jdCol], bins=nBins, labels=labels)
    
    #print(gdf)

    # 1. Date density plot
    # Count number of observations in DOY bins
    x = np.asarray(gdf[yearCol])
    y = np.asarray(gdf[jdBinCol])

    """    # Get counts for color/size plotting (methods 1 and 2)
    cntr = Counter(zip(x,y))

    sz = [10*cntr[(x1, y1)] for x1,y1 in zip(x,y)]
    
    plt.scatter(x, y, s=sz)
    
    #* WILL - add code to plot Toa strip date
    
    # Plot formatting
    plt.xlabel('Year')
    plt.ylabel('Month')
    
    steps = np.linspace(min(y), max(y), num=12)   
    plt.yticks(ticks=steps, labels=calendar.month_abbr[1:], rotation = 'horizontal')
    plt.title(title)
    plt.savefig(outPlot)
    
    plt.cla()
    plt.clf()
    plt.close()
    """
    
    # 2. Data by year histogram bar plot
    # x is already year column into arrays
    # Get list to see year range, in this case we want years with no data to be on plot
    outHist = outPlot.replace('__dateDensityPlot.png', '__yearHistogram.png')
    
    # Opt A - use matplot bar not pandas hist
    # Plot formatting
    plt.xlabel('Year')
    plt.ylabel('Strip Count')
    plt.title('Data Availability by Year')
    
    # Get bins - this returns a dict with year:count
    cntr = Counter(x)
    print(cntr)
    
    # Format x axis
    minYear = np.min(x)
    maxYear = np.max(x)
    xx = [y for y in range(minYear, maxYear+1)] # all years not just ones with data
    
    # yy is the count for all the x's in year range (so if 2013 has 0 count it is included in x axis/plot)
    yy = []
    for x in xx:
        try:
            yy.append(cntr[x])
        except KeyError: 
            yy.append(0)
            
    steps = np.linspace(minYear, maxYear, num=len(xx)).astype('int')
    plt.xticks(ticks=steps, labels=steps, rotation=45)
    
    plt.subplots_adjust(bottom=0.15)
    
    plt.bar(xx, yy)
    
    

    plt.savefig(outHist)
    
    plt.cla()
    plt.clf()
    plt.close()
    
    # IF we decide to plot all years over range
    """minYear = np.min(x)
    maxYear = np.max(x)
    xArr = [y for y in range(minYear, maxYear+1)]
    print(xArr)
    
    # to count
    #data = np.random.randint(0, 10, 1000)
    counts = np.bincount(data)

    """
    
    """    
    # Plot histogram -  using pandas.hist
    # this does not use the stuff from above but instead makes 
    # number bins = n of years in unique years
    # bins=np.arange(nBins)-0.5 to get centered x ticks did not work
    nBins = len(np.unique(x))
    ax = gdf[yearCol].plot.hist(by=yearCol, bins = nBins, 
                                                linewidth=.5, edgecolor='black')
    
    # Plot formatting vars
    ax.set_xlabel('Year')
    ax.set_ylabel('Strip Count')
    ax.set_title('Data Availability by Year')
    
    
        
    # Cannot get this to work
    ##steps = np.linspace(min(x), max(x), num=nBins)
    ##print(steps)
    ##ax.set_xticks(steps+0.3)

    ##ax.figure.savefig(outHist)
    """
    
    
    return

createDateDensityPlot(inShp)