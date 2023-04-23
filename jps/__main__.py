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
    cmsearch_out = pipe.cmsearch(sto, e=e, dbfna=dbfna)
    print(f"Next, run analyze on {cmsearch_out}")


@cli.command()
@click.argument('cmsearch_out')
@click.argument('color', default="DarkBlue")
@click.option('--threshold', default=1.0)
def analyze(cmsearch_out, color, threshold):
    uniq_keep_sto = pipe.analyze(cmsearch_out, color=color, threshold=threshold)
    print(f"Next, run refold on {uniq_keep_sto}")


@cli.command()
@click.argument('sto')
def refold(sto):
    fna = pipe.reformat(sto)
    motif_sto = pipe.cmfind(fna)
    print(f"Next, run r2r on {motif_sto}")



@cli.command()
@click.argument('sto')
@click.argument('out', default=None)
def reformat(sto, out):
    fna = pipe.reformat(sto, out=out)
    print(f"Next, run cmfind on {fna}")


@cli.command()
@click.argument('fna')
def cmfind(fna):
    motif_sto = pipe.cmfind(fna)
    print(f"Next, run r2r on {motif_sto}")


@cli.command()
@click.argument('path')
def r2r(path):
    pipe.r2r(path)


if __name__ == '__main__':
    cli()