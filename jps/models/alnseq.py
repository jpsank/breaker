from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, DeclarativeBase

from config import *


class Alnseq(DeclarativeBase):
    """ Represents a sequence in a Stockholm file. """

    id: int = Column(Integer, primary_key=True)
    stockholm_id: Mapped[int] = Column(Integer, ForeignKey('stockholm.id'))
    stockholm: Mapped['Stockholm'] = relationship('Stockholm')

    alnseq: str = Column(Text)


class StoFeature(DeclarativeBase):
    """ Represents a feature in a Stockholm file. """

    id: int = Column(Integer, primary_key=True)
    stockholm_id: int = Column(Integer, ForeignKey('Stockholm.id'))
    stockholm: 'Stockholm' = relationship('Stockholm')

    # If feature is associated with a sequence
    alnseq_id: int = Column(Integer, ForeignKey('Alnseq.id'), nullable=True)
    alnseq: Alnseq = relationship('Alnseq')

    field: str = Column(String(255))
    text: str = Column(Text)
    fmt: str = Column(String(2))  # GF, GS, GC, GR


class Stockholm(DeclarativeBase):
    """ Represents a Stockholm file, including its alignment and features. """

    datapath: str = Column(String(255), unique=True)
    alnseqs: Mapped[list[Alnseq]] = relationship('Alnseq', backref='stockholm')
    features: Mapped[list[StoFeature]] = relationship('Feature', backref='stockholm')
