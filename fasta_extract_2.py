#!/usr/bin/env python

# Shamelessly stolen and modified from @enormandeau (https://github.com/enormandeau)

import gzip
import argparse
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
    parser = argparse.ArgumentParser(description="Extract sequences from a FASTA [.fasta/.fa(.gz)] file if their identifier is in a <WANTED> file. Wanted file contains one sequence identifier per line. This version requires the identifier to be the first field of the FASTA header.")

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

    parser.add_argument('-f', '--output-file',
                        dest='out_file',
                        type=str,
                        metavar='<output-file>',
                        help='Prefix for the output file. If specified, all sequences are written to this file.')

    parser.add_argument('-d', '--delimiter',
                        dest='delim',
                        default="\t",
                        type=str,
                        metavar='<delimiter>',
                        help='Delimiter for the ID in the FASTA header.')

    parser.add_argument('--unique',
                        dest='unique',
                        action="store_true",
                        help='Switch to indicate if identifier is unique in source table. Causes ID to be removed from query set if found to speed up the search.')

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
    out_file = args.out_file
    out_dir = args.out
    if out_dir:
        # Make output directory if it does not exist
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
    delim = args.delim
    unique = args.unique


    # Add IDs to set
    wanted = set()
    with open(wanted_file) as f:
        for line in f:
            line = line.strip()
            if line != "":
                wanted.add(line)

    # Parse FASTA
    fasta_seqs = fasta_parser(fasta_file)

    if out_file:
        # Write all sequences that match <wanted> to <out_file>
        with open(out_file, "wt") as f:
            for seq in fasta_seqs:
                ID = seq.name.split(delim)[0]
                if ID in wanted:
                    seq.write_to_file(f)
                    if unique:
                        wanted.remove(ID)
    else:
        # Iterate through FASTA and write to separate file if ID in <wanted>
        for seq in fasta_seqs:
            ID = seq.name.split(delim)[0]
            if ID in wanted:
                with open(os.path.join(out_dir, ID + ".fa"), "a") as f:
                    seq.write_to_file(f)
                    if unique:
                        wanted.remove(ID)
