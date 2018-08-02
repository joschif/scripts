import sys
import argparse
from Bio import SeqIO
from Bio.SeqUtils.ProtParam import ProteinAnalysis

# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Extract sequences from a FASTA [.fasta/.fa(.gz)] file if their identifier is in a <WANTED> file. Wanted file contains one sequence identifier per line.")

    parser.add_argument('FASTA',
                        type=str,
                        metavar='<FASTA>',
                        help='(Multi-) FASTA file [.fasta/.fa(.gz)]')

    parser.add_argument('-o', '--output-file',
                        dest='out_file',
                        type=argparse.FileType("w"),
                        default=sys.stdout,
                        nargs="?",
                        metavar='<output-file>',
                        help='Prefix for the output file. If given, all lines are written to this file.')

    args = parser.parse_args()
    return args

# MAIN
if __name__ == "__main__":
    args = interface()
    fasta_file = args.FASTA
    out_file = args.out_file

    fasta = SeqIO.parse(fasta_file, "fasta")

    header= ["protein_id", "MW", "aromaticity", "II", "GRAVY", "pI", "helix", "turn", "sheet",
        "extinction"]
    out_file.write("\t".join(header) + "\n")

    for rec in fasta:
        sequence = (str(rec.seq).replace("*", "").replace("X", "").replace("J", "L")
            .replace("B", "N").replace("Z", "Q").replace("U", "C"))
        ID = rec.id.split("|")[-1]
        anal = ProteinAnalysis(sequence)
        mw = anal.molecular_weight()
        aro = anal.aromaticity()
        insta = anal.instability_index()
        grev = anal.gravy()
        ie = anal.isoelectric_point()
        sec = anal.secondary_structure_fraction()
        helix = sec[0]
        turn = sec[1]
        sheet = sec[2]
        ext = anal.molar_extinction_coefficient()[0]
        row = [ID, mw, aro, insta, grev, ie, helix, turn, sheet, ext]
        row = [str(n) for n in row]
        out_file.write("\t".join(row) + "\n")
