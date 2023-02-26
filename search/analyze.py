import pandas
import sys
import matplotlib.pyplot as plt
import numpy as np

from parse import df1, df2

# Counts above threshold (E-value < 0.01)
inc1 = df1[df1['inc'] == '!']
inc2 = df2[df2['inc'] == '!']
print(f"Number of DUF1646 hits above threshold: {len(inc1)}")
print(f"Number of nhaA-I hits above threshold: {len(inc2)}")

inc_threshold = 0.01

def plot_score(df, name, color):
    # TODO: Get rid of duplicate sequences
    # TODO: Integrate into SearchResult class
    # Score distribution
    score = np.log(df['E-value'])
    hist = score.plot.hist(bins=20, color=color, label=name, log=True)
    # Inclusion threshold (0.01)
    hist.axvline(x=np.log(inc_threshold), color=color, linestyle='dashed')
    # Plot
    plt.title(f"{name} score distribution")
    plt.show()

plot_score(df1, 'DUF1646', 'DarkBlue')
plot_score(df2, 'nhaA-I', 'DarkGreen')

