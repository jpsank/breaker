import os

basedir = os.path.dirname(os.path.realpath(__file__))

DATA_DIR = os.path.join(basedir, "data")
SEARCHES_DIR = os.path.join(DATA_DIR, "searches")
ANALYSIS_DIR = os.path.join(DATA_DIR, "analysis")
REFOLD_DIR = os.path.join(DATA_DIR, "refold")
STO_DIR = os.path.join(DATA_DIR, "sto")

SCRIPTS_DIR = os.path.join(basedir, "jps/scripts")


# Create directories if they don't exist
os.makedirs(SEARCHES_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)
os.makedirs(REFOLD_DIR, exist_ok=True)
