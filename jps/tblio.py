"""
tblio.py

This module contains classes for parsing and working with cmsearch result tables.
"""
from dataclasses import dataclass, field


class TableError(Exception):
    """ Errors related to table file formatting. """


TBLHEADERS = ['target_name', 'target_accession', 'query_name', 'query_accession', 
              'mdl', 'mdl_from', 'mdl_to', 'seq_from', 'seq_to', 'strand', 'trunc', 
              'pass', 'gc', 'bias', 'score', 'E_value', 'inc', 'description_of_target']


@dataclass
class SearchResultRow:
    """ Represents a single row in a cmsearch result table. """

    id: int
    acn: str
    start: int
    end: int
    strand: str
    score: float
    E_value: float
    inc: str

    @property
    def seqname(self):
        return f"{self.acn}/{self.start}-{self.end}"

    @staticmethod
    def parse(row, id_: int):
        return SearchResultRow(
            id_,
            acn=row['target_name'].strip(),
            start=int(row['seq_from']),
            end=int(row['seq_to']),
            strand=row['strand'],
            score=float(row['score']),
            E_value=float(row['E_value']),
            inc=row['inc'].strip()
        )


@dataclass
class SearchResultTable:
    rows: 'dict[str, SearchResultRow]'
    path: str = None

    @staticmethod
    def parse(path: str):
        rows = {}
        with open(path) as f:
            for i, line in enumerate(f):
                if line.startswith('#'):
                    # Skip comments
                    continue

                values = line.split(maxsplit=len(TBLHEADERS)-1)
                if len(values) != len(TBLHEADERS):
                    raise TableError(f"Expected {len(TBLHEADERS)} columns, got {len(values)} at line {i}")

                row = SearchResultRow.parse(dict(zip(TBLHEADERS, values)), i)
                rows[row.seqname] = row
        
        return SearchResultTable(rows, path)

    # TODO: Add methods to write table to file, applying filters like inclusion threshold and no duplicates

if __name__ == '__main__':
    import sys
    SearchResultTable.parse(sys.argv[1])
