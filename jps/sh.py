import sys, os
from subprocess import Popen, PIPE
from dataclasses import dataclass


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


def run_sbatch(script):
    """
    Run a shell script on the cluster.

    script: shell script
    """
    return run_script(f"""
sbatch <<EOF
{script}
EOF
""", name="sbatch")


# def make_jobscript(script, name, modules=[], partition="pi_breaker", time="1:00:00", ntasks=1, cpus_per_task=8):
#         return f"""
# #!/bin/bash
# #SBATCH --job-name={name}
# #SBATCH --time={time}
# #SBATCH --ntasks={ntasks}
# #SBATCH --cpus-per-task={cpus_per_task}
# #SBATCH --partition {partition}

# {'module load ' + ' '.join(modules) if modules else ''}
# {script}
# """


# # Run cmsearch on a Stockholm alignment file.
# #   sto: path to Stockholm alignment file
# #   out: path to output file (cmsearch output, ending with .out)
# #   E: E-value threshold
# #   incE: E-value inclusion threshold
# #   DBFNA: path to sequence database
# cmsearch_script = """
# sto="{sto}"
# out="{out}"

# # Build a covariance model from a Stockholm alignment file.
# if [ ! -f "$sto.cm" ]; then
#     cmbuild "$sto.cm" "$sto"
#     cmcalibrate "$sto.cm"
# fi

# # Search covariance model against sequence database.
# cmsearch -o "$out" -A "$out.sto" --tblout "$out.tbl" -E "{E}" --incE "{incE}" "$sto.cm" "{DBFNA}"
# """

# # Run esl-reformat on a Stockholm alignment file.
# #   sto: path to Stockholm alignment file
# #   out: path to output .fna file (esl-reformat output)
# esl_reformat_script = """
# esl-reformat fasta "{sto}" > "{out}"
# """

# # Run cmfinder on a Stockholm alignment file.
# #   fna: path to .fna file
# #   out: path to output file (cmfinder output)
# cmfinder_script = """
# export PATH="$PATH:/gpfs/gibbs/pi/breaker/software/bin/cmfinder.pl"
# export CMfinder="/gpfs/gibbs/pi/breaker/software/packages/cmfinder-0.4.1.18"

# /gpfs/gibbs/pi/breaker/software/bin/cmfinder.pl --combine "{fna}" > "{out}"
# """

# # R2R aliases should already be loaded in the environment.
# r2r_aliases = """
# function r2r-mkcons {
# 	# Usage: r2r-mkcons <name>.sto
#     r2r --GSC-weighted-consensus "$1" "${1%sto}cons.sto" \
#         3 0.97 0.9 0.75 4 0.97 0.9 0.75 0.5 0.1
# }

# function r2r-mkpdf-cons {
# 	# Usage: r2r-mkpdf-cons <name>.cons.sto
#     r2r --disable-usage-warning "$1" "${1%cons.sto}pdf"
# }

# function r2r-mkpdf-meta {
# 	# Usage: r2r-mkpdf-meta <name>.r2r_meta
#     r2r --disable-usage-warning "$1" "${1%r2r_meta}pdf"
# }
# """

# # Run r2r on a Stockholm alignment file.
# r2r_script = """
# r2r-mkcons "{name}.sto"
# r2r-mkpdf-cons "{name}.cons.sto"
# """


# @dataclass
# class Script:
#     script: str
#     name: str

#     def run(self):
#         return run_script(self.script, name=self.name)

#     def run_sbatch(self):
#         return run_sbatch(self.script, name=self.name)



