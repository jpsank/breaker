#!/bin/bash

#SBATCH --job-name=gtdb-prok_search_DUF1646
#SBATCH --time=2:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --partition pi_breaker

module load Infernal

# Logging function.
me=$(basename "$0")
function log () {
    echo "$me: $*" >&2
}

# Search function.
OUTDIR=./searches
function search () {
    local sto=$1
    local name=$2
    local dbfna=$3
    local E=$4     # 100
    local incE=$5  # 0.01

    # Build a covariance model from a Stockholm alignment file.
    if [ ! -f "$sto.cm" ]; then
        log "Covariance model $sto.cm not found, building..."
        cmbuild "$sto.cm" "$sto"
        cmcalibrate "$sto.cm"
        log "Built $sto.cm."
    else
        log "Found covariance model $sto.cm."
    fi

    # Select a folder for the output.
    idx=1
    while [ -d $OUTDIR/"${name}_$idx" ];
        do idx=$((idx+1));
    done
    name="${name}_$idx"
    mkdir "$OUTDIR/$name"
    out="$OUTDIR/$name/$name.out"
    log "Output will be in $out."

    # Search covariance model against sequence database.
    log "Searching $sto.cm in $dbfna with E-value = $E and inclusion threshold = $incE..."
    cmsearch -o "$out" -A "$out.sto" --tblout "$out.tbl" -E "$E" --incE "$incE" "$sto.cm" "$dbfna"

    log "Finished."
}

dbfna=../gtdb/gtdb-bact-r207-repr.fna.gz
search sto/DUF1646/RF03071.sto "gtdb-prok_DUF1646" $dbfna 1000.0 1000.0
search sto/nhaA-I/RF03057.sto "gtdb-prok_nhaA-I" $dbfna 1000.0 1000.0

