#!/bin/bash

sto="$1"
fna="$2"

esl-reformat fasta "$sto" > "$fna"
