#!/bin/bash

#SBATCH --job-name=gtdb-bact_search_DUF1646
#SBATCH --time=2:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8

module load Inferno

./search.sh sto/DUF1646/RF03071.sto "gtdb-bact_DUF1646_1" ./gtdb/gtdb-bact-r207-repr.fna.gz 100.0 0.01
