import click
import subprocess

from config import *
from jps.analyze import *

def next_free_path(name, fmt):
    out = fmt.format(name)
    i = 1
    while os.path.exists(out):
        out = fmt.format(f"{name}_{i}")
        i += 1
    return out


# def run_script(script, shell="bash"):
#     """
#     Run a shell script.

#     script: shell script
#     shell: shell to run script in (default: bash)
#     """
#     print(f"Running script: {script}")
#     p = Popen([shell], stdin=PIPE, stdout=PIPE, stderr=PIPE)
#     stdout, stderr = p.communicate(script.encode())
#     if p.returncode != 0:
#         raise Exception(f"Script failed with return code {p.returncode}: {stderr.decode()}")
#     return stdout.decode()

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
@click.option('--name', 'name', default=None)  # name of the search
@click.option('--e', 'e', default=1000.0)  # E-value threshold and cutoff
@click.option('--dbfna', 'dbfna', default="~/project/gtdb/gtdb-bact-r207-repr.fna.gz")  # path to database FASTA file
def cmsearch(sto, name, e, dbfna):
    """ Run a cmsearch on a stockholm alignment file. """

    # Auto-generate name if not provided
    if name is None:
        name = "_".join([
            os.path.splitext(os.path.basename(sto))[0],
            str(e),
            os.path.basename(dbfna).split('.')[0]
            ])
    
    # Compute output path and create directories
    out = os.path.join(SEARCHES_DIR, f"{name}", f"{name}.out")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    
    # Run cmsearch
    for line in execute(["sbatch", os.path.join(SCRIPTS_DIR, 'cmsearch.sh'), sto, out, str(e), str(e), dbfna]):
        print(line, end="")

# Example usage:
# cmsearch data/sto/DUF1646/RF03071.sto
# cmsearch data/sto/nhaA-I/RF03057.sto


@cli.command()
@click.argument('cmsearch_out')
@click.argument('name')
@click.argument('color')
@click.option('--threshold', default=1)
def analysis(cmsearch_out, name, color, threshold=1):
    sr = SearchResult.parse(cmsearch_out)
    analyze(sr, name, color, threshold=threshold)

# Example usage:
# analysis data/searches/gtdb-prok_DUF1646/gtdb-prok_DUF1646.out gtdb-prok_DUF1646 DarkBlue
# analysis data/searches/gtdb-prok_nhaA-I/gtdb-prok_nhaA-I.out gtdb-prok_nhaA-I DarkGreen


@cli.command()
@click.argument('sto')
@click.argument('out', default=None)
def reformat(sto, out):
    if out is None:
        out = f"{sto}.fna"

    for line in execute([os.path.join(SCRIPTS_DIR, 'reformat.sh'), sto, out]):
        print(line, end="")

# Example usage:
# reformat data/analysis/data/DUF1646.uniq.keepE1.sto data/refold/DUF1646.fna
# reformat data/analysis/data/nhaA-I.uniq.keepE1.sto data/refold/nhaA-I.fna


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