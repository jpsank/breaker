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


@cli.command()
@click.argument('cmsearch_out')
@click.argument('color')
@click.option('--threshold', default=1)
def analyze(cmsearch_out, color, threshold=1):
    pipe.analyze(cmsearch_out, color=color, threshold=threshold)


@cli.command()
@click.argument('sto')
def refold(sto):
    fna = pipe.reformat(sto)
    pipe.cmfind(fna)


@cli.command()
@click.argument('sto')
@click.argument('out', default=None)
def reformat(sto, out):
    pipe.reformat(sto, out=out)


@cli.command()
@click.argument('fna')
def cmfind(fna):
    pipe.cmfind(fna)


@cli.command()
@click.argument('path')
def r2r(path):
    pipe.r2r(path)


if __name__ == '__main__':
    cli()