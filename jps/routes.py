"""
routes.py
"""

from dataclasses import dataclass, field
from collections import defaultdict
import pandas
from pyfaidx import Fasta
from sqlalchemy import select
from tabulate import tabulate
import sys
import os
import subprocess

from jps.util.slurm import shexecute
import jps.util.tblio as tblio
import jps.util.iosto as iosto
from jps.analyze import plot_score_distribution
from jps.models import *
from jps.util.helpers import *
from cgk.interval import ChrInterval


CMSEARCH_TBLHEADERS = ['target_name', 'target_accession', 'query_name', 'query_accession', 
                       'mdl', 'mdl_from', 'mdl_to', 'seq_from', 'seq_to', 'strand', 'trunc', 
                       'pass_', 'gc', 'bias', 'score', 'E_value', 'inc', 'description_of_target']


def cmbuild_submit(sto: str, out: str = None):
    """ Submit a cmbuild job. """
    return SlurmJob.submit(os.path.join(SCRIPTS_DIR, 'cmbuild.sh'), fullpath(sto), fullpath(out))


def cmsearch_submit(cm: str, param: str, target: str):
    search = Search(cm=cm, param=param, target=target)

    # Create search directory
    os.makedirs(os.path.dirname(fullpath(search.datapath)), exist_ok=True)

    # Submit search job
    search.job = SlurmJob.submit(
        os.path.join(SCRIPTS_DIR, 'cmsearch.sh'), 
        fullpath(search.cm), fullpath(search.datapath), search.target, search.param)
    
    return search


def cmsearch_parse(search: Search):
    """ Parse cmsearch results into a list of Hit objects. """

    # Parse Stockholm and table files
    sequences, features = iosto.sto_read(f"{fullpath(search.datapath)}.sto")
    rows = tblio.tbl_read(f"{fullpath(search.datapath)}.tbl", headers=CMSEARCH_TBLHEADERS)
    rows = dict(zip(CMSEARCH_TBLHEADERS, rows))

    with SessionLocal() as session:
        # Create Stockholm database entry
        sto = Stockholm(datapath=f"{search.datapath}.sto")
        
        # Create Alnseq database entries
        esltag_to_id = defaultdict(int)
        for esltag, seq in sequences.items():
            alnseq = Alnseq(alnseq=seq.alnseq)
            esltag_to_id[esltag] = alnseq.id
            sto.alnseqs.append(alnseq)
        
        # Create Feature database entries
        for feat in features:
            feature = StoFeature(
                alnseq_id=esltag_to_id[feat.esltag], fmt=feat.fmt, field=feat.field, text=feat.text)
            sto.features.append(feature)
        
        session.add(sto)

        # Create hits from table
        for i, row in enumerate(rows):
            start, end = int(row['seq_from']), int(row['seq_to'])
            if (strand := row['strand']) == '-':
                start, end = end, start
            hit = Hit(
                search=search, rank=i,
                chraccn=row['target_name'], start=start, end=end, strand=strand,
                evalue=row['E_value'], bitscore=row['score'], bias=row['bias'], gc=row['gc'],
                trunc=row['trunc'], mdl_from=row['mdl_from'], mdl_to=row['mdl_to'])
            if hit.esltag in esltag_to_id:
                hit.alnseq_id = esltag_to_id[hit.esltag]
            search.hits.append(hit)
        
        session.commit()


def runr2r(sto: str):
    """ Run R2R on a Stockholm file. """
    try:
        for line in shexecute([os.path.join(SCRIPTS_DIR, 'r2r.sh'), sto]):
            print(line, end="")
    except subprocess.CalledProcessError:
        print("R2R failed to run, skipping...", file=sys.stderr)


def cmsearch_analyze(search: Search, color, threshold=0.01):
    outdir = os.path.join(ANALYSIS_DIR, search.name)
    os.makedirs(outdir, exist_ok=True)

    # Filter out duplicate hits
    unique = search.hits.distinct(Hit.alnseq.alnseq)

    # Plot score distribution
    plot_score_distribution(unique.all(), search.name, color, 
                        out=os.path.join(outdir, f"{search.name}_score_distribution.png"), threshold=threshold)
    
    # Filter hits by threshold
    keep = search.hits.filter(Hit.evalue <= threshold)
    keep_unique = unique.filter(Hit.evalue <= threshold)

    # Write counts table
    with open(os.path.join(ANALYSIS_DIR, f"{search.name}.counts.txt"), 'w') as f:
        table = [
            ["Name", "# Total", "# Unique", f"# E<{threshold}", f"# Unique E<{threshold}"],
            [search.name, search.hits.count(), unique.count(), keep.count(), keep_unique.count()]
        ]
        f.write(tabulate(table, headers="firstrow", tablefmt="plain"))
    
    
    os.makedirs(datadir := os.path.join(outdir, "data"), exist_ok=True)
    iosto.sto_write(unique.all(), os.path.join(datadir, f"{search.name}.uniq.sto"))
    iosto.sto_write(keep.all(), os.path.join(datadir, f"{search.name}.keepE{slugify_float(threshold)}.sto"))
    iosto.sto_write(keep_unique.all(), keep_uniq_path := os.path.join(datadir, f"{search.name}.uniq.keepE{slugify_float(threshold)}.sto"))

    # Run R2R
    runr2r(keep_uniq_path)

    return keep_uniq_path


def sto_reformat(sto: str, out: str):
    """ Reformat a stockholm alignment file. """
    for line in shexecute([os.path.join(SCRIPTS_DIR, 'reformat.sh'), sto, out]):
        print(line, end="")


def run_cmfinder(fna: str):
    """ Run CMfinder on a FASTA file. """
    return SlurmJob.submit(os.path.join(SCRIPTS_DIR, 'cmfinder.sh'), fna)

    # Expected path to CMfinder output: f"{fna}.motif.h2_1"


def pipeline(sto: str, e: float = 1000.0):
    """ Run the entire pipeline on a stockholm alignment file. """
    # Run cmbuild/cmcalibrate
    with SessionLocal() as session:
        job1 = cmbuild_submit(sto, cm := f"{sto}.cm")
        session.add(job1)
    job1.wait()

    # Run cmsearch
    with SessionLocal() as session:
        search = cmsearch_submit(cm, f"-E {e} --incE {e}", GTDB_PROK_DB)
        session.add(search)
    search.job.wait()
    cmsearch_parse(search)

    # Run cmsearch analysis
    keep_uniq_sto = cmsearch_analyze(search, color='DarkBlue')

    # Run reformat
    sto_reformat(keep_uniq_sto, keep_uniq_fna := os.path.join(REFOLD_DIR, search.name, f"{sto}.fna"))

    # Run cmfinder
    job2 = run_cmfinder(keep_uniq_fna)
    job2.wait()
    motif_sto = f"{keep_uniq_fna}.motif.h2_1"

    # Run r2r on new motif
    runr2r(motif_sto)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pipe.py <sto file>")
        sys.exit(1)
    sto = sys.argv[1]
    if not os.path.exists(sto):
        print(f"sto file {sto} does not exist")
        sys.exit(1)
    
    # Run pipeline
    pipeline(sto)


# def select_overlapping_hits():
#     overlapping = select((Hit, Hit)).where(
#         Hit.chraccn == Hit.chraccn,
#         Hit.start <= Hit.end,
#         Hit.end >= Hit.start,
#     )
#     return overlapping

# def select_tandems():
#     """ Select tandem hits. """
#     # tandem = select((Hit, Hit, 'distance')).where(
#     #     Hit.chraccn == Hit.chraccn,
#     # ).order_by(
#     #     Hit.chraccn, Hit.start, Hit.end
#     # ).having(
#     #     'distance < 1000'
#     # )
#     # return tandem

