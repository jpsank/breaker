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


def compare(sr1: SearchResult, sr2: SearchResult):
    # Get target names that are in both sr1 and sr2
    hits1 = defaultdict(list)
    for h in sr1.hits.values():
        hits1[h.row.target_name].append(h)
    hits2 = defaultdict(list)
    for h in sr2.hits.values():
        hits2[h.row.target_name].append(h)
    
    # Check for intersecting hits
    intersects = []
    for target_name in set(hits1.keys()).intersection(set(hits2.keys())):
        for h1 in hits1[target_name]:
            for h2 in hits2[target_name]:
                max_len = max(len(h1.seq.text), len(h2.seq.text))

                from1, to1 = h1.row.seq_from, h1.row.seq_to
                from2, to2 = h2.row.seq_from, h2.row.seq_to
                if from1 > to1: from1, to1 = to1, from1
                if from2 > to2: from2, to2 = to2, from2
                if abs(from1-from2) <= max_len or abs(to1-to2) <= max_len:
                    intersects.append((h1, h2))
    
    return intersects


def plot_score_distribution(sr: SearchResult, name, color, out, threshold=0.01):
    df = pandas.DataFrame([hit.asdict() for hit in sr.hits.values()])
    score = np.log10(df["E_value"])
    ax = score.hist(bins=50, color=color, label=name, log=True)
    ax.axvline(x=np.log10(threshold), color=color, linestyle='dashed')
    ax.set_title(f"{name} score distribution")
    ax.set_xlabel('log(E-value)')
    ax.set_ylabel('Count')
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
    # # Load search results and analyze
    # sr1 = SearchResult.parse(os.path.join(SEARCHES_DIR, 'gtdb-prok_DUF1646_1/gtdb-prok_DUF1646_1.out'))
    # sr2 = SearchResult.parse(os.path.join(SEARCHES_DIR, 'gtdb-prok_nhaA-I_2/gtdb-prok_nhaA-I_2.out'))
    # threshold = 1
    # run_analysis(sr1, 'DUF1646', 'DarkBlue', outdir=os.path.join(ANALYSIS_DIR, 'gtdb-prok_DUF1646_1'), threshold=threshold)
    # print()
    # run_analysis(sr2, 'nhaA-I', 'DarkGreen', outdir=os.path.join(ANALYSIS_DIR, 'gtdb-prok_nhaA-I_2'), threshold=threshold)

    # Search result path names
    DUF = "gtdb-prok_DUF1646_1"
    NHA = "gtdb-prok_nhaA-I_2"
    DUFNHA = "DUF1646_nhaA-I.fna.motif.h2_1_gtdb-bact-r207-repr_E1000.0"
    LINA = "lina-combo-v1_gtdb-bact-r207-repr_E1000.0"

    # First, get numbers for all models
    threshold = 1000
    table = [["Name", "# Total", "# Unique", f"# Unique E<{threshold}"]]
    for name in [DUF, NHA, DUFNHA, LINA]:
        sr = SearchResult.parse(os.path.join(SEARCHES_DIR, name, f"{name}.out"))
        ntotal = len(sr.hits)
        sr.remove_duplicates()
        nunique = len(sr.hits)
        sr.apply_threshold(threshold)
        nunique_keep = len(sr.hits)
        table.append([name, ntotal, nunique, nunique_keep])
    print(tabulate(table, headers="firstrow", tablefmt="github"))
    print()

    # Then, do DUF and NHA intersect?
    sr_duf = SearchResult.parse(os.path.join(SEARCHES_DIR, DUF, f"{DUF}.out"))
    sr_nha = SearchResult.parse(os.path.join(SEARCHES_DIR, NHA, f"{NHA}.out"))

    # Only need unique hits
    sr_duf.remove_duplicates()
    sr_nha.remove_duplicates()

    # Get intersecting hits
    intersects = compare(sr_duf, sr_nha)
    print(f"Found {len(intersects)} intersecting hits between DUF1646 and nhaA-I")
    print()

    # Next, do DUF and nhaA-I intersect with combined model?
    for combo in [DUFNHA, LINA]:
        # Load search results of models in question
        sr_duf = SearchResult.parse(os.path.join(SEARCHES_DIR, DUF, f"{DUF}.out"))
        sr_nha = SearchResult.parse(os.path.join(SEARCHES_DIR, NHA, f"{NHA}.out"))
        sr_combo = SearchResult.parse(os.path.join(SEARCHES_DIR, combo, f"{combo}.out"))

        # Only need unique hits
        sr_duf.remove_duplicates()
        sr_nha.remove_duplicates()
        sr_combo.remove_duplicates()

        # Compare search results of combined model vs. DUF1646 and nhaA-I (old models)
        # What we want to know:
        # E    I    II   III   IV   V
        # 1    ?    ?    ?     ?    ?
        # 10   ?    ?    ?     ?    ?
        # 100  ?    ?    ?     ?    ?
        # 1000 ?    ?    ?     ?    ?
        # Where:
        # E = E-value threshold
        # I = # of DUF1646 hits not in combo
        # II = # of DUF1646 hits in combo
        # III = # of combo hits not in DUF1646 or nhaA-I
        # IV = # of nhaA-I hits in combo
        # V = # of nhaA-I hits not in combo

        I = []
        II = []
        III = []
        IV = []
        V = []

        table = [["E", "I", "II", "III", "IV", "V"]]
        for threshold in [1000, 100, 10, 1]:
            sr_duf.apply_threshold(threshold)
            sr_nha.apply_threshold(threshold)
            sr_combo.apply_threshold(threshold)

            duf_intersects_combo = compare(sr_duf, sr_combo)
            nha_intersects_combo = compare(sr_nha, sr_combo)

            I.append(len(sr_duf.hits) - len(duf_intersects_combo))
            II.append(len(duf_intersects_combo))
            III.append(len(sr_combo.hits) - len(duf_intersects_combo) - len(nha_intersects_combo))
            IV.append(len(nha_intersects_combo))
            V.append(len(sr_nha.hits) - len(nha_intersects_combo))

            table.append([threshold, I[-1], II[-1], III[-1], IV[-1], V[-1]])

        print(f"Comparison of {combo} to {DUF} and {NHA}:")
        print(tabulate(table, headers="firstrow", tablefmt="github"))
        print()
        
