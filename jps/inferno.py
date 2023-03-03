"""
inferno.py

Infernal (cmsearch) output parser.
"""

from dataclasses import dataclass, field
from collections import defaultdict
import pandas
from pyfaidx import Fasta

from jps.iosto import Stockholm, StoSequence
from jps.tblio import SearchResultRow, SearchResultTable


@dataclass
class SearchResultHit:
    """
    Represents a single hit in a cmsearch result, consisting of a row in the
    cmsearch result table and the corresponding sequence in the Stockholm file.
    """

    id: int
    acn: str
    start: int
    end: int
    strand: str

    # Sequence from Stockholm file
    text: str

    # Scores from cmsearch result table
    score: float
    E_value: float
    inc: str

    @staticmethod
    def create(row: SearchResultRow, seq: StoSequence, id_: int):
        return SearchResultHit(
            id=id_,
            acn=row.acn,
            start=row.start,
            end=row.end,
            strand=row.strand,
            score=row.score,
            E_value=row.E_value,
            inc=row.inc,
            text=seq.text if seq else None
        )

    @property
    def seqname(self):
        return f"{self.acn}/{self.start}-{self.end}"

    def coords(self):
        return (self.start, self.end)

    def eslcoords(self):
        return (self.start, self.end) if self.strand == '+' else (self.end, self.start)


@dataclass
class SearchResult:
    """ Represents the results of a cmsearch. """

    sto: Stockholm
    tbl: SearchResultTable
    hits: 'dict[str, SearchResultHit]'
    dbfna_path: str = None

    fasta: Fasta = field(init=False)
    def __post_init__(self):
        if self.dbfna_path:
            self.fasta = Fasta(self.dbfna_path)

    @staticmethod
    def parse(path: str, dbfna_path: str = None):
        """ Parse cmsearch output files. """

        # Parse Stockholm file
        sto = Stockholm.parse(f"{path}.sto")

        # Parse tbl file
        tbl = SearchResultTable.parse(f"{path}.tbl")

        # Create hits
        hits = {}
        for i, (seqname, row) in enumerate(tbl.rows.items()):
            hits[seqname] = SearchResultHit.create(row, sto.msa.get(seqname), i)

        return SearchResult(sto, tbl, hits, dbfna_path=dbfna_path)

    # def get_flank(self, seq: StoSequence, flank: int):
    #     if not self.fasta:
    #         raise ValueError("No database FASTA provided")
    #     # TODO: Bounds checking
    #     s = self.fasta[seq.name][seq.start-1-flank:seq.end+flank]
    #     if seq.strand == -1:
    #         s = s.complement
    #     return StoSequence(seq.name, seq.start-flank, seq.end+flank, str(s), seq.strand)

    def to_dataframe(self):
        return pandas.DataFrame([h.__dict__ for h in self.hits.values()])
    

if __name__ == '__main__':
    import sys
    sr = SearchResult.parse(sys.argv[1])
    print(sr.to_dataframe())
