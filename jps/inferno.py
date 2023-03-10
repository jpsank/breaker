"""
inferno.py

Infernal (cmsearch) output parser.
"""

from dataclasses import dataclass, field
from collections import defaultdict
import pandas
from pyfaidx import Fasta

from jps.tblio import SearchResultRow, SearchResultTable
from jps.iosto import Stockholm, StoSequence


class InfernoError(Exception):
    """ Errors related to processing Infernal output. """


@dataclass
class SearchResultHit:
    """
    Represents a single hit in a cmsearch result, consisting of a row in the
    cmsearch result table and the corresponding sequence in the Stockholm file.
    """

    row: SearchResultRow
    seq: StoSequence

    def asdict(self):
        return {
            'seqname': self.row.seqname(),
            **self.row.__dict__,
            'seq': self.seq.text if self.seq else None,
        }


@dataclass
class SearchResult:
    """ Represents the results of a cmsearch, consisting of a sto file and tbl. """

    sto: Stockholm
    tbl: SearchResultTable
    hits: 'dict[str, SearchResultHit]'
    dbfna_path: str = None
    fasta: Fasta = None

    @staticmethod
    def parse(path: str, dbfna_path: str = None):
        """ Parse a cmsearch result from a path. """

        # Parse Stockholm file
        sto = Stockholm.parse(f"{path}.sto")

        # Parse tbl file
        tbl = SearchResultTable.parse(f"{path}.tbl")

        # Create hits relation
        hits = {seqname: SearchResultHit(row, sto.msa.get(seqname)) for seqname, row in tbl.rows.items()}
        
        # Create FASTA index
        fasta = Fasta(dbfna_path) if dbfna_path else None
        
        return SearchResult(sto, tbl, hits, dbfna_path, fasta)

    def copy(self):
        return SearchResult(self.sto.copy(), self.tbl.copy(), self.hits.copy())

    def remove_hit(self, seqname: str):
        """ Remove a hit from the search result. """
        self.tbl.remove_row(seqname)
        self.sto.remove_seq(seqname)
        del self.hits[seqname]

    def apply_threshold(self, threshold: float):
        for seqname, hit in list(self.hits.items()):
            if hit.row.E_value >= threshold:
                self.remove_hit(seqname)

    def remove_duplicates(self):
        seen = set()
        for seqname, hit in list(self.hits.items()):
            if hit.seq is None:
                print(f"WARNING: No sequence found for {seqname}")
                continue
            if hit.seq.text in seen:
                self.remove_hit(seqname)
            else:
                seen.add(hit.seq.text)

    def write(self, path: str):
        self.sto.write(f"{path}.sto")
        self.tbl.write(f"{path}.tbl")

    # def get_flank(self, seq: StoSequence, flank: int):
    #     if not self.fasta:
    #         raise ValueError("No database FASTA provided")
    #     # TODO: Bounds checking
    #     s = self.fasta[seq.name][seq.start-1-flank:seq.end+flank]
    #     if seq.strand == -1:
    #         s = s.complement
    #     return StoSequence(seq.name, seq.start-flank, seq.end+flank, str(s), seq.strand)
    

if __name__ == '__main__':
    import sys
    sr = SearchResult.parse(sys.argv[1])
