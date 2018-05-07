#!/usr/bin/env python

import gzip
import argparse
import os

# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Extract lines from a table file if their identifier is in a <WANTED> file. Wanted file contains one identifier per line which has to match a column in the table file.")

    parser.add_argument('TABLE',
                        type=str,
                        metavar='<TABLE>',
                        help='Table to extract lines from.')

    parser.add_argument('WANTED',
                        type=str,
                        metavar='<WANTED>',
                        help='Wanted file with one identifier per line.')

    parser.add_argument('-o', '--output-file',
                        dest='out_file',
                        type=str,
                        metavar='<output-file>',
                        help='Prefix for the output file. If given, all lines are written to this file.')

    parser.add_argument('-d', '--delimiter',
                        dest='delim',
                        type=str,
                        default="\t",
                        metavar='<delimiter>',
                        help='Column delimiter of table.')

    parser.add_argument('-f', '--field',
                        dest='field',
                        type=int,
                        default="0",
                        metavar='<field>',
                        help='Field in which to look for the identifier.')

    parser.add_argument('-i', '--id-delimiter',
                        dest='id_delim',
                        type=str,
                        metavar='<id-delimiter>',
                        help='ID delimiter in column.')

    args = parser.parse_args()
    return args


# MAIN
if __name__ == "__main__":
    args = interface()
    table_file = args.TABLE
    wanted_file = args.WANTED
    out_file = args.out_file
    delim = args.delim
    field = args.field
    id_delim = args.id_delim

    # Add IDs to set
    wanted = set()
    with open(wanted_file) as f:
        for line in f:
            line = line.strip()
            if line != "":
                wanted.add(line)

    with open(table_file, "rt") as fin:
        # Write all lines that match <wanted> to <out_file>
        with open(out_file, "wt") as fout:
            for line in fin:
                ID = line.split(delim)[field]
                if id_delim:
                    ID = ID.split(id_delim)[0]
                if ID in wanted:
                    fout.write(line)
                    # wanted.remove(ID)
