#!/usr/bin/env python

import sys
import argparse
import gzip
import glob
import os
import itertools

# FUNC
def interface():
    parser = argparse.ArgumentParser(description='Simple script to check if read filed in a directory are paired or not. Renames the files appropriately. Quick and dirty, more like an educated guess, but fast.')

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
    names = glob.glob(reads_dir + '/*')
    names.sort()
    base = [name.split('.')[0] for name in names]
    ext = ['.'.join(name.split('.')[1:]) for name in names]
    files = [list(rec) for rec in zip(names, base, ext)]

    for file in files:
        with open_gz(file[0]) as f:
            line1 = f.readline().strip()
            if line1.startswith('>'):
                file.append(line1)
                for line in f:
                    if line.startswith('>'):
                        file.append(line.strip())
                        break     
            if line1.startswith('@'):
                file.append(line1)
                [f.readline() for n in range(3)]
                file.append(f.readline().strip())
            else:
                raise TypeError("Files have to be in FASTQ or FASTA format")


    inter = []
    for file in files: 
        if file[3][:-1] == file[4][:-1]:
            inter.append(file)
            files.remove(file)

    firsts = []
    seconds = []
    for comb in itertools.combinations(files, 2):
        if comb[0][3][:-1] == comb[1][3][:-1] and comb[0][3] != comb[1][3]:
            firsts.append(comb[0])
            seconds.append(comb[1])

    singles = []
    for file in files:
        if file not in firsts and file not in seconds:
            singles.append(file)

    for rec in inter:
        if '.pairs.interleaved.' not in rec[2]:
            os.rename(rec[0], rec[1] + '.pairs.interleaved.' + rec[2])                 
    
    for rec in firsts:
        if '.pair.1.' not in rec[2] and '.pair.2.' not in rec[2]:
            os.rename(rec[0], rec[1] + '.pair.1.' + rec[2])      

    for rec in seconds:
        if '.pair.1.' not in rec[2] and '.pair.2.' not in rec[2]:
            os.rename(rec[0], rec[1] + '.pair.2.' + rec[2])                 
    
    for rec in singles:
        if '.single.' not in rec[2]:
            os.rename(rec[0], rec[1] + '.single.' + rec[2])                 
    

    



