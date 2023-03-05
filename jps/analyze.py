"""
Analyze search results and generate plots.
"""

import pandas
import sys, os
import matplotlib.pyplot as plt
import numpy as np

from jps.inferno import *


def analyze(sr: SearchResult, name, color, outdir='search/analyze', threshold=0.01):
    # Table of counts/statistics
    print(f"Total number of {name} hits: {len(sr.hits)}")

    # Number of unique hits
    sr.remove_duplicates()
    print(f"Number of unique {name} hits: {len(sr.hits)}")
    sr.write(uniq_path := f"{outdir}/{name}.uniq")

    # Plot score distribution of unique hits
    print(f"Plotting {name} score distribution of unique hits...")
    df = pandas.DataFrame([hit.asdict() for hit in sr.hits.values()])
    score = np.log(df["E_value"])
    ax = score.hist(bins=50, color=color, label=name, log=True)
    ax.axvline(x=np.log(threshold), color=color, linestyle='dashed')
    ax.set_title(f"{name} score distribution")
    ax.set_xlabel('log(E-value)')
    ax.set_ylabel('Count')
    ax.figure.savefig(f"{outdir}/{name}_score_distribution.png")
    plt.clf()
    print(f"Saved {outdir}/{name}_score_distribution.png")

    # Number of unique hits with E-value < threshold
    sr.apply_threshold(threshold)
    print(f"Number of unique {name} hits with E-value < {threshold}: {len(sr.hits)}")
    sr.write(uniq_keep_path := f"{outdir}/{name}.uniq.keepE{str(threshold).replace('.', '')}")

    # R2R diagrams
    print("R2R commands:")
    print(f'r2r-mkcons {uniq_path}.sto')
    print(f'r2r-mkpdf-cons {uniq_path}.cons.sto')
    print(f'r2r-mkcons {uniq_keep_path}.sto')
    print(f'r2r-mkpdf-cons {uniq_keep_path}.cons.sto')


if __name__ == '__main__':
    # Load search results
    sr1 = SearchResult.parse('./search/searches/gtdb-prok_DUF1646_1/gtdb-prok_DUF1646_1.out')
    sr2 = SearchResult.parse('./search/searches/gtdb-prok_nhaA-I_2/gtdb-prok_nhaA-I_2.out')

    # Analyze search results
    threshold = 1
    outdir = 'search/analysis'
    analyze(sr1, 'DUF1646', 'DarkBlue', outdir=outdir, threshold=threshold)
    print()
    analyze(sr2, 'nhaA-I', 'DarkGreen', outdir=outdir, threshold=threshold)
