#!/usr/bin/env python

import gzip
import argparse
import sys


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
    parser = argparse.ArgumentParser(description='Takes one multi-FASTA (contigs) and sorts it according to a clustering table assigning each contig to a cluster.')

    parser.add_argument('FASTA',
                        type=str,
                        metavar='<FASTA>',
                        help='FASTA file [.fasta/.fa(.gz)].')    

    parser.add_argument('CLUSTERS',
                        type=str,
                        metavar='<CLUSTERS>',
                        help='Table with cluster assignments for each contig [.tsv/.csv].')    

    parser.add_argument('OUT',
                        type=str,
                        metavar='<OUT_DIR>',
                        help='Directory to output the sorted sequences.')



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


def read_csv_tsv(input_file):
    '''Takes a two-column table file in .csv or .tsv format and returns a dict
    '''

    splitchar = ''
    if input_file.endswith('.csv'):
        splitchar = ','
    if input_file.endswith('.tsv'):
        splitchar = '\t'

    out_dict = dict()
    with open(input_file, 'r') as f:
        for line in f:
            line = line.split(splitchar)
            out_dict[line[0]] = line[1]

    return out_dict



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

    contigs = fasta_parser(args.FASTA)
    clusters = read_csv_tsv(args.CLUSTERS)

    out_dir = args.out
    if not out_dir.endswith('/'):
        out_dir += '/'

    for contig in contigs:
        if contig.name in clusters.keys():
            out_name = 'cluster_{0}.fa'.format(clusters[contig.name])
            with open(out_dir + out_name, 'a') as f:
                contig.write_to_file(f)

