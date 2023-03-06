"""
Analyze search results and generate plots.
"""

import pandas
import sys, os
import matplotlib.pyplot as plt
import numpy as np

from jps.inferno import *


def compare(sr1: SearchResult, sr2: SearchResult, distance_threshold=1000):
    # Get target names that are in both sr1 and sr2
    hits1 = defaultdict(list)
    for h in sr1.hits.values():
        hits1[h.row.target_name].append(h)
    hits2 = defaultdict(list)
    for h in sr2.hits.values():
        hits2[h.row.target_name].append(h)
    targets = set(hits1.keys()).intersection(set(hits2.keys()))
    
    # Check for intersecting hits
    for target_name in targets:
        if target_name in hits1 and target_name in hits2:
            for h1 in hits1[target_name]:
                for h2 in hits2[target_name]:
                    from1, to1 = h1.row.seq_from, h1.row.seq_to
                    from2, to2 = h2.row.seq_from, h2.row.seq_to
                    if from1 > to1: from1, to1 = to1, from1
                    if from2 > to2: from2, to2 = to2, from2
                    if abs(from1-from2) < distance_threshold or abs(to1-to2) < distance_threshold:
                        print(f"compare: Potential intersect at {target_name}, 1:{from1}-{to1} 2:{from2}-{to2}")
    else:
        print("compare: No intersecting hits found")


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
