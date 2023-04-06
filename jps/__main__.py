import click
from subprocess import Popen, PIPE

from config import *
from jps.analyze import *

def next_free_path(name, out_fmt):
    if not os.path.exists(name):
        return name
    i = 1
    while os.path.exists(out_fmt.format(f"{name}_{i}")):
        i += 1
    return f"{name}_{i}"


def run_script(script, shell="bash", name="script"):
    """
    Run a shell script.

    script: shell script
    shell: shell to run script in (default: bash)
    """
    p = Popen([shell], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate(script.encode())
    if p.returncode != 0:
        raise Exception(f"Script '{name}' failed with return code {p.returncode}: {stderr.decode()}")
    return stdout.decode()


@click.group()
def cli():
    pass

@cli.command()
@click.argument('name') # name of the search
@click.argument('sto')  # path to stockholm alignment file
@click.option('--E', default=1000.0)
@click.option('--incE', default=1000.0)
@click.option('--DBFNA', default="gtdb/gtdb-bact-r207-repr.fna.gz")
def cmsearch(name, sto, E, incE, DBFNA):
    out = next_free_path(name, out_fmt=os.path.join(SEARCHES_DIR, "{}/{}.out"))
    stdout = run_script(f"sbatch {os.path.join(SCRIPTS_DIR, 'cmsearch.sh')} {sto} {out} {E} {incE} {DBFNA}")
    print(stdout)
    print(f"Search results will be written to {out}.")

# Example usage:
# cmsearch("gtdb-prok_DUF1646", "data/sto/DUF1646/RF03071.sto")
# cmsearch("gtdb-prok_nhaA-I", "data/sto/nhaA-I/RF03057.sto")


@cli.command()
@click.argument('cmsearch_out')
@click.argument('name')
@click.argument('color')
@click.option('--threshold', default=1)
def analysis(cmsearch_out, name, color, threshold=1):
    sr = SearchResult.parse(cmsearch_out)
    analyze(sr, name, color, threshold=threshold)

# Example usage:
# analysis("data/searches/gtdb-prok_DUF1646/gtdb-prok_DUF1646.out", "gtdb-prok_DUF1646", "DarkBlue")
# analysis("data/searches/gtdb-prok_nhaA-I/gtdb-prok_nhaA-I.out", "gtdb-prok_nhaA-I", "DarkGreen")

@cli.command()
@click.argument('sto')
@click.argument('out')
def reformat(sto, out):
    run_script(f"{os.path.join(SCRIPTS_DIR, 'reformat.sh')} {sto} {out}")

# Example usage:
# reformat("data/analysis/data/DUF1646.uniq.keepE1.sto", "data/refold/DUF1646.fna")
# reformat("data/analysis/data/nhaA-I.uniq.keepE1.sto", "data/refold/nhaA-I.fna")

@cli.command()
@click.argument('fna')
def cmfind(fna):
    stdout = run_script(f"sbatch {os.path.join(SCRIPTS_DIR, 'cmfinder.sh')} {fna}")
    print(stdout)

# Example usage:
# cmfinder("data/refold/DUF1646.fna")
# cmfinder("data/refold/nhaA-I.fna")

@cli.command()
@click.argument('name')
def r2r(name):
    stdout = run_script(f"{os.path.join(SCRIPTS_DIR, 'r2r.sh')} {name}")
    print(stdout)

# Example usage:
# r2r("data/refold/DUF1646.fna.motif.h2_1")
# r2r("data/refold/nhaA-I.fna.motif.h2_1")


if __name__ == '__main__':
    cli()