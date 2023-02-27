import pandas
import sys, os
import matplotlib.pyplot as plt
import numpy as np

from parse import *

DUF = SearchResult.from_files(
    './search/searches/gtdb-bact_DUF1646_1/gtdb-bact_DUF1646_1.out.sto',
    './search/searches/gtdb-bact_DUF1646_1/gtdb-bact_DUF1646_1.out.tbl',
)
NHA = SearchResult.from_files(
    './search/searches/gtdb-bact_nhaA-I_1/gtdb-bact_nhaA-I_1.out.sto',
    './search/searches/gtdb-bact_nhaA-I_1/gtdb-bact_nhaA-I_1.out.tbl',
)

# Counts above threshold (E-value < 0.01)
incDUF = sum(1 for h in DUF.hits.values() if h.inc == '!')
incNHA = sum(1 for h in NHA.hits.values() if h.inc == '!')
print(f"Number of DUF1646 hits above threshold: {incDUF}")
print(f"Number of nhaA-I hits above threshold: {incNHA}")

# Score distribution

inc_threshold = 0.01
def plot_score(df, name, color, outdir='search/analyze'):
    # TODO: Get rid of duplicate sequences
    # TODO: Integrate into SearchResult class
    # Remove duplicates
    unique = df[df['seq'].isnull() | ~df[df['seq'].notnull()].duplicated(subset='seq', keep='first')]
    # Score distribution
    score = np.log(unique['E_value'])
    ax = score.hist(bins=50, color=color, label=name, log=True)
    # Inclusion threshold (0.01)
    ax.axvline(x=np.log(inc_threshold), color=color, linestyle='dashed')
    # Plot
    ax.set_title(f"{name} score distribution")
    ax.set_xlabel('log(E-value)')
    ax.set_ylabel('Count')
    ax.figure.savefig(f"{outdir}/{name}_score_distribution.png")
    plt.clf()


dfDUF = DUF.to_dataframe()
dfNHA = NHA.to_dataframe()

plot_score(dfDUF, 'DUF1646', 'DarkBlue')
plot_score(dfNHA, 'nhaA-I', 'DarkGreen')

# R2R diagrams

print("R2R commands:")
print(f'r2r-mkcons {DUF.sto.path}')
print(f'r2r-mkpdf-cons {DUF.sto.path.removesuffix(".sto")}.cons.sto')
print()
print(f'r2r-mkcons {NHA.sto.path}')
print(f'r2r-mkpdf-cons {NHA.sto.path.removesuffix(".sto")}.cons.sto')

