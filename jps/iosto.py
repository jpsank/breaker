"""
iosto.py

Module for handling Stockholm file i/o.
"""

from dataclasses import dataclass, field
from collections import defaultdict

# Stockholm line formats:
#   GF:   Global feature
#   GS:   Sequence feature
#   GC:   Global comment
#   GR:   Sequence comment
#   #:    Comment
#   //:   End of alignment
#   else: Sequence


class StockholmError(Exception):
    """ Errors related to Stockholm file formatting. """


@dataclass
class StoLine:
    """ Represents a single line in a Stockholm file during parsing. """

    id: int
    text: str
    fmt: str = None
    seqname: str = None
    field: str = None

    @staticmethod
    def parse(line: str, id_: int) -> 'StoLine':
        """ Factory for parsing a line from a Stockholm file. """

        if len(line) == 0:
            return None
        elif line.startswith('#='):
            fmt = line[2:4]
            if fmt == 'GF' or fmt == 'GC':
                # GF and GC lines have no sequence name
                seqname = None
                field, text = line.split(maxsplit=2)[1:]
            elif fmt == 'GS' or fmt == 'GR':
                # GS and GR lines have a sequence name
                seqname, field, text = line.split(maxsplit=3)[1:]
            else:
                raise StockholmError(f"Invalid Stockholm line of unknown format '{fmt}': {line}")
            return StoFeature(id_, text=text, fmt=fmt, seqname=seqname, field=field)
        elif line.startswith('#'):
            return StoComment(id_, text=line)
        elif line == '//':
            return StoEnd(id_, text=line)
        else:
            seqname, alnseq = line.split(maxsplit=1)

            # Split seqname into accession and coordinates (TODO: Error handling?)
            acn, coords = seqname.split('/')
            start, end = (int(p) for p in coords.split('-'))

            # Determine strand
            strand = '-' if start > end else '+'
            
            return StoSequence(id_, text=alnseq, seqname=seqname, 
                               acn=acn, start=start, end=end, strand=strand)

@dataclass
class StoComment(StoLine):
    """ Represents a comment in a Stockholm file. """

@dataclass
class StoEnd(StoLine):
    """ Represents the end of an alignment in a Stockholm file. """

@dataclass
class StoSequence(StoLine):
    """ Represents a sequence in a Stockholm file. """

    acn: str = None
    start: int = None
    end: int = None
    strand: str = None


@dataclass
class StoFeature(StoLine):
    """ Represents a feature in a Stockholm file. """


@dataclass
class FeatureSet:
    # Global features
    gf: 'dict[str, StoFeature]' = field(default_factory=defaultdict)
    gc: 'dict[str, StoFeature]' = field(default_factory=defaultdict)
    
    # Sequence features
    gs: 'dict[str, dict[str, StoFeature]]' = field(default_factory=lambda: defaultdict(lambda: defaultdict(str)))
    gr: 'dict[str, dict[str, StoFeature]]' = field(default_factory=lambda: defaultdict(lambda: defaultdict(str)))

    def add(self, feat: StoFeature):
        if feat.fmt == 'GF' or feat.fmt == 'GC':
            features = self.gf if feat.fmt == 'GF' else self.gc
            if feat.field in features:
                features[feat.field].text += feat.text
            else:
                features[feat.field] = feat
        elif feat.fmt == 'GS' or feat.fmt == 'GR':
            features = self.gs if feat.fmt == 'GS' else self.gr
            if feat.field in features[feat.seqname]:
                features[feat.seqname][feat.field].text += feat.text
            else:
                features[feat.seqname][feat.field] = feat
        else:
            raise StockholmError(f"Invalid feature format '{feat.fmt}'")

    def copy(self):
        """ Return a copy of the feature set. """
        return FeatureSet(self.gf.copy(), self.gc.copy(), self.gs.copy(), self.gr.copy())

    def remove_seq(self, seqname: str):
        """ Remove a sequence from the feature set. """
        if seqname in self.gs:
            del self.gs[seqname]
        if seqname in self.gr:
            del self.gr[seqname]

@dataclass
class Stockholm:
    """ Represents a Stockholm file, including its alignment and features. """
    
    msa: 'dict[str, StoSequence]'
    features: FeatureSet
    path: str = None
    
    @property
    def SS_cons(self):
        return self.features.gc['SS_cons'][0].text

    @staticmethod
    def parse(path: str):
        """ Parse a Stockholm file. """

        msa: dict[str, StoSequence] = {}
        features = FeatureSet()

        with open(path) as f:
            if (header := f.readline()) != '# STOCKHOLM 1.0\n':
                raise StockholmError("Invalid Stockholm header")
        
            for i, line in enumerate(f):
                line = StoLine.parse(line.strip(), i)

                if line is None or isinstance(line, StoComment) or (end := isinstance(line, StoEnd)):
                    # An empty line indicates the end of a block

                    # An end line indicates the end of the file
                    if end:
                        break
                elif isinstance(line, StoFeature):
                    # Feature
                    features.add(line)
                else:
                    # Sequence
                    if line.seqname not in msa:
                        msa[line.seqname] = line
                    else:
                        msa[line.seqname].text += line.text
        
        return Stockholm(msa, features, path)

    def copy(self):
        """ Return a copy of the Stockholm object. """
        return Stockholm(self.msa.copy(), self.features.copy(), self.path)

    def remove_seq(self, seqname: str):
        """ Remove a sequence from the alignment. """
        if seqname in self.msa:
            del self.msa[seqname]
        self.features.remove_seq(seqname)

    def write(self, path: str):
        """ Write a Stockholm file. """
        width = max(len(seq.seqname) for seq in self.msa.values())

        with open(path, 'w') as f:
            f.write('# STOCKHOLM 1.0\n')

            # Write global features at the top
            for field, line in self.features.gf.items():
                f.write(f'#=GF {field} {line.text}\n')

            # Write sequence features above alignment
            for seqname in self.features.gs:
                for field, line in self.features.gs[seqname].items():
                    f.write(f'#=GS {seqname: <{width + 3}} {field} {line.text}\n')

            # Write aligned sequences and sequence comments
            for seqname, seq in self.msa.items():
                f.write(f'{seqname: <{width + 8}} {seq.text}\n')
                if seqname in self.features.gr:
                    for field, line in self.features.gr[seqname].items():
                        f.write(f'#=GR {seqname: <{width}} {field} {line.text}\n')

            # Write global comments at the bottom
            for field, line in self.features.gc.items():
                f.write(f'#=GC {field: <{width + 3}} {line.text}\n')

            f.write('//\n')

if __name__ == '__main__':
    import sys
    sto = Stockholm.parse(sys.argv[1])
    print(sto.SS_cons)
