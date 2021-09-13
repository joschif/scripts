import os
import sys
import argparse


# FUNC
def interface():
    parser = argparse.ArgumentParser(description='Merges fragment files from scATAC experiments.')

    parser.add_argument('FRAGMENTS',
                        type=str,
                        nargs='+',
                        metavar='<FRAGMENTS>',
                        help='Fragment files.')

    parser.add_argument('-o',
                        dest='OUT',
                        default='fragments',
                        type=str,
                        metavar='<OUT>',
                        help='Output file basename.')

    parser.add_argument('-p', '--prefix',
                        dest='prefix',
                        type=str,
                        nargs='+',
                        metavar='<str>',
                        help='Prefixes for cell IDs.')

    parser.add_argument('-c', '--cpus',
                        dest='cpus',
                        default=1,
                        type=int,
                        metavar='<int>',
                        help='Number of cpus.')

    args = parser.parse_args()
    return args

def add_prefix(fragments_file, prefix):
    fragments_base = os.path.splitext(fragments_file)[0]
    cmd = f'gzip -dc {fragments_file} '
    cmd += '| awk \'BEGIN {FS=OFS="\t"} {print $1,$2,$3,"'
    cmd += prefix
    cmd += '_"$4,$5}\' - > '
    cmd += fragments_base
    sys.stdout.write(cmd + '\n')
    os.system(cmd)
    return fragments_base

def merge_fragments(fragments_files, merged_file):
    cmd = 'sort -m -k 1,1V -k2,2n '
    cmd += ' '.join(fragments_files)
    cmd += f' > {merged_file}'
    sys.stdout.write(cmd + '\n')
    os.system(cmd)

# MAIN
if __name__ == '__main__':
    args = interface()

    # Make sure prefixes and files match
    assert len(args.FRAGMENTS) == len(args.prefix), \
        'Number of prefixes must match the number of fragment files.'

    # Add prefixes to all fragments files
    new_files = list()
    for pfx, frag in zip(args.prefix, args.FRAGMENTS):
        new_file = add_prefix(frag, pfx)
        new_files.append(new_file)

    # Merge to single file
    merged_file = f'{args.OUT}.tsv'
    merge_fragments(new_files, merged_file)

    # Block gzip
    cmd = f'bgzip -@ {args.cpus} {merged_file}'
    sys.stdout.write(cmd + '\n')
    os.system(cmd)

    # Index gzipped file
    cmd = f'tabix -p bed {merged_file}.gz'
    sys.stdout.write(cmd + '\n')
    os.system(cmd)

    # Remove intermediates
    for tmp in new_files:
        os.remove(tmp)
