#!/bin/bash

export PATH="$PATH:/gpfs/gibbs/pi/breaker/software/bin/cmfinder.pl"
export CMfinder="/gpfs/gibbs/pi/breaker/software/packages/cmfinder-0.4.1.18"

module load Infernal

name1="./analysis/DUF1646.uniq.keepE1"
esl-reformat fasta "$name1.sto" > "$name1.fna"
./cmfinder.pl -def "$name1.fna"

name2="./analysis/nhaA-I.uniq.keepE1"
esl-reformat fasta "$name2.sto" > "$name2.fna"
./cmfinder.pl -def "$name2.fna"
