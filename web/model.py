from dataclasses import dataclass, field
from collections import defaultdict
import pandas
from pyfaidx import Fasta

@dataclass
class Sequence:
    name: str
    start: int
    end: int
    seq: str
    strand: str = '+'  # + = forward, - = reverse

    @property
    def coords(self):
        return (self.start, self.end) if self.strand == 1 else (self.end, self.start)

    @staticmethod
    def from_line(line: str):
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
        
        # Add sequence to dict
        return Sequence(name, start, end, seq, strand)


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
                seq = Sequence.from_line(line)
                msa[seq.name] = seq
        return cls(msa, features, **kwargs)

    @classmethod
    def from_file(cls, path: str, **kwargs):
        with open(path) as f:
            data = f.read()
        return cls.from_data(data, **kwargs)


@dataclass
class SearchResultHit:
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
    inc: int
    description_of_target: str

    @staticmethod
    def from_row(row: pandas.Series):
        return SearchResultHit(
            target_name=row['target_name'],
            target_accession=row['target_accession'],
            query_name=row['query_name'],
            query_accession=row['query_accession'],
            mdl=row['mdl'],
            mdl_from=row['mdl_from'],
            mdl_to=row['mdl_to'],
            seq_from=row['seq_from'],
            seq_to=row['seq_to'],
            strand=row['strand'],
            trunc=row['trunc'],
            pass_=row['pass'],
            gc=row['gc'],
            bias=row['bias'],
            score=row['score'],
            E_value=row['E-value'],
            inc=row['inc'],
            description_of_target=row['description_of_target'],
        )

@dataclass
class SearchResult:
    sto: Stockholm = field(init=False)
    tbl: 'dict[str, SearchResultHit]'

    dbfna: str = None
    fasta: Fasta = field(init=False)

    def __post_init__(self):
        self.fasta = Fasta(self.dbfna)

    @staticmethod
    def from_files(sto_path: str, tbl_path: str, dbfna: str = None):
        sr = SearchResult(dbfna=dbfna)
        # Read sto
        sr.sto = Stockholm.from_file(sto_path)

        # Read tbl
        colnames = ['target_name', 'target_accession', 'query_name', 'query_accession', 'mdl', 'mdl_from', 'mdl_to', 'seq_from', 'seq_to', 'strand', 'trunc', 'pass', 'gc', 'bias', 'score', 'E-value', 'inc', 'description_of_target']
        df = pandas.read_fwf(tbl_path, comment='#', delim_whitespace=True, on_bad_lines='warn', names=colnames)
    
        # Join tbl with sto
        for i, row in df.iterrows():
            seq = sr.sto.msa.get(row['target_name'])
            hit = SearchResultHit.from_(row)
            key = f"{hit.target_name}/{hit.seq_from}-{hit.seq_to}"
            sr.tbl[key] = hit

        return sr

    def get_flank(self, seq: Sequence, flank: int):
        # TODO: Bounds checking
        s = self.fasta[seq.name][seq.start-1-flank:seq.end+flank]
        if seq.strand == -1:
            s = s.complement
        return Sequence(seq.name, seq.start-flank, seq.end+flank, str(s), seq.strand)


def main():
    # sto = parse_file('../search/sto/DUF1646/RF03071.sto')
    sr = SearchResult.from_files(
        '../search/searches/bacteria-DUF1646-6/bacteria-DUF1646-6.out.sto',
        '../search/searches/bacteria-DUF1646-6/bacteria-DUF1646-6.out.tbl',
        dbfna='/Users/julian/bioinfo/db/rs213-bact-repr/rs213-bact-repr.fna')
    
    # print(sr.msa)
    # seq = sr.msa['NZ_QFFZ01000015.1']
    seq = sr.sto.msa['NZ_BJDX01000003.1']
    flanked = sr.get_flank(seq, 0)
    print(seq)
    print(flanked)

if __name__ == '__main__':
    main()
