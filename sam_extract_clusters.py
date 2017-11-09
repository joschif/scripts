#!/usr/bin/env python

import gzip
import argparse
import sys
import pysam

# FUNC
def interface():
    parser = argparse.ArgumentParser(description='Takes one BAM file and one clustering file assigning contigs to a cluster. It then extracts all reads from the SAM file which align to that cluster.')

    parser.add_argument('BAM',
                        type=str,
                        metavar='<BAM>',
                        help='BAM file with reads aligned to contigs.')

    parser.add_argument('CLUSTERS',
                        type=str,
                        metavar='<CLUSTERS>',
                        help='Table with cluster assignments for each contig [.tsv/.csv].') 

    parser.add_argument('OUT',
                        type=str,
                        metavar='<OUT_DIR>',
                        help='Directory to output the clustered reads as multi-FASTA.')

    args = parser.parse_args()
    return args

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
            line = line.strip().split(splitchar)
            out_dict[line[0]] = line[1]

    return out_dict


# MAIN
if __name__ == "__main__":
    args = interface()

    bam_file = pysam.AlignmentFile(args.BAM, 'rb')
    clusters = read_csv_tsv(args.CLUSTERS)

    out_dir = args.OUT
    if not out_dir.endswith('/'):
        out_dir += '/'

    for read in bam_file.fetch():
        ref = read.reference_name
        try:
            seq = read.query_sequence
            name = read.query_name
            fname = '{0}cluster_{1}.fa.gz'.format(out_dir, clusters[ref])
            with gzip.open(fname, 'a') as f:
                f.write(name + '\n')
                f.write(seq + '\n')
        except KeyError:
            print('{0} is not in cluster file'.format(ref))
            pass

