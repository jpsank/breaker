import os

basedir = os.path.dirname(os.path.realpath(__file__))

DATA_DIR = os.path.join(basedir, "data")
SEARCHES_DIR = os.path.join(DATA_DIR, "searches")
ANALYSIS_DIR = os.path.join(DATA_DIR, "analysis")
REFOLD_DIR = os.path.join(DATA_DIR, "refold")
STO_DIR = os.path.join(DATA_DIR, "sto")

SCRIPTS_DIR = os.path.join(basedir, "jps/scripts")


# Create directories if they don't exist
if not os.path.exists(SEARCHES_DIR):
    os.makedirs(SEARCHES_DIR)
if not os.path.exists(ANALYSIS_DIR):
    os.makedirs(ANALYSIS_DIR)
if not os.path.exists(REFOLD_DIR):
    os.makedirs(REFOLD_DIR)
