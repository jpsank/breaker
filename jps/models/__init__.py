from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from config import *

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
Base.metadata.create_all(bind=engine)

from jps.models.search import Search, Hit, SlurmJob
from jps.models.alnseq import Alnseq, StoFeature, Stockholm