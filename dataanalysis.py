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
from optparse import OptionParser
from reducemaps import extractheader, outfilename
import time 

LANDUSEMAP = "./Data/landuse.txt"
RESIDENTIALMIN = 21
RESIDENTIALMAX = 22
COMMERCIALMIN =  23
COMMERCIALMAX = 24
ATTRBASKETNUM = 10
COSTBASEKTNUM = 10
ATTRBASE = 3817
COSTBASE = 999
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

def plotgraph_attr(x, y, xsize, outfile, name, mapname):
    plt.close("all")
    fig, ax = plt.subplots()
    # set the grids of the x axis
    if mapname == ATT:
        major_ticks = xrange(0, x[-1]+2000, 2000)
        minor_ticks = xrange(0, x[-1]+2000, 1000)
    else:
        major_ticks = xrange(0, x[-1]+10, 10)
        minor_ticks = xrange(0, x[-1]+10, 1)
    ax.set_xticks(major_ticks)
    ax.set_xticks(minor_ticks, minor=True)
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)

    # minor_ticks = xrange(2000, 18000)
    # ax.set_xticks(minor_ticks, minor=True)
    # ax.grid(which='minor', minor=True)
    # ax.grid(which='minor', alpha=0.2)
    # set the range of the y axis
    plt.ylim(0, 1)
    # set the title and labels
    plt.title(name +' ' + mapname + ' Frequency Distribution')
    plt.xlabel(mapname + ' Score')
    plt.ylabel('Fraction ' + name + ' Over All Landuse Type ' + mapname +' Frequency')
    # set the x axis values to be 100 times and y axis values to be 100% times.
    # if mapname == CST:
    #     formatter = FuncFormatter(add_base)
    #     plt.gca().xaxis.set_major_formatter(formatter)
    formatter = FuncFormatter(to_percent)
    plt.gca().yaxis.set_major_formatter(formatter)

    #plot the graph and pinpoint the max y value point
    plt.plot(x, y, 'ro--')
    ymax_index = np.argmax(y)
    ymax       = y[ymax_index]
    ymax_xval  = x[ymax_index]
    print ymax_xval, ymax
    plt.scatter(ymax_xval, ymax*100)
    plt.grid(True)

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
    """Generate travelcost map by overlapping the 100 pop/emp center travelcost maps
       and obtain the minimal value of each cell in these 100 maps.
       This process takes several minutes.
       @param: nrows is # rows and ncols is # columns of travelcostmaps.
       @output: the overlapped minimal value travelcostmap
    """
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

    parser = OptionParser()
    parser.add_option("-g", "--gentravelcost", default=False, action="store_true",
        help="generate travelcostmap by overlapping 100 maps. pop/emp needs to be speicified in this source code.")
    (options, args) = parser.parse_args()
    if options.gentravelcost:
        print "generate travelcostmap..."
        (nrows, ncols) = landusemap.shape
        travelcostmap  = gettravelcostmap(nrows, ncols)
        print "finish generating travelcostmap."

    start = time.time()

    landusemap     = pd.read_csv(LANDUSEMAP, sep=r"\s+", skiprows=6, header=None)
    attrmap        = pd.read_csv(ATTRMAP, sep=r"\s+", skiprows=6, header=None)
    try:
        travelcostmap  = pd.read_csv(TRCOSTMAP, sep=r"\s+", skiprows=6, header=None)
    except IOError:
        print "Error: No travelcostmap found. You need to use -g as argument to genearte travelcostmap."
        exit(1)
    
    landuse_arr    = landusemap.values.flatten()
    mask_res       = (landuse_arr >= RESIDENTIALMIN)& (landuse_arr <= RESIDENTIALMAX)
    mask_com       = (landuse_arr >= COMMERCIALMIN) & (landuse_arr <= COMMERCIALMAX)

    attr_arr       = attrmap.values.flatten()
    attr_res_arr   = attr_arr[mask_res]
    attr_com_arr   = attr_arr[mask_com]
    cost_arr       = travelcostmap.values.flatten()
    cost_res_arr   = cost_arr[mask_res]
    cost_com_arr   = cost_arr[mask_com]


    # find one x axis (quantile or equal interval) for attr_arr, attr_res_arr, attr_com_arr
    # note that, about 63.5% attrmap cells have base value, so we do not consider base value cells
    # when finding x axis for quantile. We will set attrbase as the first x tick.
    attr_arr_nobase    = attr_arr[attr_arr > ATTRBASE] 
    attr_arr_nblen     = len(attr_arr_nobase)
    attrbasketsize     = attr_arr_nblen/ATTRBASKETNUM
    attr_arr_nbsort    = np.sort(attr_arr_nobase)
    attr_arr_x         = attr_arr_nbsort[0:attr_arr_nblen-1:attrbasketsize] # the x axis tick values 
    attr_arr_x         = np.concatenate(([ATTRBASE], attr_arr_x.tolist()))  # need add one basket for base value
    attr_arr_x         = attr_arr_x[0:ATTRBASKETNUM+1]                      # merge the last basket to the previous one
    attrbasketsize_1st = len(attr_arr[attr_arr == ATTRBASE])
    attrbasketsize_last= attr_arr_nblen%ATTRBASKETNUM
    attrbasketsize_nths= np.full((1, ATTRBASKETNUM), attrbasketsize,dtype=np.int)
    attr_arr_freq      = np.insert(attrbasketsize_nths, 0, attrbasketsize_1st)
    attr_arr_freq[ATTRBASKETNUM] += attrbasketsize_last                     # in total ATTRBASKETNUM baskets

    attr_res_arr_nobase     = attr_res_arr[attr_res_arr > ATTRBASE]
    attr_res_arr_nbsort     = np.sort(attr_res_arr_nobase)
    attr_res_basketsize_1st = len(attr_res_arr[attr_res_arr == ATTRBASE])
    attr_res_freq = []
    attr_res_freq = np.append(attr_res_freq, attr_res_basketsize_1st)
    cur1 = attr_arr_x[1]
    count = 0
    for i in xrange(2, ATTRBASKETNUM+1): #i is for cur2. in total ATTRBASKETNUM baskets.
        cur2 = attr_arr_x[i]
        mask = (attr_res_arr >= cur1) & (attr_res_arr < cur2)
        attr_res_freq = np.append(attr_res_freq, len(attr_res_arr[mask]))
        cur1 = cur2
        count+=1
    attr_res_freq = np.append(attr_res_freq, len(attr_res_arr[attr_res_arr >= cur1]))
    
    attr_res_y = np.divide(attr_res_freq, attr_arr_freq)
    attr_res_y = np.nan_to_num(attr_res_y)
    plotgraph_attr(attr_arr_x, attr_res_y, ATTRBASKETNUM, ATTRFREQ_RES, RES, ATT)
    # plotgraph_attr(attr_arr_x, attr_res_y, ATTRBASKETNUM, ATTRFREQ_COM, COM, ATT)


if __name__ == "__main__":
    main()
    
