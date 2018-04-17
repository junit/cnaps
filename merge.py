import shutil
import glob
import os
import fnmatch

if __name__ == '__main__':
    outfilename = "assets/branch.txt"
    with open(outfilename, 'wb') as outfile:
        for root, dirnames, filenames in os.walk('bank/'):
            for filename in fnmatch.filter(filenames, '*.txt'):
                if filename == outfilename:
                    # don't want to copy the output into the output
                    continue
                with open(root+"/"+filename, 'rb') as readfile:
                    shutil.copyfileobj(readfile, outfile)
