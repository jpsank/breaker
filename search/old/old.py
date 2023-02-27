import pandas
import sys

num = 6
if len(sys.argv) > 1: num = int(sys.argv[1])
tbl1 = f"searches/bacteria-DUF1646-{num}/bacteria-DUF1646-{num}.out.tbl"
tbl2 = f"searches/bacteria-nhaA-I-{num}/bacteria-nhaA-I-{num}.out.tbl"

def read_tbl(fp):
    df = pandas.read_fwf(fp, comment='#', delim_whitespace=True, on_bad_lines='warn')
    df = df.iloc[:, [0, 14, 15, 16]]
    df.columns = ['target name', 'score', 'E-value', 'inc']
    return df

df1 = read_tbl(tbl1)
df2 = read_tbl(tbl2)
