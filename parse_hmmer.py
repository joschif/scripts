#!/usr/bin/env python

import argparse
import sys

# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Takes a HMMER output file (--domtblout/.dom) and converts it into a nice TSV file.")

    parser.add_argument("DOM",
                        type=str,
                        metavar="<HMMER-output>",
                        help="HMMER output file from --domtblout.")

    parser.add_argument("OUT",
                        type=argparse.FileType("w"),
                        default=sys.stdout,
                        nargs="?",
                        metavar="<TSV-out>",
                        help="Name of the output TSV file.") 

    args = parser.parse_args()
    return args

# MAIN
if __name__ == "__main__":
    args = interface()

    dom_file = args.DOM
    out_file = args.OUT

    header = ["name", "gene_accession", "tlen", "query", "hmm_accession", "qlen", "E-value_full", "score_full", "c-Evalue", "i-Evalue", "score", "hmm_start", 
        "hmm_end", "ali_start", "ali_end", "env_start", "env_end", "acc", "description"]
    out_file.write("\t".join(header) + "\n")

    with open(dom_file, "rt") as f:
        for line in f:
            if not line.startswith("#"):
                line = line.split()
                row = line[0:8] + line[11:14] + line[15:22] + [" ".join(line[22:])]
                out_file.write("\t".join(row) + "\n")
