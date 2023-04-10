"""
Analyze search results and generate plots.
"""

import pandas
import sys, os
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate

from config import *
from jps.inferno import *
from jps.util import *


# def compare(sr1: SearchResult, sr2: SearchResult, distance_threshold=1000):
#     # Get target names that are in both sr1 and sr2
#     hits1 = defaultdict(list)
#     for h in sr1.hits.values():
#         hits1[h.row.target_name].append(h)
#     hits2 = defaultdict(list)
#     for h in sr2.hits.values():
#         hits2[h.row.target_name].append(h)
#     targets = set(hits1.keys()).intersection(set(hits2.keys()))
    
#     # Check for intersecting hits
#     for target_name in targets:
#         if target_name in hits1 and target_name in hits2:
#             for h1 in hits1[target_name]:
#                 for h2 in hits2[target_name]:
#                     from1, to1 = h1.row.seq_from, h1.row.seq_to
#                     from2, to2 = h2.row.seq_from, h2.row.seq_to
#                     if from1 > to1: from1, to1 = to1, from1
#                     if from2 > to2: from2, to2 = to2, from2
#                     if abs(from1-from2) < distance_threshold or abs(to1-to2) < distance_threshold:
#                         print(f"compare: Potential intersect at {target_name}, 1:{from1}-{to1} 2:{from2}-{to2}")
#     else:
#         print("compare: No intersecting hits found")


def plot_score_distribution(sr: SearchResult, name, color, out=None, threshold=0.01):
    df = pandas.DataFrame([hit.asdict() for hit in sr.hits.values()])
    score = np.log10(df["E_value"])
    ax = score.hist(bins=50, color=color, label=name, log=True)
    ax.axvline(x=np.log10(threshold), color=color, linestyle='dashed')
    ax.set_title(f"{name} score distribution")
    ax.set_xlabel('log(E-value)')
    ax.set_ylabel('Count')
    if out:
        ax.figure.savefig(out)
    plt.clf()


def run_analysis(sr: SearchResult, name, color, outdir, threshold=0.01):
    # Get unique hits
    (sr_unique := sr.copy()).remove_duplicates()

    # Plot score distribution of unique hits
    print(f"Plotting {name} score distribution of unique hits...")
    plot_score_distribution(sr_unique, name, color, 
                            out=f"{outdir}/{name}_score_distribution.png", threshold=threshold)
    print(f"Saved {outdir}/{name}_score_distribution.png")

    # Get included hits and included unique hits
    (sr_keep := sr.copy()).apply_threshold(threshold)
    (sr_unique_keep := sr_keep.copy()).remove_duplicates()

    # Write table of counts
    with open(f"{outdir}/{name}.counts.txt", 'w') as f:
        table = [
            ["Name", "# Total", "# Unique", f"# E<{threshold}", f"# Unique E<{threshold}"],
            [name, len(sr.hits), len(sr_unique.hits), len(sr_keep.hits), len(sr_unique_keep.hits)]
        ]
        f.write(tabulate(table, headers="firstrow", tablefmt="plain"))
    print(f"Saved {outdir}/{name}.counts.txt")

    # Save data files for R2R
    os.makedirs(data_dir := os.path.join(outdir, "data"), exist_ok=True)
    sr_unique.write(os.path.join(data_dir, f"{name}.uniq"))
    sr_keep.write(os.path.join(data_dir, f"{name}.keepE{slugify_float(threshold)}"))
    sr_unique_keep.write(uniq_keep_path := os.path.join(data_dir, f"{name}.uniq.keepE{slugify_float(threshold)}"))

    return uniq_keep_path


if __name__ == '__main__':
    # Load search results
    sr1 = SearchResult.parse(os.path.join(SEARCHES_DIR, 'gtdb-prok_DUF1646_1/gtdb-prok_DUF1646_1.out'))
    sr2 = SearchResult.parse(os.path.join(SEARCHES_DIR, 'gtdb-prok_nhaA-I_2/gtdb-prok_nhaA-I_2.out'))

    # Analyze search results
    threshold = 1
    run_analysis(sr1, 'DUF1646', 'DarkBlue', outdir=os.path.join(ANALYSIS_DIR, 'gtdb-prok_DUF1646_1'), threshold=threshold)
    print()
    run_analysis(sr2, 'nhaA-I', 'DarkGreen', outdir=os.path.join(ANALYSIS_DIR, 'gtdb-prok_nhaA-I_2'), threshold=threshold)
