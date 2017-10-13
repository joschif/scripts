#!/usr/bin/env python

import gzip
import argparse
import sys

# FUNC
def interface():
	parser = argparse.ArgumentParser(description='Takes one file with sequences in FASTA or FASTQ format and counts the occurences of each ID in an <ID_FILE>. Returns a tab separated list in standart output.')

	parser.add_argument('SEQUENCES',
						type=str,
						metavar='<SEQS>',
						help='File with sequences [.fasta/.fa/.fq(.gz)].')

	parser.add_argument('IDs',
						type=str,
						metavar='<ID_FILE>',
						help='File with one ID per line to be matched in the header of the sequences.')

	args = parser.parse_args()
	return args


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
	seq_file = args.SEQUENCES
	ID_file = args.IDs

	# Add IDs to dict
	IDs = dict()
	with open(ID_file) as f:
		for line in f:
			line = line.strip()
			if line != "":
				IDs[line] = 0


   	with open_gz(seq_file, "r") as f:
   		for line in f:
   			if line.startswith("@") or line.startswith(">"):
   				for ID in IDs.keys():
   					if ID in line:
   						IDs[ID] += 1

   	num_reads = sum([n for n in IDs.values()])
   	for ID, count in IDs.items():
   		sys.stdout.write("\t".join([ID, str(count), str(count / float(num_reads))]) + "\n")


