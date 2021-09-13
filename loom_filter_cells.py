import os
import sys
import argparse
import numpy as np
import pandas as pd
import scanpy as sc
import loompy as lp
import anndata as ad

# FUNC
def interface():
    parser = argparse.ArgumentParser(description='Joins loom files.')

    parser.add_argument('LOOM',
                        type=str,
                        metavar='<LOOM>',
                        help='Loom file.')

    parser.add_argument('-o', '--out_loom',
                        default='filtered.loom',
                        type=str,
                        metavar='<f>',
                        help='Output LOOM.')

    parser.add_argument('-c', '--cell-ids',
                        dest='cells',
                        type=str,
                        metavar='<f>',
                        help='Cell ids to subset.')

    args = parser.parse_args()
    return args

# MAIN
if __name__ == '__main__':
    args = interface()

    sys.stdout.write(f'Reading\n')
    adata = sc.read_loom(args.LOOM)
    with open(args.cells, 'rt') as f:
        cells_use = pd.Series([l.strip() for l in f.readlines()])

    inter_cells = adata.obs.index[adata.obs.index.isin(cells_use)]
    sys.stdout.write(f'Found {len(inter_cells)} intersecting cells\n')

    sys.stdout.write(f'Filtering cells\n')
    adata = adata[inter_cells, :]

    sys.stdout.write(f'Writing\n')
    adata.write_loom(args.out_loom)
