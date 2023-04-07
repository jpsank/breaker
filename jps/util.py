
from config import *

def float_to_str(f: float):
    if f.is_integer():
        return str(int(f))
    # Just convert to European format
    return str(f).replace('.', ',')


def sto_filename(path: str):
    basename = os.path.basename(path)
    if basename.endswith('.sto'):
        return basename[:-4]
    return basename
