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

    def get_shortname(self, separator):
        if separator:
            self.temp = self.name.split(separator)
            del(self.temp[-1])
            return separator.join(self.temp)
        else:
            return self.name

    def write_to_file(self, handle):
        handle.write(self.name + "\n")
        handle.write(self.seq + "\n")
        handle.write(self.name2 + "\n")
        handle.write(self.qual + "\n")


# FUNC
def interface():
    parser = argparse.ArgumentParser(
        description='Takes one ore more (multi-)FASTA file(s) and calculates basic stats for quality estimation. Returns the stats as tab separated values.')

    parser.add_argument('FASTA',
                        type=str,
                        metavar='<FASTA>',
                        nargs='+',
                        help='FASTA file [.fasta/.fa(.gz)].')

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

    for fasta_file in args.FASTA:
        basename = '.'.join(fasta_file.split('.')[0:-1]).split('/')[-1]
        fasta_seqs = fastq_parser(fasta_file)

        seq_num = N_num = GC_num = 0
        contigs = []

        for record in fasta_seqs:
            seq_num += 1
            N_num += record.seq.count('N')
            GC_num += record.seq.count('G')
            GC_num += record.seq.count('C')
            contigs.append(record.seq)

        lengths = [len(s) for s in contigs]
        assembly_len = sum(lengths)
        mean_len = assembly_len / len(contigs)
        longest_contig = max(lengths)
        shortest_contig = min(lengths)
        GC_cont = GC_num / float(assembly_len)
        N_cont = N_num / float(assembly_len)

        N50 = L50 = test_sum = 0
        for l in sorted(lengths, reverse=True):
            L50 += 1
            test_sum += l
            if test_sum >= assembly_len / 2:
                N50 = l
                break

        stats = [basename, seq_num, assembly_len, mean_len,
                 longest_contig, shortest_contig, GC_cont, N_cont, N50, L50]
        line = [str(n) for n in stats]
        print('\t'.join(line) + '\n')
        sys.stdout.write('\t'.join(line) + '\n')
