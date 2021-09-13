#!/usr/bin/env python

import gzip
import argparse
import os
import sys

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
                        type=argparse.FileType("w"),
                        default=sys.stdout,
                        nargs="?",
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
                        default="1",
                        metavar='<field>',
                        help='Field in which to look for the identifier.')

    parser.add_argument('-i', '--id-delimiter',
                        dest='id_delim',
                        type=str,
                        metavar='<id-delimiter>',
                        help='ID delimiter in column.')

    parser.add_argument('--unique',
                        dest='unique',
                        action="store_true",
                        help='Switch to indicate if identifier is unique in source table. Causes ID to be removed from query set if found to speed up the search.')

    parser.add_argument('--header',
                        dest='header',
                        action="store_true",
                        help='Switch to extract the header from the source table.')

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
    unique_id = args.unique
    header = args.header

    # Add IDs to set
    wanted = set()
    with open(wanted_file) as f:
        for line in f:
            line = line.strip()
            if line != "":
                wanted.add(line)

    with open(table_file, "rt") as f:
        # Read and write header if header == True
        if header:
            header = f.readline()
            out_file.write(header)
        # Write all lines that match <wanted> to <out_file>
        for line in f:
            ID = line.split(delim)[field - 1]
            if id_delim:
                ID = ID.split(id_delim)[0]
            if ID in wanted:
                out_file.write(line)
                if unique_id:
                    wanted.remove(ID)
