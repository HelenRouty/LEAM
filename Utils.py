import os
def createdirectorynotexist(fname):
    """Create a directory if the directory does not exist.
       @param: fname is the full file path name
       @reference:[http://stackoverflow.com/questions/12517451/python-automatically-creating-directories-with-file-output]
    """
    if not os.path.exists(os.path.dirname(fname)):
        try:
            os.makedirs(os.path.dirname(fname))
        except OSError as exc: #Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def extractheader(header):
    with open(header, 'r') as h:
        header = h.read()
    return header


def outfilename(cellx, celly, path, fname, dirname, count):
    """Modify filename "file.txt" to be "cell0_0/Data/file_0_0_SE1.txt" for starting cell (0,0) on the first 2hrs run.
    """
    return path + "/cell" + "_" + str(cellx) + "_" + str(celly) + "/" + fname[:-4] \
                         + "_" + str(cellx) +"_" + str(celly) + "_" +dirname + str(count) + ".txt"
