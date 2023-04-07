#!/bin/bash

#SBATCH --job-name=cmsearch
#SBATCH --time=2:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --partition pi_breaker

module load Infernal

sto="$1"
out="$2"
E="$3"
incE="$4"
DBFNA="$5"

me=$(basename "$0"); function log () { echo "$me: $*" >&2; }

# Build a covariance model from a Stockholm alignment file.
if [ ! -f "$sto.cm" ]; then
    log "Building covariance model at $sto.cm."
    cmbuild "$sto.cm" "$sto"
    cmcalibrate "$sto.cm"
fi

# Search covariance model against sequence database.
log "Running cmsearch for $sto.cm with (E=$E, incE=$incE, DBFNA=$DBFNA)."
log "Output will be written to $out."
cmsearch -o "$out" -A "$out.sto" --tblout "$out.tbl" -E "$E" --incE "$incE" "$sto.cm" "$DBFNA"
