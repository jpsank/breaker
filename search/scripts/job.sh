#!/bin/bash

#SBATCH --job-name=gtdb-prok_search_DUF1646
#SBATCH --time=2:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --partition pi_breaker

module load Infernal

# Logging function.
me=$(basename "$0"); function log () { echo "$me: $*" >&2; }

# Hyperparameters.
OUTDIR=data/searches
DBFNA=gtdb/gtdb-bact-r207-repr.fna.gz  # On the cluster, this is a symlink to the database.
E=1000.0     # default 100
incE=1000.0  # default 0.01

# Search function.
function search () {
    local sto=$1
    local name=$2

    # Build a covariance model from a Stockholm alignment file.
    if [ ! -f "$sto.cm" ]; then
        log "Covariance model $sto.cm not found, building..."
        cmbuild "$sto.cm" "$sto"
        cmcalibrate "$sto.cm"
        log "Built $sto.cm."
    else
        log "Found covariance model $sto.cm."
    fi

    # Select a new folder for the output.
    idx=1
    while [ -d "$OUTDIR/${name}_$idx" ]; do
        idx=$((idx+1));
    done
    mkdir "$OUTDIR/${name}_$idx"
    out="$OUTDIR/${name}_$idx/${name}_$idx.out"

    # Search covariance model against sequence database.
    log "Searching $sto.cm in $DBFNA with E=$E, incE=$incE..."
    cmsearch -o "$out" -A "$out.sto" --tblout "$out.tbl" -E "$E" --incE "$incE" "$sto.cm" "$DBFNA"

    log "Finished, output in $out."
}

search data/sto/DUF1646/RF03071.sto "gtdb-prok_DUF1646"
search data/sto/nhaA-I/RF03057.sto "gtdb-prok_nhaA-I"

