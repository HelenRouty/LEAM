import pandas as pd
import numpy as np
import time
from scipy.interpolate import griddata
from multiprocessing.dummy import Pool

from Utils import extractheader

"""
Time consumption for 64 threads and 1 repeattime: 12min
Time consumption for 64 threads and 2 repeattime: 24min
Time consumption for 32 threads and 2 repeattime: 23min
Time consumption for no thread  and 1 repeattime with landuse type considered: 4min!!!
"""
ISEMP = 0
REPEATNUM = 5
# INPUT="testmap2"
# OUTPUT="testmapout"

if ISEMP == 0:
    INPUT="./Data/costmap-pop.txt"
    OUTPUT="./Data/costmap-pop-interpolated.txt"
else:
    INPUT="./Data/costmap-emp.txt"
    OUTPUT="./Data/costmap-emp-interpolated.txt"

HEADER="./Input/arcGISheader.txt"
WEIGHTMAP = "./Input/weightmap-travelcost.txt"
SPEEDMAP = "./Data/speedmap.txt"
CELLSIZE = 30
#THREADNUM = 32


class SmoothCost():
    def __init__(self, matrix, weightarray, speed_df, cellsize=CELLSIZE, repeattimes=REPEATNUM):
        start = time.time()
        self.weightarray = weightarray
        self.matrix = matrix
        (self.rows, self.cols) = matrix.shape
        self.maxrow = self.rows-2
        self.maxcol = self.cols-2
        self.cellsize = cellsize
        self.speed_df = speed_df
        self.smoothedmap = np.zeros((self.rows, self.cols), dtype=np.int)
        self.smoothedmap.fill(999)
        self.smooth2min(repeattimes)

    def smoothrow(self, rowidx):
        """This function assigns the center of 5*5 cells a value that equals to the sum of all cells having larger values multiplying by
           a weight. The weight is read from the input weightmap and has a value propotional to the distance to the center cell. Repeat 
           the steps for all cells of the row with rowidx in the attrmap matrix.
           @param: rowidx is the row index of the attrmap matrix.
           @output: the smoothedmap filled with row index of rowidx.
        """
        if rowidx < 2 or rowidx >= self.maxrow:
            return
        #debug: print "rowidx: ", rowidx , "==========="
        for colidx in xrange(2, self.maxcol): # for each cell in a row
            #debug: print "colidx: ", colidx, "-----------"
            matrix_arr = self.matrix[rowidx-2:rowidx+3, colidx-2:colidx+3].flatten()
            minindex   = np.argmin(matrix_arr)
            minval     = matrix_arr[minindex]
            # print "--------------"
            # print "cur val:", self.matrix[rowidx][colidx]
            # print "minindex", minindex
            # print "minval: ", minval
            # print "### len weightarray ", len(self.weightarray)
            weight     = self.weightarray[minindex]
            speed      = self.speed_df.ix[rowidx, colidx]
            # print "speed: ", speed
            # print "weight: ", weight 
            # print "final: ", minval + self.cellsize*weight/speed

            try:
                self.smoothedmap[rowidx][colidx] = minval + self.cellsize*weight/speed
            except ZeroDivisionError:
                self.smoothedmap[rowidx][colidx] = self.matrix[rowidx][colidx]
                print "Error: Divide by Zero. Speedmap contains zero speed."    
        
    def smooth2min(self, repeattimes):
        """smooth2min creates THREADNUM number of threads to parallell smoothing each row of the attrmap matrix.
            As the two side columns and rows are not smoothed in the attrmap, overlay the original map and smoothedmap
            can obtain the original attrativenesss score for the side columns and rows. Also, cells that decreases its
            values due to rounding to int can have the original higher values back.
        """
        for i in xrange(repeattimes):
            #pool = Pool(THREADNUM)
            #pool.map(self.smoothrow, xrange(self.rows))
			
            #debug:
            for rowidx in xrange(self.rows):
               self.smoothrow(rowidx)
            self.matrix = np.minimum(self.smoothedmap, self.matrix)
        self.smoothedmap = self.matrix

def outputmap(attrmap, header, output):
    with open(output, 'w') as f:
        f.writelines(header)
        np.savetxt(f, attrmap, fmt='%d',delimiter=' ')

def main():
    costmap_df = pd.read_csv(INPUT, sep=' ', skiprows=6, header=None, dtype=np.float)
    costmap = np.asarray(costmap_df).round()
    weightarray = np.fromfile(WEIGHTMAP, sep=' ', dtype=np.float)
    speed_df = pd.read_csv(SPEEDMAP, sep=' ', skiprows=6, header=None, dtype=np.int)
    
    smoothcost = SmoothCost(costmap, weightarray, speed_df)
    costmap = smoothcost.smoothedmap

    header = extractheader(HEADER)
    outputmap(costmap, header, OUTPUT)

if __name__ == "__main__":
	main()
