#!/usr/bin/env python

import sys
import argparse
from Bio import AlignIO as aio


# FUNC
def interface():
	parser = argparse.ArgumentParser(description='Parses needle files to extract alignment stats.')

	parser.add_argument('NEEDLE',
						type=str,
						metavar='<NEEDLE>',
						nargs='+',
						help='NEEDLE output file [.needle].')

	args = parser.parse_args()
	return args


# MAIN
if __name__ == "__main__":
	args = interface()

	header = ['query_id', 'subject_id', 'aln_length', 'prc_identity', 'prc_similarity',
		'gaps', 'score']
	sys.stdout.write('\t'.join(header) + '\n')

	for needle_file in args.NEEDLE:
		ndl = aio.parse(needle_file, 'emboss')

		for record in ndl:
			query_id = record._records[0].id
			subject_id = record._records[1].id
			aln_length = len(record._records[0])
			prc_identity = record.annotations['identity'] / aln_length
			prc_similarity = record.annotations['similarity'] / aln_length
			gaps = record.annotations['gaps']
			score = record.annotations['score']

			stats = [query_id, subject_id, aln_length, prc_identity, prc_similarity,
				gaps, score]
			line = [str(n) for n in stats]
			sys.stdout.write('\t'.join(line) + '\n')
