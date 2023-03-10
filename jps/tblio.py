"""
tblio.py

This module contains classes for parsing and working with cmsearch result tables.
"""
from dataclasses import dataclass, field


class TableError(Exception):
    """ Errors related to table file formatting. """


# Column headers for cmsearch result table
TBLHEADERS = ['target_name', 'target_accession', 'query_name', 'query_accession', 
              'mdl', 'mdl_from', 'mdl_to', 'seq_from', 'seq_to', 'strand', 'trunc', 
              'pass_', 'gc', 'bias', 'score', 'E_value', 'inc', 'description_of_target']


@dataclass
class SearchResultRow:
    """ Represents a single row in a cmsearch result table. """

    id: int
    
    # Columns from cmsearch result table (see TBLHEADERS)
    target_name: str
    target_accession: str
    query_name: str
    query_accession: str
    mdl: str
    mdl_from: int
    mdl_to: int
    seq_from: int
    seq_to: int
    strand: str
    trunc: str
    pass_: str
    gc: float
    bias: float
    score: float
    E_value: float
    inc: str
    description_of_target: str

    def coords(self):
        return (self.seq_from, self.seq_to)

    def seqname(self):
        return f"{self.target_name}/{self.seq_from}-{self.seq_to}"

    def eslcoords(self):
        return (self.seq_from, self.seq_to) if self.strand == '+' else (self.seq_to, self.seq_from)

    def esltag(self):
        start, end = self.eslcoords()
        return f"{self.target_name}/{start}-{end}"

    @staticmethod
    def parse(values, id_: int):
        return SearchResultRow(
            id_,
            **{k: (SearchResultRow.__annotations__[k])(values[i].strip()) for i, k in enumerate(TBLHEADERS)}
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
                if line.startswith('#'): continue  # Skip comments

                # Split line into columns
                values = line.split(maxsplit=len(TBLHEADERS)-1)
                if len(values) != len(TBLHEADERS):
                    raise TableError(f"Expected {len(TBLHEADERS)} columns, got {len(values)} at line {i}")

                # Parse row and add to table
                row = SearchResultRow.parse(values, i)
                rows[row.seqname()] = row
        
        return SearchResultTable(rows, path)

    def copy(self):
        return SearchResultTable({k: v for k, v in self.rows.items()}, self.path)

    def remove_row(self, seqname: str):
        del self.rows[seqname]
    
    def write(self, path: str):
        colwidths = {
            h: max(
                len(h) + (1 if i == 0 else 0),  # Add 1 to first column for # symbol
                *(len(str(getattr(row, h))) for row in self.rows.values())
                )
            for i, h in enumerate(TBLHEADERS)}
        with open(path, 'w') as f:
            f.write(' '.join(f'{("#" + h if i == 0 else h): <{colwidths[h]}}' for i, h in enumerate(TBLHEADERS)) + "\n")
            for row in self.rows.values():
                f.write(' '.join([f"{getattr(row, h):<{colwidths[h]}}" for h in TBLHEADERS]) + "\n")


if __name__ == '__main__':
    import sys
    tbl = SearchResultTable.parse(sys.argv[1])
    print(tbl.rows)