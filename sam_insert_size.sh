#!/bin/bash

SAM_FILE=$1

head -100000 $SAM_FILE | awk '{ if ($9 > 0) { N+=1; R+=length($10); I+=$9-(2*length($10)); R2+=length($10)*length($10); I2+=($9-(2*length ($10)))*($9-(2*length ($10))) }} END { MR=R/N; MI=I/N; SR=sqrt ((R2-MR*MR*N)/(N-1)); SI=sqrt ((I2-MI*MI*N)/(N-1)); print "Sampled n="N" reads -> \n READ: mean="MR", stdev="SR" \n INSERT: mean="MI", stdev="SI}'