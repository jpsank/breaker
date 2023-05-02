#!/bin/bash

#SBATCH --job-name=cmsearch
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --partition pi_breaker

module load Infernal

cm="$1"             # Covariance model
out="$2"            # Output file prefix
target="$3"         # Database to search against
param=( "${@:4}" )  # ex: -E XXXX --incE XXXX

# Search covariance model against sequence database.
cmsearch -o "$out" -A "$out.sto" --tblout "$out.tbl" "${param[@]}" "$cm" "$target"
