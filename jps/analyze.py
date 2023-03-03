"""
Analyze search results and generate plots.
"""

import pandas
import sys, os
import matplotlib.pyplot as plt
import numpy as np

from jps.inferno import *


def get_unique(hits: list[SearchResultHit]):
    """Remove duplicate hits from a search result."""
    sequence_texts = []
    unique_hits = []
    for hit in hits:
        if hit.text not in sequence_texts:
            unique_hits.append(hit)
            sequence_texts.append(hit.text)
    return unique_hits

def get_included(hits: list[SearchResultHit], threshold=0.01):
    """Get hits that are included in the final alignment."""
    return [hit for hit in hits if hit.E_value < threshold]


def analyze(sr: SearchResult, name, color, outdir='search/analyze', threshold=0.01):
    # Table of counts/statistics
    unique_all = get_unique(sr.hits.values())
    included = get_included(sr.hits.values(), threshold)
    unique_included = get_unique(included)
    print(f"Total number of {name} hits: {len(sr.hits)}")
    print(f"Number of unique {name} hits: {len(unique_all)}")
    print(f"Number of {name} hits with E-value < {threshold}: {len(included)}")
    print(f"Number of unique {name} hits with E-value < {threshold}: {len(unique_included)}")

    # TODO: Save included and unique hits to .keepE001 and .keepE001.uniq files using tblio.py

    # Plot score distribution as histogram
    df = pandas.DataFrame([hit.__dict__ for hit in unique_all])
    score = np.log(df["E_value"])
    ax = score.hist(bins=50, color=color, label=name, log=True)

    # Plot inclusion threshold (0.01)
    ax.axvline(x=np.log(threshold), color=color, linestyle='dashed')

    # Plot and save
    ax.set_title(f"{name} score distribution")
    ax.set_xlabel('log(E-value)')
    ax.set_ylabel('Count')
    ax.figure.savefig(f"{outdir}/{name}_score_distribution.png")
    plt.clf()

    # R2R diagrams
    # TODO: Make R2R diagrams of .keep.uniq file
    print("R2R commands:")
    print(f'r2r-mkcons {sr.sto.path}')
    print(f'r2r-mkpdf-cons {sr.sto.path.removesuffix(".sto")}.cons.sto')


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
