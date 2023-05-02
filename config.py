import os

basedir = os.path.dirname(os.path.realpath(__file__))

DATADIR = os.path.join(basedir, "data")
SEARCHES_DIR = os.path.join(DATADIR, "searches")
ANALYSIS_DIR = os.path.join(DATADIR, "analysis")
REFOLD_DIR = os.path.join(DATADIR, "refold")
STO_DIR = os.path.join(DATADIR, "sto")

SCRIPTS_DIR = os.path.join(basedir, "jps/scripts")


# Create directories if they don't exist
os.makedirs(SEARCHES_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)
os.makedirs(REFOLD_DIR, exist_ok=True)

# Database paths
GTDB_PROK_DB = "/gpfs/gibbs/pi/breaker/cgkdb/gtdb/gtdb-bact-r207-repr.fna.gz"


# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "data.sqlite")}'


