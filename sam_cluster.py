#!/usr/bin/env python

import gzip
import argparse
import sys
import pysam

# FUNC
def interface():
    parser = argparse.ArgumentParser(description='Takes one BAM file and one FASTA file with contigs or a list of contig IDs. Exrtacts the reads from the fasta file that align to the given contigs and writes tehm to a gzipped multi-FASTA.')

    parser.add_argument('BAM',
                        type=str,
                        metavar='<BAM>',
                        help='BAM file with reads aligned to contigs.')

    parser.add_argument('CONTIGS',
                        type=str,
                        metavar='<CONTIGS>',
                        help='Either FASTA file with contigs or list of contig IDs.') 

    parser.add_argument('OUT',
                        type=str,
                        metavar='<OUT_FILE>',
                        help='File to output the clustered reads as multi-FASTA.')

    args = parser.parse_args()
    return args


# MAIN
if __name__ == "__main__":
    args = interface()

    bam_file = pysam.AlignmentFile(args.BAM, 'rb')
    contigs = args.CONTIGS
    out_file = args.OUT

    # All IDs in cluster to set
    contig_ids = set()
    with open(contigs, 'r') as f:
        line = f.readline()
        contig_ids.add(line)
        if line.startswith('>'):
            for line in f:
                if line.startswith('>'):
                    contig_ids.add(line)
        else:
            for line in f:
                contig_ids.add(line)

    # Extract from BAM file
    with gzip.open(out_file, 'wt') as f:
        for read in bam_file.fetch():
            if read.reference_name in contig_ids:
                f.write(read.query_sequence + '\n')
                f.write(read.query_name + '\n')





