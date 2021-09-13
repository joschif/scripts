#!/usr/bin/env python

import argparse
import sys
import gzip
import numpy as np
import re

DEFAULTS = {
    'only_homo': False
}


def interface():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'annot',
        help='The string of group annotations, with individuals separated by comma (e.g. A,A,B,B)'
    )
    parser.add_argument(
        'vcffile',
        help='The VCF file (- for STDIN)'
    )
    parser.add_argument(
        '--homo',
        dest='only_homo',
        action='store_true',
        default=DEFAULTS['only_homo'],
        help='Only consider the variant sites with all lines homogeneous'
    )
    parser.add_argument(
        '--allow-unknown',
        dest='allow_unknown',
        action='store_true',
        help='Allow unknown sites within lines.'
    )
    parser.add_argument(
        '--filter-identical',
        dest='filter_identical',
        action='store_true',
        help='Filter sites that are identical across lines.'
    )

    args = parser.parse_args()
    return(args)


if __name__ == '__main__':
    args = interface()

    # Field annotation
    annot = np.array(args.annot.split(','))

    # Open vcf file
    fileopen = gzip.open if args.vcffile.endswith('.gz') else open
    fh = fileopen(args.vcffile) if args.vcffile != '-' else sys.stdin

    # Read vcf file
    for line in fh:
        line = line.rstrip()

        # Write out information header
        if line.startswith('##'):
            sys.stdout.write(line + '\n')
            continue

        elem = line.split('\t')

        # Format and write header
        if line.startswith('#'):
            header = elem[:9]
            for g in np.unique(annot):
                header.append(g)
            sys.stdout.write('\t'.join(header) + '\n')
            continue

        gt_format = elem[8].split(':')
        GT_idx = np.where(np.array(np.array(gt_format) == 'GT'))[0]
        if np.size(GT_idx) != 1:
            continue
        GT_idx = GT_idx.tolist()[0]

        genotypes = np.array([])
        is_homo = np.array([])
        for info in elem[9:]:
            # gt = info.split(':')[GT_idx].split('/')
            gt = re.split(r'/|\|', info.split(':')[GT_idx])
            genotypes = np.append(genotypes, '/'.join(gt))
            is_homo = np.append(is_homo, gt[0] == gt[1])

        consistent_genotypes = True
        unknown_genotypes = False
        has_unknown = False
        line_genotypes = list()
        for a in np.unique(annot):
            annot_idx = np.where(annot == a)[0]
            annot_gt = genotypes[annot_idx]
            if np.all(annot_gt == './.'):
                unknown_genotypes = True
                break
            if np.any(annot_gt == './.'):
                annot_gt = annot_gt[annot_gt != './.']
                has_unknown = True
            if np.unique(annot_gt).size > 1:
                consistent_genotypes = False
                break
            line_genotypes.append(np.unique(annot_gt)[0])

        # Skip sites with different genotypes in different replicates of the same line
        if not consistent_genotypes or unknown_genotypes:
            continue

        # Skip if any line has unknown sites and not allow_unknown
        if has_unknown and not args.allow_unknown:
            continue

        # Skip sites with the same genotype in all lines
        if np.unique(np.array(line_genotypes)).size <= 1 and args.filter_identical:
            continue

        # Skip if only_homo==True and any line is heterozygous
        if args.only_homo and np.sum(is_homo) != np.size(is_homo):
            continue

        output = elem[:8] + ['GT'] + line_genotypes
        sys.stdout.write('\t'.join(output) + '\n')

    fh.close()
