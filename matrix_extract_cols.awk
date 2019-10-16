# awk -F "\t" -v tgt="sample_1" -f ~/scripts/helper/matrix_extract_cols.awk matrix.mtx

NR==1 {
    for (i=1;i<=NF;i++) {
        if ( (tgt == "") || ($i !~ tgt) ) {
            f[++nf] = i
        }
    }
}
{
    for (i=1; i<=nf; i++) {
        printf "%s%s", $(f[i]), (i<nf?OFS:ORS)
    }
}
