"""
    Combine 303 patterns into a single file.
    Author: @samvanstroud

    Usage:
    - set paths at the end of the script.
    - run `python create_training_file.py`.
"""

from pathlib import Path
import os

import numpy as np
import pandas as pd


def load_pattern(filepath):
    pat = pd.read_csv(filepath)
    return pat

def tokenize_pattern(pat):
    seperators = ['!', '#', '$', '&', '%', '=']
    s = ''

    for i, row in pat.iterrows():
        for sep, col in zip(seperators, pat.columns[1:]):

            s += str(row[col]) + sep
        s += '\n'

    return  s


def dump_patterns(in_path, out_filename):
    """
    Tokenize and dump all 303 patterns in `in_path` to a single txt file.
    """
    #if not os.path.exists(out_path):
    #    Path(out_path).mkdir(parents=True, exist_ok=True)
    with open(out_filename, 'w') as out_file:
        for i, file in enumerate(sorted(Path(in_path).rglob('*.csv'))):
            print('converting pattern file:', file)
            pat = load_pattern(file)
            pat_str = tokenize_pattern(pat)

        
            out_file.write(pat_str)
            out_file.write('~\n')


if __name__ == "__main__":
    dump_patterns('../data/processed/', '../data/input_patterns.txt')
    filepath = '../data/processed/midi/1.csv'
