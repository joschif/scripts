#!/usr/bin/env python

import os
import argparse
from fastq_reader import *


# FUNC
def interface():
    parser = argparse.ArgumentParser(
        description="Merges paired files and splits to interleaved.")

    parser.add_argument("-1",
                        dest="READS_1",
                        type=str,
                        metavar="<reads_1>",
                        help="First part of paired reads.")    

    parser.add_argument("-2",
                        dest="READS_2",
                        type=str,
                        metavar="<reads_2>",
                        help="Second part of paired reads.")

    parser.add_argument("-r",
                        dest="READS",
                        type=str,
                        metavar="<reads>",
                        help="Unpaired or interleaved reads.")

    parser.add_argument("-n",
                        dest="num_reads",
                        default="100000",
                        type=int,
                        metavar="<n_reads>",
                        help="Number of reads per split file.")

    parser.add_argument("-o", "--output-dir",
                        dest="out",
                        default="./",
                        type=str,
                        metavar="<output-directory>",
                        help="Output directory for splitting the reads.")

    args = parser.parse_args()
    return args


# MAIN
if __name__ == "__main__":
    args = interface()

    reads_1 = args.READS_1
    reads_2 = args.READS_2
    reads_single = args.READS
    num_reads = args.num_reads
    out_dir = os.path.abspath(args.out)
    if not out_dir.endswith("/"):
        out_dir += "/"

    if reads_1 and reads_2:
        interleaved = interleave(parse(reads_1), parse(reads_2))
        basenames = [os.path.basename(r) for r in [reads_1, reads_2]]
        prefix = os.path.commonprefix(basenames) + "interleaved.fq.gz"
        split(interleaved, num_reads, out_dir + prefix)

    if reads_single:
        single = parse(reads_single)
        split(single, num_reads, out_dir + os.path.basename(reads_single) + ".gz")
