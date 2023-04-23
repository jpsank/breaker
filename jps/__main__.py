import click
import subprocess

from config import *
from jps.analyze import *
from jps.util import *
import jps.pipe as pipe


@click.group()
def cli():
    pass

@cli.command()
@click.argument('sto')  # path to stockholm alignment file
@click.option('--e', 'e', default=1000.0)  # E-value threshold and cutoff
@click.option('--dbfna', 'dbfna', default=GTDB_PROK_DB)  # path to database FASTA file
def cmsearch(sto, e, dbfna):
    pipe.cmsearch(sto, e=e, dbfna=dbfna)

# Example usage:
# cmsearch data/sto/DUF1646/RF03071.sto
# cmsearch data/sto/nhaA-I/RF03057.sto


@cli.command()
@click.argument('cmsearch_out')
@click.argument('color')
@click.option('--threshold', default=1)
def analyze(cmsearch_out, color, threshold=1):
    pipe.analyze(cmsearch_out, color=color, threshold=threshold)

# Example usage:
# analyze data/searches/gtdb-prok_DUF1646_1/gtdb-prok_DUF1646_1.out DarkBlue
# analyze data/searches/gtdb-prok_nhaA-I_2/gtdb-prok_nhaA-I_2.out DarkGreen
# analyze data/searches/DUF1646_nhaA-I.fna.motif.h2_1_gtdb-bact-r207-repr_E1000.0/DUF1646_nhaA-I.fna.motif.h2_1_gtdb-bact-r207-repr_E1000.0.out Purple
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
@click.argument('path')
def r2r(path):
    for line in execute([os.path.join(SCRIPTS_DIR, 'r2r.sh'), path]):
        print(line, end="")

# Example usage:
# r2r data/refold/DUF1646.fna.motif.h2_1
# r2r data/refold/nhaA-I.fna.motif.h2_1


if __name__ == '__main__':
    cli()