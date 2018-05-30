#!/bin/bash

ID_LIST=$1
FASTA=$2
OUT=$3

cat $ID_LIST | while read ID;
    do
        echo "Looking up $ID"
        perl -ne 'if (/^>(\w+\.\w+)\..*/){ $match = grep{ /$1/ } "'$ID'" } print if $match;' $FASTA > $OUT/$ID.fa
    done
