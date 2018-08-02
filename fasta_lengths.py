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
	parser = argparse.ArgumentParser(description='Takes one ore more (multi-)FASTA file(s) and calculates basic stats for quality estimation. Returns the stats as tab separated values in standard output.')

	parser.add_argument('FASTA',
						type=str,
						metavar='<FASTA>',
						help='FASTA file [.fasta/.fa(.gz)].')

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

	fasta_seqs = fasta_parser(args.FASTA)

	for record in fasta_seqs:
		length = len(record.seq)
		base = record.name.split()[0]
		ncbi = base.split(".")[0]
		prj = base.split(".")[1]
		line = [str(_) for _ in [ncbi, prj, base, length]]
		sys.stdout.write('\t'.join(line) + '\n')
