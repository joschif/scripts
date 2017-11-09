#!/usr/bin/env python

# Shamelessly stolen and modified from @enormandeau (https://github.com/enormandeau)

import gzip
import argparse
import sys
import os


# CLASS
class Fasta(object):
    """Fasta object with name and sequence
    """
    def __init__(self, name, sequence):
        self.name = name
        self.seq = sequence

    def write_to_file(self, handle):
        handle.write(">" + self.name + "\n")
        handle.write(self.seq + "\n")


# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Extract sequences from a FASTA [.fasta/.fa(.gz)] file if their identifier is in a <WANTED> file. Wanted file contains one sequence identifier per line.")

    parser.add_argument('FASTA',
                        type=str,
                        metavar='<FASTA>',
                        help='(Multi-) FASTA file [.fasta/.fa(.gz)]')

    parser.add_argument('WANTED',
                        type=str,
                        metavar='<WANTED>',
                        help='Wanted file with one identifier per line.')

    parser.add_argument('-o', '--output-dir',
                        dest='out',
                        type=str,
                        metavar='<output-directory>',
                        help='Prefix for the output folder. Defaults to name of <WANTED> if omitted.')

    args = parser.parse_args()
    return args


def fasta_parser(input_file):
    """Takes a fasta file input_file and returns a fasta iterator
    """

    with open_gz(input_file) as f:
        sequence = ""
        name = ""
        begun = False
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if begun:
                    yield Fasta(name, sequence)
                name = line.replace(">", "")
                sequence = ""
                begun = True
            else:
                sequence += line

        if name != "":
            yield Fasta(name, sequence)


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
    fasta_file = args.FASTA
    wanted_file = args.WANTED
    if args.out:
        out_dir = args.out
    else:
        out_dir = wanted_file.split(".")[0]
    if not out_dir.endswith('/'):
        out_dir += '/'
    
    # Make output directory if it does not exist
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Add IDs to set
    wanted = set()
    with open(wanted_file) as f:
        for line in f:
            line = line.strip()
            if line != "":
                wanted.add(line)

    # Parse FASTA
    fasta_seqs = fasta_parser(fasta_file)

    # Iterate through FASTA and write to file if ID in <wanted>
    for seq in fasta_seqs:
        for ID in wanted:
            if ID in seq.name and len(seq.seq) > 0:
                with open(out_dir + ID + ".fa", "a") as f:
                    seq.write_to_file(f)
