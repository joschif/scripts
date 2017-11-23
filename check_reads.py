#!/usr/bin/env python

import argparse
import gzip
import glob
import os

# FUNC
def interface():
    parser = argparse.ArgumentParser(description='Simple script to check if read filed in a directory are paired or not. Renames the files appropriately. More like an educated guess, but fast.')

    parser.add_argument('READS_DIR',
                        type=str,
                        metavar='<READS_DIR>',
                        help='Directory with reads.')

    args = parser.parse_args()
    return args

def open_gz(infile, mode='rt'):
    """Takes input and uncompresses gzip if needed
    """

    if infile.endswith('.gz'):
        return gzip.open(infile, mode=mode)
    else:
        return open(infile, mode=mode)

# MAIN
if __name__ == "__main__":
    args = interface()
    reads_dir = os.path.abspath(args.READS_DIR)
    files = glob.glob(reads_dir + '/*')
    base = [name.split('.')[0] for name in files]
    ext = ['.'.join(name.split('.')[1:]) for name in files]
    lines = []

    for file in files:
        with open_gz(file) as f:
            lines.append(f.readline())

    for n in range(len(lines)):
        for m in range(len(lines)):
            if (lines[n] != lines[m]) and (lines[n][:-1] == lines[m][:-1]):
                first = files.pop(n)
                base1 = base.pop(n)
                ext1 = ext.pop(n)
                os.rename(first, base1 + '.pair.1.' + ext1)                 
                second = files.pop(m)
                base2 = base.pop(m)
                ext2 = ext.pop(m)
                os.rename(first, base2 + '.pair.2.' + ext2) 

    for n in range(len(files)):
        os.rename(files[n], base[n] + '.single.' + ext[n])



