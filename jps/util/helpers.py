
from config import *

def slugify_float(f: float):
    if int(f) == f:
        return str(int(f))
    # Just convert to European format
    return str(f).replace('.', ',')

def fullpath(datapath: str):
    """ Return the full path to a data file. """
    if datapath.startswith('/'):
        return datapath
    else:
        return os.path.join(DATADIR, datapath)
