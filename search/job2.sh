#!/bin/bash

#SBATCH --job-name=gtdb-bact_search_nhaA-I
#SBATCH --time=2:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8

module load Inferno

./search.sh sto/nhaA-I/RF03057.sto "gtdb-bact_nhaA-I_1" ./gtdb/gtdb-bact-r207-repr.fna.gz 100.0 0.01
