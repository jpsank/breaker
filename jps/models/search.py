from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Text, select, func, and_
from sqlalchemy.orm import relationship, Mapped, column_property
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from datetime import datetime

from config import *
from jps.models import Base, Alnseq
from jps.util.slurm import *
from cgk.interval import ChrInterval


class SlurmJob(Base):
    """ Represents a Slurm job on the supercomputer cluster. """
    jobid: int = Column(Integer, primary_key=True)
    script: str = Column(String, nullable=False)
    args: str = Column(String, nullable=False)
    status: str = Column(String, nullable=False, default="RUNNING")  # RUNNING, FINISHED, CANCELLED

    # TODO: Add job start time, job end time, job duration, job output, job error?

    @staticmethod
    def submit(script: str, *args):
        """ Submit a Slurm job. """
        jobid = slurm_submit(script, *args)
        job = SlurmJob(jobid=jobid, script=script, args=" ".join(args))
        return job

    def check(self):
        """ Check the status of the Slurm job. """
        self.status = "RUNNING" if slurm_check(self.jobid) else "FINISHED"

    def cancel(self):
        """ Cancel the Slurm job. """
        if self.status == "FINISHED":
            raise ValueError("Cannot cancel a finished job.")
        slurm_cancel(self.jobid)
        self.status = "CANCELLED"

    def wait(self):
        """ Wait for the Slurm job to finish. """
        slurm_wait(self.jobid)
        self.status = "FINISHED"


class Hit(Base, ChrInterval):
    """
    Represents a single hit in a cmsearch result, consisting of data from a row in the
    cmsearch result table and the corresponding sequence in the Stockholm file.
    """

    search_id: Mapped[int] = Column(Integer, ForeignKey('Search.id'), primary_key=True)
    search: Mapped['Search'] = relationship("Search", back_populates="hits")
    rank: int = Column(Integer, primary_key=True)

    # Stockholm file properties
    alnseq_id: Mapped[int] = Column(Integer, ForeignKey('Alnseq.id'), nullable=True)
    alnseq: Mapped[Alnseq] = relationship("Alnseq", back_populates="hits")

    # DBFNA properties
    chraccn: str = Column(String(255))
    start: int = Column(Integer)
    end: int = Column(Integer)
    strand: str = Column(Boolean)
    
    # Tblstats
    evalue: float = Column(Float)
    bitscore: float = Column(Float)
    bias: float = Column(Float)
    gc: float = Column(Float)
    trunc: str = Column(String)
    mdl_from: int = Column(Integer)
    mdl_to: int = Column(Integer)

    # overlaps = column_property(
    #     select('Hit')
    #     .where(
    #         and_(
    #             'Hit'.chraccn == chraccn,
    #             'Hit'.start <= end,
    #             'Hit'.end >= start,
    #         )
    #     )
    #     .correlate_except('Hit')
    # )

    # @hybrid_method
    # def overlaps(self, other: 'Hit'):
    #     sign = 2 * (self.strand == other.strand) - 1
    #     return sign * (
    #         (self.chraccn == other.chraccn) & (not self.end < other.start) & (not self.start > other.end)
    #     )

    def asdict(self):
        return {
            'rank': self.rank,
            'alnseq': self.alnseq.alnseq if self.alnseq else None,
            'chraccn': self.chraccn,
            'start': self.start,
            'end': self.end,
            'strand': self.strand,
            'evalue': self.evalue,
            'bitscore': self.bitscore,
            'bias': self.bias,
            'gc': self.gc,
            'trunc': self.trunc,
            'mdl_from': self.mdl_from,
            'mdl_to': self.mdl_to,
        }


class Search(Base):
    """ Represents an Infernal cmsearch. """

    id: int = Column(Integer, primary_key=True)
    
    # Search parameters
    cm: str = Column(String)
    param: str = Column(String)
    target: str = Column(String)
    timestamp: DateTime = Column(DateTime, default=datetime.now)

    # Slurm job ID
    jobid: Mapped[int] = Column(Integer, ForeignKey('SlurmJob.id'))
    job: Mapped[SlurmJob] = relationship("SlurmJob", back_populates="search")

    # Search results
    hits: Mapped[list[Hit]] = relationship("Hit", back_populates="search")

    # @hybrid_property
    # def overlapping_hits(self, other: 'Search'):
    #     return self.hits.join(other.hits).filter(
    #         and_(
    #             Hit.chraccn == other.hits.chraccn,
    #             Hit.start <= other.hits.end,
    #             Hit.end >= other.hits.start,
    #         )
    #     )

    @property
    def name(self):
        cm_name = os.path.splitext(os.path.basename(self.cm))[0]
        return f"{self.id}_{cm_name}_{self.timestamp.strftime('%Y-%m-%d_%H-%M-%S')}"

    @property
    def datapath(self):
        return os.path.join("searches", self.name, f"{self.name}.out")

    def submit(self):
        """ Submit the search to Slurm. """
        self.job = SlurmJob.submit(
            os.path.join(SCRIPTS_DIR, "cmsearch.sh"), 
            self.cm, self.datapath, self.target, self.param,
        )
        self.job.submit()

