import pandas
import sys

num = 6
if len(sys.argv) > 1:
    num = int(sys.argv[1])
tbl1 = f"searches/bacteria-DUF1646-{num}/bacteria-DUF1646-{num}.out.tbl"
tbl2 = f"searches/bacteria-nhaA-I-{num}/bacteria-nhaA-I-{num}.out.tbl"

def read_tbl(fp):
    df = pandas.read_table(fp, comment='#', delim_whitespace=True, on_bad_lines='skip')
    df = df.iloc[:, [0, 7, 8]]
    df.columns = ['target name', 'seq from', 'seq to']
    return df

df1 = read_tbl(tbl1)
df2 = read_tbl(tbl2)

# Get target names that are in both tbl1 and tbl2
targets = set(df1['target name']).intersection(set(df2['target name']))

if not targets:
    print("compare.py: No target names in common.")
    exit()
else:
    print(f"compare.py: {len(targets)} target names in common.")

threshold = 1000
for target in targets:
    df1_target = df1[df1['target name'] == target]
    df2_target = df2[df2['target name'] == target]
    for i, row1 in df1_target.iterrows():
        for j, row2 in df2_target.iterrows():
            from1, to1 = row1['seq from'], row1['seq to']
            from2, to2 = row2['seq from'], row2['seq to']
            if from1 > to1: from1, to1 = to1, from1
            if from2 > to2: from2, to2 = to2, from2
            if abs(from1-from2) < threshold or abs(to1-to2) < threshold:
                print(f"compare.py: Potential intersect at {target}, 1:{from1}-{to1} 2:{from2}-{to2}")

