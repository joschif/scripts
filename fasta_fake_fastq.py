#!/usr/bin/env python

import gzip
import argparse
import sys


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


class Fasta(object):
    """Fasta object with name and sequence
    """
    def __init__(self, name, sequence):
        self.name = name
        self.seq = sequence

    def write_to_file(self, handle):
        handle.write(">" + self.name + "\n")
        handle.write(self.seq + "\n")

    def to_fake_fastq(self, symbol='I'):
        name = '@' + self.name
        qual = symbol * len(self.seq) 
        return Fastq(name, self.seq, '+', qual)


# FUNC
def interface():
    parser = argparse.ArgumentParser(description='Takes one (multi-)FASTA file(s) and outputs a fake FASTQ file with <quality-symbol> as the quality line.')

    parser.add_argument('FASTA',
                        type=str,
                        metavar='<FASTA_IN>',
                        help='FASTA file [.fasta/.fa(.gz)].')

    parser.add_argument('FASTQ',
                        type=str,
                        metavar='<FASTQ_OUT>',
                        help='Out FASTQ file [.fasta/.fa(.gz)].')

    parser.add_argument('-q',
                        type=str,
                        dest='qualsym',
                        default='I',
                        metavar='<quality-symbol>',
                        help='Quality symbol for FASTQ. Defaults to "I"')

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


def open_gz(infile, mode="r"):
    """Takes input and uncompresses gzip if needed
    """

    if infile.endswith(".gz"):
        return gzip.open(infile, mode=mode)
    else:
        return open(infile, mode=mode)


# MAIN
if __name__ == "__main__":
    args = interface()

    fasta_in = fasta_parser(args.FASTA)
    sym = args.qualsym

    with open_gz(args.FASTQ, 'w') as fout:
        for read in fasta_in:
            read.to_fake_fastq(sym).write_to_file(fout)