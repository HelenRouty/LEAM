"""
This script will do:
1. (optional)-overlap the miniumum of 100 travelcost maps to have a complete travelcost map. ./Data/travelcost-pop.txt
2. read the interpolated attrmap and the travelcost map into an array seperately, and create a dictionary to map them. Sort.
3. use the two arrays and matplotlib libarary and ggplot2 to generate:
   (1) travelcost vs. attractiveness graph
   (2) travelcost vs. low&high residential frequency (type 21, 22)
   (3) travelcost vs. low&high commercial frequency (type 23, 24)
   (4) attractiveness vs. low&high residentail frequency 
   (5) attractivenss vs. low&high commercial frequency

"""

#from ggplot import * #ggplot is best to be used with pandas DataFrames
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from reducemaps import extractheader, outfilename
import time 

LANDUSEMAP = "./Data/landuse.txt"
RESIDENTIALMIN = 21
RESIDENTIALMAX = 22
COMMERCIALMIN =  23
COMMERCIALMAX = 24
#ATTRBASEMAX = 3817
TRVALCOSTBASE = 999
ATTRFREQ_COM = "./Data/attrfreq-commericial.png"
ATTRFREQ_RES = "./Data/attrfreq-residential.png"
COSTFREQ_COM = "./Data/trcostfreq-commercial.png"
COSTFREQ_RES = "./Data/trcostfreq-residential.png"
RES = "Residential"
COM = "Commercial"
ATT = "Attractiveness"
CST = "Travelcost"

# for gettravelcostmap
ISEMP = 0
if ISEMP == 1:
    CENTERLIST = "./Data/empcenterlist.txt"
    ATTRMAP = "./Data/attrmap-emp-interpolated.txt"
    TRAVELCOSTPATH = "./Data/costmaps-emp"
    TRCOSTMAP = "./Data/costmap-emp.txt"
else:
    CENTERLIST = "./Data/popcenterlist.txt"
    ATTRMAP = "./Data/attrmap-pop-interpolated.txt"
    TRAVELCOSTPATH = "./Data/costmaps"
    TRCOSTMAP = "./Data/costmap-pop.txt"
TRAVELCOSTMAP = "travelcostmap.txt"
HEADER = "./Input/arcGISheader.txt"


def to_percent(y, position):
    """[reference:http://matplotlib.org/examples/pylab_examples/histogram_percent_demo.html]
    """
    s = str(100 * y)

    # The percent symbol needs escaping in latex
    if matplotlib.rcParams['text.usetex'] is True:
        return s + r'$\%$'
    else:
        return s + '%'

def to_hundreds(x, position):
    return str(100* x)

def add_base(x, position):
    return str(x+20)

def plotgraph(xsize, y, outfile, name, mapname):
    plt.close("all")
    fig, ax = plt.subplots()
    # set the grids of the x axis
    if mapname == ATT:
        major_ticks = xrange(0, xsize+1, 50)
        minor_ticks = xrange(0, xsize+1, 10)
    else:
        major_ticks = xrange(0, xsize+1, 10)
        minor_ticks = xrange(0, xsize+1, 1)
    ax.set_xticks(major_ticks)
    ax.set_xticks(minor_ticks, minor=True)
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)

    # set the range of the y axis
    plt.ylim(0, 1)
    # set the title and labels
    plt.title(name +' ' + mapname + ' Frequency Distribution')
    plt.xlabel(mapname + ' Score')
    plt.ylabel('Fraction ' + name + ' Over All Landuse Type ' + mapname +' Frequency')
    # set the x axis values to be 100 times and y axis values to be 100% times.
    if mapname == ATT:
        formatter = FuncFormatter(to_hundreds) 
    else:
        formatter = FuncFormatter(add_base)
    plt.gca().xaxis.set_major_formatter(formatter)
    formatter = FuncFormatter(to_percent)
    plt.gca().yaxis.set_major_formatter(formatter)

    #plot the graph and pinpoint the max y value point
    plt.plot(y)
    ymax_index = np.argmax(y)
    ymax = y[ymax_index]
    plt.scatter(ymax_index, ymax)

    # save the figure to file
    plt.savefig(outfile)

def frequencyanalysis(arr, maskcondition, arr_count, arr_countsize, outfile, name, mapname):
    mask_arr = arr[maskcondition]
    if mapname == CST:
        mask_arr = mask_arr[mask_arr != TRVALCOSTBASE]
    mask_arr_count = np.bincount(mask_arr)
    if mapname == ATT:
        ### needs to be modified!!! (select 1 out of 100)
        mask_arr_count = mask_arr_count[mask_arr_count!=0]  # keep only the attractiveness scores of 100 times
        mask_arr_align = np.zeros(arr_countsize-mask_arr_count.shape[0])
        mask_arr_count = np.concatenate((mask_arr_count, mask_arr_align), axis=0)

    print mask_arr_count.round().astype(int)
    mask_arr_freq  = np.divide(mask_arr_count, arr_count)
    mask_arr_freq  = np.nan_to_num(mask_arr_freq)
    mask_arr_freq[mask_arr_freq > 100] = 0 # hack. There was overflow...
    print (mask_arr_freq*100).round().astype(int)
    plotgraph(arr_countsize, mask_arr_freq, outfile, name, mapname)

def gettravelcostmap(nrows, ncols):
    with open(CENTERLIST, 'r') as p:
        centerlist = p.readlines()
     
    trcostdf = pd.DataFrame(index=xrange(nrows), columns=xrange(ncols)) #initialize costmap with nan
    trcostdf = trcostdf.fillna(999)    #initialize costmap with 999

    for i in range(99):
        (disW, disN, weight) = centerlist[i].strip('\n').split(',')
        costmapfile = outfilename(disW, disN, TRAVELCOSTPATH, TRAVELCOSTMAP, "NW", 100)
        try:
            newtrcostdf = pd.read_csv(costmapfile, skiprows=6, header=None, sep=r"\s+" ) #skip the 6 header lines
        except IOError:
            print "file not found: ", outfilename
            continue
        trcostdf = np.minimum(trcostdf, newtrcostdf)
      
    header = extractheader(HEADER)
    with open(TRCOSTMAP, 'w') as w:
        w.writelines(header)
    trcostdf.round() # round to integer
    trcostdf.to_csv(path_or_buf=TRCOSTMAP, sep=' ', index=False, header=False, mode = 'a') # append
    return trcostdf

def main():
    start = time.time()

    landusemap     = pd.read_csv(LANDUSEMAP, sep=r"\s+", skiprows=6, header=None)
    attrmap        = pd.read_csv(ATTRMAP, sep=r"\s+", skiprows=6, header=None)
    attrmap        = attrmap.mul(0.01).round().mul(100).round().astype(np.int)
    #(nrows, ncols) = landusemap.shape
    #travelcostmap  = gettravelcostmap(nrows, ncols)
    travelcostmap  = pd.read_csv(TRCOSTMAP, sep=r"\s+", skiprows=6, header=None)
    travelcostmap  = travelcostmap.round().astype(np.int)
    
    landuse_arr    = landusemap.values.flatten()
    attr_arr       = attrmap.values.flatten()
    attr_count     = np.bincount(attr_arr)
    attr_countsize = attr_count.shape[0]

    attr_count     = attr_count[attr_count!=0] # keep only the attractiveness scores of 100 times
    attr_countsize = attr_count.shape[0]
    cost_arr       = travelcostmap.values.flatten()
    cost_arr_nobase= cost_arr[cost_arr != TRVALCOSTBASE]
    cost_count     = np.bincount(cost_arr_nobase)
    cost_countsize = cost_count.shape[0]
    mask_res       = (landuse_arr >= RESIDENTIALMIN)& (landuse_arr <= RESIDENTIALMAX)
    mask_com       = (landuse_arr >= COMMERCIALMIN) & (landuse_arr <= COMMERCIALMAX)

    frequencyanalysis(attr_arr, mask_res, attr_count, attr_countsize, ATTRFREQ_RES, RES, ATT) # attrfreq-residential
    frequencyanalysis(attr_arr, mask_com, attr_count, attr_countsize, ATTRFREQ_COM, COM, ATT) # attrfreq-commercial
    frequencyanalysis(cost_arr, mask_res, cost_count, cost_countsize, COSTFREQ_RES, RES, CST) # costfreq-residential
    frequencyanalysis(cost_arr, mask_com, cost_count, cost_countsize, COSTFREQ_COM, COM, CST) # costfreq-residential

    print time.time()-start

if __name__ == "__main__":
    main()
    
