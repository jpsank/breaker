#!/bin/bash

module load Infernal
module load HMMER

sto="$1"
fna="$2"

esl-reformat fasta "$sto" > "$fna"
