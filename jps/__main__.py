import click
import subprocess

from config import *
from jps.analyze import *


def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


@click.group()
def cli():
    pass

@cli.command()
@click.argument('sto')  # path to stockholm alignment file
@click.option('--e', 'e', default=1000.0)  # E-value threshold and cutoff
@click.option('--dbfna', 'dbfna', default="/home/jps228/project/gtdb/gtdb-bact-r207-repr.fna.gz")  # path to database FASTA file
def cmsearch(sto, e, dbfna):
    """ Run a cmsearch on a stockholm alignment file. """

    # Auto-generate output path
    names = [
        sto_filename(sto),
        os.path.basename(dbfna).split('.')[0],
        f"E{float_to_str(e)}",
    ]
    fullname = "_".join(names)
    out = os.path.join(SEARCHES_DIR, f"{fullname}", f"{fullname}.out")
    if os.path.exists(out):
        raise Exception(f"Output path already exists: {out}")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    
    # Run cmsearch
    for line in execute(["sbatch", os.path.join(SCRIPTS_DIR, 'cmsearch.sh'), sto, out, str(e), str(e), dbfna]):
        print(line, end="")

# Example usage:
# cmsearch data/sto/DUF1646/RF03071.sto
# cmsearch data/sto/nhaA-I/RF03057.sto


@cli.command()
@click.argument('cmsearch_out')
@click.argument('color')
@click.option('--threshold', default=1)
def analyze(cmsearch_out, color, threshold=1):
    sr = SearchResult.parse(cmsearch_out)
    name = os.path.splitext(os.path.basename(cmsearch_out))[0]
    outdir = os.path.join(ANALYSIS_DIR, name)
    os.makedirs(outdir, exist_ok=True)
    run_analysis(sr, name, color, outdir, threshold)

# Example usage:
# analyze data/searches/gtdb-prok_DUF1646/gtdb-prok_DUF1646.out gtdb-prok_DUF1646 DarkBlue
# analyze data/searches/gtdb-prok_nhaA-I/gtdb-prok_nhaA-I.out gtdb-prok_nhaA-I DarkGreen
# analyze data/searches/lina-combo-v1_gtdb-bact-r207-repr_E1000.0/lina-combo-v1_gtdb-bact-r207-repr_E1000.0.out DarkRed


@cli.command()
@click.argument('sto')
def refold(sto):
    name = sto_filename(sto)
    fna = os.path.join(REFOLD_DIR, name, f"{name}.fna")
    os.makedirs(os.path.dirname(fna), exist_ok=True)

    # Reformat to FASTA
    for line in execute([os.path.join(SCRIPTS_DIR, 'reformat.sh'), sto, fna]):
        print(line, end="")

    # Run CMfinder
    for line in execute(["sbatch", os.path.join(SCRIPTS_DIR, 'cmfinder.sh'), fna]):
        print(line, end="")


@cli.command()
@click.argument('sto')
@click.argument('out', default=None)
def reformat(sto, out):
    if out is None:
        out = f"{sto}.fna"

    for line in execute([os.path.join(SCRIPTS_DIR, 'reformat.sh'), sto, out]):
        print(line, end="")

# Example usage:
# reformat data/analysis/data/DUF1646.uniq.keepE1.sto
# reformat data/analysis/data/nhaA-I.uniq.keepE1.sto


@cli.command()
@click.argument('fna')
def cmfind(fna):
    for line in execute(["sbatch", os.path.join(SCRIPTS_DIR, 'cmfinder.sh'), fna]):
        print(line, end="")

# Example usage:
# cmfinder data/refold/DUF1646.fna
# cmfinder data/refold/nhaA-I.fna


@cli.command()
@click.argument('name')
def r2r(name):
    for line in execute([os.path.join(SCRIPTS_DIR, 'r2r.sh'), name]):
        print(line, end="")

# Example usage:
# r2r data/refold/DUF1646.fna.motif.h2_1
# r2r data/refold/nhaA-I.fna.motif.h2_1


if __name__ == '__main__':
    cli()