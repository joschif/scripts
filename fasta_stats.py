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
	parser = argparse.ArgumentParser(description='Takes one ore more (multi-)FASTA file(s) and calculates basic stats for quality estimation. Returns the stats as tab separated values.')

	parser.add_argument('FASTA',
						type=str,
						metavar='<FASTA>',
						nargs='+',
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

	for fasta_file in args.FASTA:
		basename = '.'.join(fasta_file.split('.')[0:-1]).split('/')[-1]
		fasta_seqs = fasta_parser(fasta_file)

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

		stats = [basename, seq_num, assembly_len, mean_len, longest_contig, shortest_contig, GC_cont, N_cont, N50, L50]
		line = [str(n) for n in stats]
		sys.stdout.write('\t'.join(line) + '\n')

