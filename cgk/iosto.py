"""
Christopher G. King

cgksto: iosto.py

Module for handling Stockholm file i/o. Utilities used by Stockholm
"""

# Concepts
#   - The parser should catch any clear formatting errors
#   - The parser does not need to catch SS_cons errors, etc, as
#     a user can define arbitrary lines w/ arbitrary syntax; these issues
#     should be caught by the user of the syntax

import os
import sys
from pprint import pprint
from collections import deque

class StockholmError(Exception):
    """
    Errors related to Stockholm file formatting
    """
            

class StockholmLine:
    """
    Represents a single line in a Stockholm file during parsing.
    """
    __slots__ = "i fmt seqname field text".split()

    def __init__(self, i, fmt, seqname, field, text):
        self.i = i
        self.fmt = fmt
        self.seqname = seqname
        self.field = field 
        self.text = text

    def __repr__(self):
        return "%s(%d, %s, %s, %s, %s)" % (
            type(self).__name__, self.i, *self.descr, self.text)
    
    def join(self, other):
        if self.descr() != other.descr:
            raise StockholmError("Line mismatch")
        self.text += other.text

    @property
    def descr(self):
        """Format descriptor for comparing line orders"""
        return self.fmt, self.seqname, self.field

    @classmethod
    def blank(cls, i):
        """Factory for a blank line"""
        return cls(i, None, None, None, None)

    @classmethod
    def parse(cls, i, line):
        """Factory for parsing a line from a Stockholm file"""
        if len(line) == 0:
            return cls.blank(i)
        elif line[:4] == '#=GF':
            return cls(i, 'GF', None, *line.split(maxsplit=2)[1:])
        elif line[:4] == '#=GS':
            return cls(i, 'GS', *line.split(maxsplit=3)[1:])
        elif line[:4] == '#=GC':
            return cls(i, 'GC', None, *line.split(maxsplit=2)[1:])
        elif line[:4] == '#=GR':
            return cls(i, 'GR', *line.split(maxsplit=3)[1:])
        elif line[0] == '#':
            return cls(i, None, None, None, line)
        elif line == '//':
            return cls(i, None, None, None, line)
        else:
            seqname, alnseq = line.split(maxsplit=2)
            return cls(i, None, seqname, None, alnseq)
            

def read_sto(fname):
    """
    Extracts parsed content from a Stockholm file.
    """
    gf = deque()
    gs = dict()
    block = deque()
    blocks = list()
    end_of_alignment = False

    with open(fname) as f:
    
        header = f.readline()
        if header != '# STOCKHOLM 1.0\n':
            raise StockholmError("Invalid Stockholm header")
    
        for i, line in enumerate(map(lambda line: line.strip(), f), 2):

            line = StockholmLine.parse(i, line)

            # An empty line terminates a block
            if len(block) > 0 and not any(line.descr):
                block.append(line)
                if len(blocks) == 0:
                    blocklen = len(block)
                elif blocklen == len(block):
                    blocks[0].rotate(-1)
                else:
                    raise StockholmError("Unexpected end of block")
                blocks.append(block)
                block = deque()
                if line.text == '//':
                    end_of_alignment = True
                    break

            # An empty line which does not end a block
            elif not any(line.descr):
                if line.text == '//':
                    end_of_alignment = True
                    break

            # GF can occur at any time (no further processing needed)
            elif line.fmt == 'GF':
                record = line.field, line.text
                gf.append(record)

            # GS can occur at any time (check name validity after parsing)
            elif line.fmt == 'GS':
                record = line.field, line.text
                gs.setdefault(line.seqname, deque()).append(record)

            # Primary block
            elif len(blocks) == 0:
                block.append(line)
                if len(line.text) != len(block[0].text):
                    raise StockholmError("Unexpected seqlen")
                
            # Secondary blocks must be checked against primary block
            elif blocks[0][0].descr == line.descr:
                block.append(line)
                blocks[0].rotate(-1)

            else:
                raise StockholmError("Unexpected block order")

    if not end_of_alignment:
        raise StockholmError("Unexpected end of file")

    msa = dict()
    gr = dict()
    gc = dict()

    for i in range(len(blocks[0])):
        if blocks[0][0].fmt == None and blocks[0][0].seqname:
            seqname = blocks[0][0].seqname
            alnseq = ''.join(blocks[j].popleft().text for j in range(len(blocks)))
            msa[seqname] = alnseq
        elif blocks[0][0].fmt == 'GC':
            field = blocks[0][0].field
            alnseq = ''.join(blocks[j].popleft().text for j in range(len(blocks)))
            gc[field] = alnseq
        elif blocks[0][0].fmt == 'GR':
            seqname = blocks[0][0].seqname
            field = blocks[0][0].field
            alnseq = ''.join(blocks[j].popleft().text for j in range(len(blocks)))
            gr.setdefault(seqname, {})[field] = alnseq
        else:
            for j in range(len(blocks)):
                blocks[j].rotate(-1)
    
    for seqname in gs:
        if seqname not in msa:
            raise StockholmError("GS seqname %s not in alignment" % seqname)
        
    return msa, gf, gs, gr, gc

