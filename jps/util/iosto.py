"""
iosto.py

Module for handling Stockholm file i/o.
"""

from dataclasses import dataclass, field
from collections import defaultdict
import os

from cgk.interval import ChrInterval

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
class StoFeature:
    """ Represents a feature in a Stockholm file. """    
    esltag: str  # If sequence feature
    field: str
    text: str
    fmt: str  # GF, GS, GC, GR


@dataclass
class StoSequence(ChrInterval):
    """ Represents a sequence in a Stockholm file. """
    chraccn: str
    start: int
    end: int
    strand: str
    alnseq: str


def sto_parseline(line: str):
    """
    Factory for parsing a line from a Stockholm file.
    Returns a StoFeature, StoSequence, or comment line.
    """
    if len(line) == 0:  # Empty line
        return ''
    elif line.startswith('#='):  # Feature line
        fmt = line[2:4]
        if fmt == 'GF' or fmt == 'GC':  # GF and GC lines have no sequence name
            field, text = line.split(maxsplit=2)[1:]
            return StoFeature(text=text, fmt=fmt, esltag=None, field=field)
        elif fmt == 'GS' or fmt == 'GR':  # GS and GR lines have a sequence name
            esltag, field, text = line.split(maxsplit=3)[1:]
            return StoFeature(text=text, fmt=fmt, esltag=esltag, field=field)
        else:
            raise StockholmError(f"Invalid Stockholm line of unknown format '{fmt}': {line}")
    elif line.startswith('#') or line == '//':  # Comment or end of alignment
        return line
    else:  # Sequence line
        esltag, alnseq = line.split(maxsplit=1)
        chraccn, coords = esltag.split('/')
        start, end = (int(p) for p in coords.split('-'))
        strand = '-' if start > end else '+'
        return StoSequence(text=alnseq, chraccn=chraccn, start=start, end=end, strand=strand)


def sto_read(path: str) -> tuple[dict[str, StoSequence], list[StoFeature]]:
    """ Parse a Stockholm file. """
    features: list[StoFeature] = []
    sequences: dict[str, StoSequence] = {}
    with open(path) as f:
        if (header := f.readline()) != '# STOCKHOLM 1.0\n':
            raise StockholmError("Invalid Stockholm header")
    
        for i, line in enumerate(f):
            line = sto_parseline(line.strip(), i)

            if isinstance(line, str):
                # An empty line indicates the end of a block
                # An end line indicates the end of the file
                if line == '//':
                    break
            elif isinstance(line, StoFeature):
                features.append(line)
            elif isinstance(line, StoSequence):
                if line.esltag in sequences:
                    sequences[line.esltag].alnseq += line.alnseq
                else:
                    sequences[line.esltag] = line
    
    return sequences, features


def sto_write(sequences: dict[str, StoSequence], features: list[StoFeature], path: str):
    """ Write a Stockholm file. """
    width = max(len(seq.esltag) for seq in sequences)

    with open(path, 'w') as f:
        f.write('# STOCKHOLM 1.0\n')

        # Write global features at the top and record other features
        above = ""
        below = ""
        gr: dict[str, list[StoFeature]] = defaultdict(list)
        for feat in features:
            if feat.fmt == 'GF':
                f.write(f'#=GF {feat.field} {feat.text}\n')
            elif feat.fmt == 'GS':
                above += f'#=GS {feat.esltag: <{width + 3}} {feat.field} {feat.text}\n'
            elif feat.fmt == 'GC':
                below += f'#=GC {feat.field: <{width + 3}} {feat.text}\n'
            elif feat.fmt == 'GR':
                gr[feat.esltag].append(feat)

        # Write sequence features above alignment
        f.write(above)

        # Write aligned sequences and sequence comments
        for seq in sequences.values():
            f.write(f'{seq.esltag: <{width + 8}} {seq.alnseq}\n')
            for feat in gr[seq.esltag]:
                f.write(f'#=GR {seq.esltag: <{width}} {feat.field} {feat.text}\n')

        # Write global comments at the bottom
        f.write(below)

        f.write('//\n')

