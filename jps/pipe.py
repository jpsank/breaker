import subprocess
from datetime import datetime
import sys

from config import *
from jps.analyze import *
from jps.slurm import *
from jps.util import *


def cmsearch(sto, out=None, e=1000.0, dbfna=GTDB_PROK_DB):
    """
    Run a cmsearch on a stockholm alignment file. 

    Args:
        sto (str): path to stockholm alignment file
        out (str): path to output file
        e (float): E-value threshold and cutoff
        dbfna (str): path to database FASTA file
    """

    # Auto-generate output path
    if out is None:
        name = f"{sto_filename(sto)}_{datetime.now().strftime('%m-%d-%Y_%H:%M:%S')}"
        out = os.path.join(name, f"{name}.out")
        os.makedirs(out, exist_ok=True)
    
    # Run cmsearch
    job = SlurmJob.submit(os.path.join(SCRIPTS_DIR, 'cmsearch.sh'), sto, out, str(e), str(e), dbfna)
    job.wait()

    return out


def analyze(cmsearch_out, name=None, color="DarkBlue", threshold=1.0):
    """
    Run analysis on a cmsearch output file.

    Args:
        cmsearch_out (str): path to cmsearch output file
        color (str): color to use for analysis
        threshold (float): threshold for E-value cutoff
    """
    # Decode cmsearch output path to make analysis output path
    name = os.path.splitext(os.path.basename(cmsearch_out))[0] if name is None else name
    outdir = os.path.join(ANALYSIS_DIR, name)
    os.makedirs(outdir, exist_ok=True)

    # Parse cmsearch output and run analysis
    sr = SearchResult.parse(cmsearch_out)
    uniq_keep_path = run_analysis(sr, name, color, outdir, threshold)

    # Run R2R
    for line in execute([os.path.join(SCRIPTS_DIR, 'r2r.sh'), f"{uniq_keep_path}.sto"]):
        print(line, end="")
    
    return uniq_keep_path


def reformat(sto, out=None):
    """
    Reformat a stockholm alignment file.

    Args:
        sto (str): path to stockholm alignment file
        out (str): path to output file
    """
    # Auto-generate output path
    if out is None:
        name = sto_filename(sto)
        out = os.path.join(REFOLD_DIR, name, f"{name}.fna")
        os.makedirs(os.path.dirname(out), exist_ok=True)

    # Run reformat
    for line in execute([os.path.join(SCRIPTS_DIR, 'reformat.sh'), sto, out]):
        print(line, end="")
    
    return out


def cmfind(fna):
    """
    Run CMfinder on a FASTA file.

    Args:
        fna (str): path to FASTA file
    """
    # Run CMfinder
    job = SlurmJob.submit(os.path.join(SCRIPTS_DIR, 'cmfinder.sh'), fna)
    job.wait()
        
    # Return expected path to CMfinder output (could be wrong)
    return f"{fna}.motif.h2_1"


def r2r(sto):
    """
    Run R2R on a stockholm alignment file.

    Args:
        sto (str): path to stockholm alignment file
    """
    for line in execute([os.path.join(SCRIPTS_DIR, 'r2r.sh'), sto]):
        print(line, end="")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pipe.py <sto file>")
        sys.exit(1)
    sto = sys.argv[1]
    if not os.path.exists(sto):
        print(f"sto file {sto} does not exist")
        sys.exit(1)
    
    # Run pipeline
    cmsearch_out = cmsearch(sto)
    uniq_keep_sto = analyze(cmsearch_out)
    uniq_keep_fna = reformat(uniq_keep_sto)
    uniq_keep_motif_sto = cmfind(uniq_keep_fna)
    r2r(uniq_keep_motif_sto)
