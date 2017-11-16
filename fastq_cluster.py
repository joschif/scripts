#!/usr/bin/env python

# Shamelessly stolen and modified from @enormandeau (https://github.com/enormandeau)

import gzip
import argparse
import sys
import os


# CLASS 
class Fastq(object):
    """Fastq object with name and sequence
    """

    def __init__(self, name, sequence, name2, qual):
        self.name = name
        self.seq = sequence
        self.name2 = name2
        self.qual = qual
        if len(self.qual) == len(self.seq):
            self.len = len(self.seq)
        else:
            self.len = -1

    def write_to_file(self, handle):
        handle.write(self.name + "\n")
        handle.write(self.seq + "\n")
        handle.write(self.name2 + "\n")
        handle.write(self.qual + "\n")


# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Extract sequences/reads from a FASTQ [.fastq/.fq(.gz)] file if their identifier is in a <CLUSTER> file. <CLUSTER> file contains one sequence identifier per line. The script writes all matching sequences to a single gzipped file.")

    parser.add_argument('FASTQ',
                        type=str,
                        metavar='<FASTQ>',
                        help='(Multi-) FASTQ file [.fasta/.fa(.gz)]')

    parser.add_argument('CLUSTER',
                        type=str,
                        metavar='<CLUSTER>',
                        help='CLUSTER file with one identifier per line.')

    parser.add_argument('-o', '--output-file',
                        dest='out',
                        type=str,
                        metavar='<output-file>',
                        help='Output file to write the extracted reads to. Defaults to the nameof the CLUSTER file if omitted.')

    args = parser.parse_args()
    return args


def fastq_parser(infile):
    """Takes a fastq file infile and returns a fastq object iterator
    """
    
    with open_gz(infile) as f:
        while True:
            name = f.readline().strip()
            if not name:
                break

            seq = f.readline().strip()
            name2 = f.readline().strip()
            qual = f.readline().strip()
            yield Fastq(name, seq, name2, qual)


def open_gz(infile, mode="rt"):
    """Takes input and uncompresses gzip if needed
    """

    if infile.endswith(".gz"):
        return gzip.open(infile, mode=mode)
    else:
        return open(infile, mode=mode)


# MAIN
if __name__ == "__main__":
    args = interface()
    fasta_file = args.FASTQ
    wanted_file = args.CLUSTER
    if args.out:
        out_file = args.out
    else:
        out_file = wanted_file.split(".")[0] + ".fq.gz"

    # Add IDs to set
    wanted = set()
    with open(wanted_file) as f:
        for line in f:
            line = line.strip()
            if line:
                wanted.add(line)

    fasta_seqs = fastq_parser(fasta_file)

    # Iterate through FASTQ and write to file if ID in CLUSTER
    with gzip.open(out_file, "wt") as f:
        for seq in fasta_seqs:
            if seq.name in wanted:
                seq.write_to_file(f)
