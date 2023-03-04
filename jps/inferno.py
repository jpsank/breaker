"""
inferno.py

Infernal (cmsearch) output parser.
"""

from dataclasses import dataclass, field
from collections import defaultdict
import pandas
from pyfaidx import Fasta

from jps.iosto import Stockholm, StoSequence


class InfernoError(Exception):
    """ Errors related to processing Infernal output. """


TBLHEADERS = ['target_name', 'target_accession', 'query_name', 'query_accession', 
              'mdl', 'mdl_from', 'mdl_to', 'seq_from', 'seq_to', 'strand', 'trunc', 
              'pass', 'gc', 'bias', 'score', 'E_value', 'inc', 'description_of_target']


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
    def parse(row: dict, sto: Stockholm, id_: int):
        acn = row['target_name'].strip()
        seq = sto.msa.get(acn)
        return SearchResultHit(
            id_,
            acn=acn,
            start=int(row['seq_from']),
            end=int(row['seq_to']),
            strand=row['strand'],
            text=seq.text if seq else None,
            score=float(row['score']),
            E_value=float(row['E_value']),
            inc=row['inc'].strip()
        )

    @property
    def seqname(self):
        return f"{self.acn}/{self.start}-{self.end}"

    def coords(self):
        return (self.start, self.end)

    def eslcoords(self):
        return (self.start, self.end) if self.strand == '+' else (self.end, self.start)

    def __str__(self):
        return f"{self.seqname} ({self.strand})"


@dataclass
class SearchResult:
    """ Represents the results of a cmsearch. """

    sto: Stockholm
    hits: 'dict[str, SearchResultHit]'
    tbl_path: str = None
    dbfna_path: str = None

    fasta: Fasta = field(init=False)
    def __post_init__(self):
        if self.dbfna_path:
            self.fasta = Fasta(self.dbfna_path)

    @staticmethod
    def parse(path: str, dbfna_path: str = None):
        # Parse Stockholm file
        sto = Stockholm.parse(f"{path}.sto")

        # Parse tbl file
        hits = {}
        with open(tbl_path := f"{path}.tbl") as f:
            for i, line in enumerate(f):
                if line.startswith('#'):
                    # Skip comments
                    continue

                values = line.split(maxsplit=len(TBLHEADERS)-1)
                if len(values) != len(TBLHEADERS):
                    raise InfernoError(f"Expected {len(TBLHEADERS)} columns, got {len(values)} at line {i}")

                hit = SearchResultHit.parse(dict(zip(TBLHEADERS, values)), sto, i)
                hits[hit.seqname] = hit
        
        return SearchResult(sto, hits, tbl_path, dbfna_path)

    def apply_threshold(self, threshold: float):
        for seqname, hit in self.hits.items():
            if hit.E_value >= threshold:
                self.sto.remove_sequence(seqname)
        self.hits = {seqname: hit for seqname, hit in self.hits.items() if hit.E_value < threshold}

    def remove_duplicates(self):
        self.sto.remove_duplicates()
        self.hits = {seqname: hit for seqname, hit in self.hits.items() if seqname in self.sto.msa}

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
