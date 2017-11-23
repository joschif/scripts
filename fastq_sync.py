#!/usr/bin/env python

# Shamelessly stolen and modified from @enormandeau (https://github.com/enormandeau)

import sys
import argparse
import gzip


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
    parser = argparse.ArgumentParser(description='Takes two FASTQ [.fq(.gz)] files and synchronizes them. Returns synchronized pairs <output_prefix>_pairs_1.fq(.gz) and <output_prefix>_pairs_2.fq(.gz) as well as a single <output_prefix>_singles.fq(.gz)')

    parser.add_argument('READS_1',
                        type=str,
                        metavar='<READS_1>',
                        help='R1 reads in FASTQ format [.fq(.gz)].')

    parser.add_argument('READS_2',
                        type=str,
                        metavar='<READS_2>',
                        help='R2 reads in FASTQ format [.fq(.gz)].')
 
    parser.add_argument('-s', '--separator',
                        dest='sep',
                        default='/',
                        type=str,
                        metavar='<sep>',
                        help='Separator for unique indentifier.')     

    parser.add_argument('-l', '--min-length',
                        dest='min',
                        default=30,
                        type=int,
                        metavar='<min-length>',
                        help='Minimum length filter for reads.')     

    parser.add_argument('-i', '--interleaved',
                        dest='interleaved',
                        action='store_true',
                        help='Use this switch to interleave the files.')

    # parser.add_argument('-g', '--gzip',
    #                     dest='compress',
    #                     action='store_true',
    #                     help='Use this switch to force compression of the output.') 

    parser.add_argument('-o', '--output-prefix',
                        dest='out',
                        type=str,
                        default='reads',
                        metavar='<output_prefix>',
                        help='Prefix for the output file.')

    args = parser.parse_args()
    return args


def both_valid(fq1, fq2, l):
    """Takes two paired Fastq sequences files and checks if both are valid
    """

    return fq1.len >= l and fq2.len >= l


def open_gz(infile, mode="rt"):
    """Takes input and uncompresses gzip if needed
    """

    if infile.endswith(".gz"):
        return gzip.open(infile, mode=mode)
    else:
        return open(infile, mode=mode)


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


# MAIN
if __name__ == "__main__":
    args = interface()
    first = args.READS_1
    second = args.READS_2
    out_prefix = args.out
    separator = args.sep
    interleaved = args.interleaved
    min_len = args.min
    # compress = args.compress

    seq1_dict = {}
    seq2_dict = {}
    seq1 = fastq_parser(first)
    seq2 = fastq_parser(second)
    s1_finished = False
    s2_finished = False

    if first.endswith('.gz'): 
        out_suffix='.fq.gz'
    else:
        out_suffix='.fq'

    count_valid = 0
    count_invalid = 0
    count_single = 0

    if not interleaved:
        with open_gz(out_prefix + "_pairs_1" + out_suffix, "wt") as out1:
            with open_gz(out_prefix + "_pairs_2" + out_suffix, "wt") as out2:
                with open_gz(out_prefix + "_singles" + out_suffix, "wt") as out3:
                    while not (s1_finished and s2_finished):
                        try:
                            s1 = next(seq1)
                            s1_name = s1.get_shortname(separator)
                        except:
                            s1_finished = True
                        try:
                            s2 = next(seq2)
                            s2_name = s2.get_shortname(separator)
                        except:
                            s2_finished = True

                        # Add new sequences to hashes
                        if not s1_finished:
                            seq1_dict[s1_name] = s1
                        if not s2_finished:
                            seq2_dict[s2_name] = s2

                        if not s1_finished and s1_name in seq2_dict:
                            if both_valid(seq1_dict[s1_name], seq2_dict[s1_name], min_len):
                                count_valid += 1
                                seq1_dict[s1_name].write_to_file(out1)
                                seq1_dict.pop(s1_name)
                                seq2_dict[s1_name].write_to_file(out2)
                                seq2_dict.pop(s1_name)
                            else:
                                count_invalid += 1
                                seq1_dict.pop(s1_name)
                                seq2_dict.pop(s1_name)

                        if not s2_finished and s2_name in seq1_dict:
                            if both_valid(seq1_dict[s2_name], seq2_dict[s2_name], min_len):
                                count_valid += 1
                                seq1_dict[s2_name].write_to_file(out1)
                                seq1_dict.pop(s2_name)
                                seq2_dict[s2_name].write_to_file(out2)
                                seq2_dict.pop(s2_name)
                            else:
                                count_invalid += 1
                                seq1_dict.pop(s2_name)
                                seq2_dict.pop(s2_name)

                    # Treat all unpaired reads
                    for r in seq1_dict.values():
                        count_single += 1
                        r.write_to_file(out3)

                    for r in seq2_dict.values():
                        count_single += 1
                        r.write_to_file(out3)

    else:         
        with open_gz(out_prefix + "_pairs_interleaved" + out_suffix, "wt") as out:
            with open_gz(out_prefix + "_singles" + out_suffix, "wt") as out3:
                while not (s1_finished and s2_finished):
                    try:
                        s1 = next(seq1)
                        s1_name = s1.get_shortname(separator)
                    except:
                        s1_finished = True
                    try:
                        s2 = next(seq2)
                        s2_name = s2.get_shortname(separator)
                    except:
                        s2_finished = True

                    # Add new sequences to hashes
                    if not s1_finished:
                        seq1_dict[s1_name] = s1
                    if not s2_finished:
                        seq2_dict[s2_name] = s2

                    if not s1_finished and s1_name in seq2_dict:
                        if both_valid(seq1_dict[s1_name], seq2_dict[s1_name], min_len):
                            count_valid += 1
                            seq1_dict[s1_name].write_to_file(out)
                            seq1_dict.pop(s1_name)
                            seq2_dict[s1_name].write_to_file(out)
                            seq2_dict.pop(s1_name)
                        else:
                            count_invalid += 1
                            seq1_dict.pop(s1_name)
                            seq2_dict.pop(s1_name)

                    if not s2_finished and s2_name in seq1_dict:
                        if both_valid(seq1_dict[s2_name], seq2_dict[s2_name], min_len):
                            count_valid += 1
                            seq1_dict[s2_name].write_to_file(out)
                            seq1_dict.pop(s2_name)
                            seq2_dict[s2_name].write_to_file(out)
                            seq2_dict.pop(s2_name)
                        else:
                            count_invalid += 1
                            seq1_dict.pop(s2_name)
                            seq2_dict.pop(s2_name)

                # Treat all unpaired reads
                for r in seq1_dict.values():
                    count_single += 1
                    r.write_to_file(out3)

                for r in seq2_dict.values():
                    count_single +=1
                    r.write_to_file(out3)
