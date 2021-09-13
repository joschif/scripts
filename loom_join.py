import os
import sys
import argparse
import numpy as np
import pandas as pd
import scanpy as sc
import loompy as lp
import anndata as ad

# CONST
MAPPING_DIR = os.path.expanduser('~/resources/mappings/')
ENS2SYM = os.path.join(MAPPING_DIR, 'ens2sym.tsv')

# FUNC
def interface():
    parser = argparse.ArgumentParser(description='Joins loom files.')

    parser.add_argument('LOOM_FILES',
                        type=str,
                        nargs='+',
                        metavar='<LOOM_FILES>',
                        help='Loom file.')

    parser.add_argument('-o', '--out_loom',
                        default='joined.loom',
                        type=str,
                        metavar='<f>',
                        help='Output LOOM.')

    parser.add_argument('-i', '--sample-ids',
                        dest='ids',
                        type=str,
                        nargs='+',
                        help='Sample IDs to add to cell barcode.')

    parser.add_argument('--limit_genes',
                        action='store_true',
                        help='Whether to limit genes.')

    args = parser.parse_args()
    return args

# MAIN
if __name__ == '__main__':
    args = interface()

    if args.ids:
        assert len(args.ids) == len(args.LOOM_FILES), 'Length of IDs must be the same as the number of LOOM files'
    else:
        args.ids = [f'SAMPLE_{i}' for i in range(len(args.LOOM_FILES))]

    ens2sym = pd.read_csv(ENS2SYM, sep='\t')

    adata_list = list()
    for name, loom in zip(args.ids, args.LOOM_FILES):
        sys.stdout.write(f'Reading {name}\n')
        adata = sc.read_loom(loom)
        adata.obs['batch'] = name
        adata.var_names_make_unique()
        if args.limit_genes:
            genes_use = list(set(adata.var.index) & set(ens2sym['symbol'].values))
            adata = adata[:, genes_use]
        adata_list.append(adata)

    sys.stdout.write(f'Joining samples\n')
    adata_joined = adata_list[0].concatenate(*adata_list[1:], index_unique=None)
    sys.stdout.write(f'Writing\n')
    adata_joined.write_loom(args.out_loom)
