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
class Stockholm:
    """ Represents a Stockholm file. """
    
    msa: 'dict[str, StoSequence]'
    glob_features: 'dict[str, dict[str, list[StoFeature]]]'
    seq_features: 'dict[str, dict[str, dict[str, list[StoFeature]]]]'
    path: str = None
    
    @property
    def SS_cons(self):
        return self.glob_features['GC']['SS_cons'][0].text

    @staticmethod
    def parse(path: str):
        """ Parse a Stockholm file. """

        glob_features = defaultdict(lambda: defaultdict(list))
        seq_features = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        msa: dict[str, StoSequence] = {}

        with open(path) as f:
            if (header := f.readline()) != '# STOCKHOLM 1.0\n':
                raise StockholmError("Invalid Stockholm header")
        
            for i, line in enumerate(f):
                line = StoLine.parse(line.strip(), i)

                if line is None or isinstance(line, StoComment) or (end := isinstance(line, StoEnd)):
                    # An empty line indicates the end of a block (ignored)

                    # An end line indicates the end of the file
                    if end:
                        break
                elif isinstance(line, StoFeature):
                    if line.fmt == 'GF' or line.fmt == 'GC':
                        # Global feature
                        glob_features[line.fmt][line.field].append(line)
                    else:
                        # Sequence feature
                        seq_features[line.fmt][line.seqname][line.field].append(line)
                else:
                    # Sequence
                    if line.seqname not in msa:
                        msa[line.seqname] = line
                    else:
                        msa[line.seqname].text += line.text
        
        return Stockholm(msa, glob_features, seq_features, path)


if __name__ == '__main__':
    import sys
    sto = Stockholm.parse(sys.argv[1])
    print(sto.SS_cons)
