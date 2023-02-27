from dataclasses import dataclass, field
from collections import defaultdict
import pandas
from pyfaidx import Fasta


@dataclass
class Sequence:
    name: str
    start: int
    end: int
    strand: str
    seq: str = None

    @property
    def coords(self):
        return (self.start, self.end)

    @property
    def eslcoords(self):
        return (self.start, self.end) if self.strand == '+' else (self.end, self.start)

    @property
    def esltag(self):
        return f"{self.name}/{self.start}-{self.end}"

    @staticmethod
    def from_sto_line(line: str):
        # Split into name and sequence
        parts = line.split(maxsplit=1)
        if len(parts) == 1:
            raise ValueError(f"Invalid line not in format 'name seq': {line}")
        
        # Split name into name and coordinates
        name, seq = parts
        parts = name.split('/', maxsplit=1)
        if len(parts) == 1:
            raise ValueError(f"Invalid line not in format 'name/coords seq': {line}")
        
        # Split coordinates into start and end
        name, coords = parts
        parts = coords.split('-', maxsplit=1)
        if len(parts) == 1:
            raise ValueError(f"Invalid line not in format 'name/start-end seq': {line}")
        
        # Parse coordinates to determine strand
        start, end = (int(p) for p in parts)
        strand = '+'
        if start > end:
            start, end = end, start
            seq = seq[::-1]
            strand = '-'
        
        return Sequence(name, start, end, strand, seq)


@dataclass
class Feature:
    category: str
    name: str
    value: str

    @staticmethod
    def from_line(line: str):
        # Separate feature category and rest of line
        cat, value = line[2:4], line[5:]
        if cat not in ('GF', 'GS', 'GR', 'GC'):
            raise ValueError(f"Invalid feature category not 'GC', 'GF', 'GR', or 'GS': {line}")
        
        # Split into feature name and value
        parts = value.split(maxsplit=1)
        if len(parts) == 1:
            raise ValueError(f"Invalid feature not in format 'name value': {line}")
        
        # Add feature to dict
        key, value = (p.strip() for p in parts)
        return Feature(cat, key, value)


@dataclass
class Stockholm:
    msa: 'dict[str, Sequence]'
    features: 'dict[str, dict[str, list[str]]]'

    path: str = None
    
    SS_cons: str = field(init=False)
    def __post_init__(self):
        self.SS_cons = self.features['GC']['SS_cons'][0].value

    @classmethod
    def from_data(cls, data: str, **kwargs):
        msa, features = {}, {}
        for line in data.splitlines():
            if line.startswith('#'):  # Comment
                if line.startswith('#='):  # Feature
                    feat = Feature.from_line(line)
                    if feat.category not in features: features[feat.category] = {}
                    if feat.name not in features[feat.category]: features[feat.category][feat.name] = []
                    features[feat.category][feat.name].append(feat)
            elif line and line != '//':  # Sequence
                seq = Sequence.from_sto_line(line)
                msa[seq.name] = seq
        return cls(msa, features, **kwargs)

    @classmethod
    def from_file(cls, path: str, **kwargs):
        with open(path) as f:
            data = f.read()
        return cls.from_data(data, path=path, **kwargs)


@dataclass
class SearchResultHit(Sequence):
    score: float = None
    E_value: float = None
    inc: str = None
    # duplicates: 'set[SearchResultHit]' = field(default_factory=set)

    @staticmethod
    def from_tblrow_and_sto(row: pandas.Series, sto: Stockholm):
        # TODO: row['strand'] is '' or nan when it should be '+'
        kwargs = {
            'name': row['target_name'].strip(),
            'start': int(row['seq_from']),
            'end': int(row['seq_to']),
            'strand': row['strand'],
            'score': float(row['score']),
            'E_value': float(row['E_value']),
            'inc': row['inc'].strip(),
        }
        if kwargs['strand'] == '-':
            kwargs['start'], kwargs['end'] = kwargs['end'], kwargs['start']
        
        if kwargs['inc'] == '!':
            seq = sto.msa[kwargs['name']]
            kwargs.update(seq.__dict__)
        return SearchResultHit(**kwargs)


@dataclass
class SearchResult:
    sto: Stockholm
    hits: 'dict[str, SearchResultHit]'
    tbl_path: str = None
    dbfna: str = None
    fasta: Fasta = None

    def __post_init__(self):
        if self.dbfna:
            self.fasta = Fasta(self.dbfna)
        # self.check_duplicates()

    @staticmethod
    def from_files(sto_path: str, tbl_path: str, dbfna: str = None):
        sto = Stockholm.from_file(sto_path)

        colnames = ['target_name', 'target_accession', 'query_name', 'query_accession', 'mdl', 'mdl_from', 'mdl_to', 'seq_from', 'seq_to', 'strand', 'trunc', 'pass', 'gc', 'bias', 'score', 'E_value', 'inc', 'description_of_target']
        hits = {}
        df = pandas.read_fwf(tbl_path, comment='#', delim_whitespace=True, on_bad_lines='warn', header=None, names=colnames, index_col=False, dtype=str, na_filter=False)
        for i, row in df.iterrows():
            hit = SearchResultHit.from_tblrow_and_sto(row, sto)
            hits[f"{hit.name}/{hit.start}-{hit.end}"] = hit

        return SearchResult(sto, hits, tbl_path=tbl_path, dbfna=dbfna)

    # def check_duplicates(self):
    #     for hit in self.hits.values():
    #         if hit.inc != '!':
    #             continue
    #         for other in self.hits.values():
    #             if hit is other or other.inc != '!':
    #                 continue
    #             if hit.seq == other.seq:
    #                 print(f"Duplicate hit: {hit.name}/{hit.start}-{hit.end} and {other.name}/{other.start}-{other.end}")
    #                 hit.duplicates.add(other.esltag)
    #                 other.duplicates.add(hit.esltag)

    def get_flank(self, seq: Sequence, flank: int):
        if not self.fasta:
            raise ValueError("No database FASTA provided")
        # TODO: Bounds checking
        s = self.fasta[seq.name][seq.start-1-flank:seq.end+flank]
        if seq.strand == -1:
            s = s.complement
        return Sequence(seq.name, seq.start-flank, seq.end+flank, str(s), seq.strand)

    def to_dataframe(self):
        return pandas.DataFrame([h.__dict__ for h in self.hits.values()])


def main():
    # sto = parse_file('../search/sto/DUF1646/RF03071.sto')
    sr = SearchResult.from_files(
        './search/searches/gtdb-bact_DUF1646_1/gtdb-bact_DUF1646_1.out.sto',
        './search/searches/gtdb-bact_DUF1646_1/gtdb-bact_DUF1646_1.out.tbl',
    )
        # dbfna='/Users/julian/bioinfo/db/rs213-bact-repr/rs213-bact-repr.fna')
    
    seq = sr.sto.msa['NZ_AUUU01000100.1']
    flanked = sr.get_flank(seq, 0)
    print(seq)
    print(flanked)

if __name__ == '__main__':
    main()
