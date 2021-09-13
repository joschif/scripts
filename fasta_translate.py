#!/usr/bin/env python

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

    def translate(self):
        table = {
        'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
        'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
        'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K',
        'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',
        'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
        'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
        'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q',
        'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
        'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V',
        'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
        'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E',
        'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
        'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
        'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
        'TAC':'Y', 'TAT':'Y', 'TAA':'', 'TAG':'',
        'TGC':'C', 'TGT':'C', 'TGA':'', 'TGG':'W',
        }
        prot = [table.setdefault(self.seq[i:i+3], "X") 
            for i in range(0, len(self.seq)-3, 3)]
        self.seq = "".join(prot)
        return self


    def write_to_file(self, handle):
        handle.write(">" + self.name + "\n")
        handle.write(self.seq + "\n")


# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Translate a FASTA [.fasta/.fa(.gz)] file.")

    parser.add_argument('IN_FASTA',
                        type=str,
                        metavar='<IN_FASTA>',
                        help='(Multi-) FASTA file [.fasta/.fa(.gz)]')

    parser.add_argument('OUT_FASTA',
                        type=str,
                        metavar='<OUT_FASTA>',
                        help='Name for translated output fasta.')

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
    fasta_file = args.IN_FASTA
    out_file = args.OUT_FASTA

    # Parse FASTA
    fasta_seqs = fasta_parser(fasta_file)

    with open(out_file, "wt") as fout:
        for record in fasta_seqs:
            record.translate().write_to_file(fout)
