#!/bin/bash

#SBATCH --job-name=cmfinder
#SBATCH --time=1:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --partition pi_breaker

module load Infernal
module load HMMER

# Set up environment variables
export PATH="$PATH:/gpfs/gibbs/pi/breaker/software/bin/cmfinder.pl"
export CMfinder="/gpfs/gibbs/pi/breaker/software/packages/cmfinder-0.4.1.18"

# Run cmfinder
fna="$1"
/gpfs/gibbs/pi/breaker/software/bin/cmfinder.pl --combine "$fna"

