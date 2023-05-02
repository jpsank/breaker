#!/bin/bash

#SBATCH --job-name=cmbuild
#SBATCH --time=0:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --partition pi_breaker

module load Infernal

sto="$1"
out="$2:-$sto.cm"

# Build a covariance model from a Stockholm alignment file.
if [ ! -f "$out" ]; then
    cmbuild "$out" "$sto"
    cmcalibrate "$out"
fi
