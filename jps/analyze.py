"""
Analyze search results and generate plots.
"""

import pandas
import sys, os
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate

from config import *
from jps.models import *
from jps.routes import *
from jps.util.helpers import *
import jps.util.iosto as iosto
from jps.extra.interval import ChrInterval


# def compare(search1: Search, search2: Search):
#     for hit in search1.overlapping_hits(search2).all():
#         if h1.overlaps(h2) != 0:
#             intersects.append((h1, h2))
#         # Check for tandems
#         elif h1.distance_to(h2) <= 100:
#             print(f"Found tandem: {h1.chraccn} {h1.start}-{h1.end} (bit={h1.bitscore}) {h2.start}-{h2.end} (bit={h2.bitscore})")
    
#     return intersects


def plot_score_distribution(hits: list[Hit], name, color, out, threshold=0.01):
    df = pandas.DataFrame([hit.asdict() for hit in hits])
    score = np.log10(df["evalue"])
    ax = score.hist(bins=50, color=color, label=name, log=True)
    ax.axvline(x=np.log10(threshold), color=color, linestyle='dashed')
    ax.set_title(f"{name} score distribution")
    ax.set_xlabel('log(E-value)')
    ax.set_ylabel('Count')
    ax.figure.savefig(out)
    plt.clf()


def compare(search1: Search, search2: Search):
    pass



if __name__ == '__main__':
    pass
    # Search result path names
    # DUF = "gtdb-prok_DUF1646_1"
    # NHA = "gtdb-prok_nhaA-I_2"
    # DUFNHA = "DUF1646_nhaA-I.fna.motif.h2_1_gtdb-bact-r207-repr_E1000.0"
    # LINA = "lina-combo-v1_gtdb-bact-r207-repr_E1000.0"

    # # First, get numbers for all models
    # threshold = 1000
    # table = [["Name", "# Total", "# Unique", f"# Unique E<{threshold}"]]
    # for name in [DUF, NHA, DUFNHA, LINA]:
    #     sr = SearchResult.parse(os.path.join(SEARCHES_DIR, name, f"{name}.out"))
    #     ntotal = len(sr.hits)
    #     sr.remove_duplicates()
    #     nunique = len(sr.hits)
    #     sr.apply_threshold(threshold)
    #     nunique_keep = len(sr.hits)
    #     table.append([name, ntotal, nunique, nunique_keep])
    # print(tabulate(table, headers="firstrow", tablefmt="github"))
    # print()

    # # Then, do DUF and NHA intersect?
    # sr_duf = SearchResult.parse(os.path.join(SEARCHES_DIR, DUF, f"{DUF}.out"))
    # sr_nha = SearchResult.parse(os.path.join(SEARCHES_DIR, NHA, f"{NHA}.out"))

    # # Only need unique hits
    # sr_duf.remove_duplicates()
    # sr_nha.remove_duplicates()

    # # Get intersecting hits
    # intersects = compare(sr_duf, sr_nha)
    # print(f"Found {len(intersects)} intersecting hits between DUF1646 and nhaA-I")
    # print()

    # # Next, do DUF and nhaA-I intersect with combined model?
    # for combo in [DUFNHA, LINA]:
    #     # Load search results of models in question
    #     sr_duf = SearchResult.parse(os.path.join(SEARCHES_DIR, DUF, f"{DUF}.out"))
    #     sr_nha = SearchResult.parse(os.path.join(SEARCHES_DIR, NHA, f"{NHA}.out"))
    #     sr_combo = SearchResult.parse(os.path.join(SEARCHES_DIR, combo, f"{combo}.out"))

    #     # Only need unique hits
    #     sr_duf.remove_duplicates()
    #     sr_nha.remove_duplicates()
    #     sr_combo.remove_duplicates()

    #     sr_duf.apply_threshold(1)
    #     sr_nha.apply_threshold(1)

    #     # Compare search results of combined model vs. DUF1646 and nhaA-I (old models)
    #     # What we want to know:
    #     # E    I    II   III   IV   V
    #     # 1    ?    ?    ?     ?    ?
    #     # 10   ?    ?    ?     ?    ?
    #     # 100  ?    ?    ?     ?    ?
    #     # 1000 ?    ?    ?     ?    ?
    #     # Where:
    #     # E = E-value threshold
    #     # I = # of DUF1646 hits not in combo
    #     # II = # of DUF1646 hits in combo
    #     # III = # of combo hits not in DUF1646 or nhaA-I
    #     # IV = # of nhaA-I hits in combo
    #     # V = # of nhaA-I hits not in combo

    #     I = []
    #     II = []
    #     III = []
    #     IV = []
    #     V = []

    #     print(f"Comparison of {combo} to {DUF} and {NHA}:")

    #     table = [["E", "I", "II", "III", "IV", "V"]]
    #     for threshold in [1000, 100, 10, 1]:
    #         sr_combo.apply_threshold(threshold)

    #         duf_intersects_combo = compare(sr_duf, sr_combo)
    #         nha_intersects_combo = compare(sr_nha, sr_combo)

    #         I.append(len(sr_duf.hits) - len(duf_intersects_combo))
    #         II.append(len(duf_intersects_combo))
    #         III.append(len(sr_combo.hits) - len(duf_intersects_combo) - len(nha_intersects_combo))
    #         IV.append(len(nha_intersects_combo))
    #         V.append(len(sr_nha.hits) - len(nha_intersects_combo))

    #         table.append([threshold, I[-1], II[-1], III[-1], IV[-1], V[-1]])

    #     print(tabulate(table, headers="firstrow", tablefmt="github"))
    #     print()
        
