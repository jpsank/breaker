#!/bin/bash

#SBATCH --job-name=refold
#SBATCH --time=1:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --partition pi_breaker

export PATH="$PATH:/gpfs/gibbs/pi/breaker/software/bin/cmfinder.pl"
# export PATH="$PATH:/gpfs/gibbs/pi/breaker/software/packages/cmfinder-0.4.1.18/bin"
export CMfinder="/gpfs/gibbs/pi/breaker/software/packages/cmfinder-0.4.1.18"

module load Infernal
module load HMMER

OUTDIR="data/refold"
if [ ! -d $OUTDIR ]; then
    mkdir $OUTDIR 
fi

# Reformat the stockholm files into fasta files and run cmfinder on them
esl-reformat fasta "data/analysis/data/DUF1646.uniq.keepE1.sto" > "$OUTDIR/DUF1646.fna"
esl-reformat fasta "data/analysis/data/nhaA-I.uniq.keepE1.sto" > "$OUTDIR/nhaA-I.fna"
/gpfs/gibbs/pi/breaker/software/bin/cmfinder.pl --combine "$OUTDIR/DUF1646.fna"
/gpfs/gibbs/pi/breaker/software/bin/cmfinder.pl --combine "$OUTDIR/nhaA-I.fna"

# Cat the fasta files together to make a combined fna file, then run cmfinder on it
# cat "$OUTDIR/DUF1646.fna" "$OUTDIR/nhaA-I.fna" > "$OUTDIR/DUF1646_nhaA-I.fna"
/gpfs/gibbs/pi/breaker/software/bin/cmfinder.pl --combine "$OUTDIR/lina-combo.fna"

# R2R aliases
function r2r-mkcons {
	# Usage: r2r-mkcons <name>.sto
    r2r --GSC-weighted-consensus "$1" "${1%sto}cons.sto" \
        3 0.97 0.9 0.75 4 0.97 0.9 0.75 0.5 0.1
}

function r2r-mkpdf-cons {
	# Usage: r2r-mkpdf-cons <name>.cons.sto
    r2r --disable-usage-warning "$1" "${1%cons.sto}pdf"
}

function r2r-mkpdf-meta {
	# Usage: r2r-mkpdf-meta <name>.r2r_meta
    r2r --disable-usage-warning "$1" "${1%r2r_meta}pdf"
}

# Run r2r on the stockholm files
function r2r() {
    local path=$1
    r2r-mkcons "$path.sto"
    r2r-mkpdf-cons "$path.cons.sto"
}

FILES="$OUTDIR/*.fna.motif.h2_1"
for f in $FILES; do
    r2r "$f"
done
