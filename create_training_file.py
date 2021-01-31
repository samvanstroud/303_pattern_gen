"""
    Combine 303 patterns into a single file.
    Author: @samvanstroud

    Usage:
    - set paths at the end of the script.
    - run `python create_training_file.py`.
"""

import os
import math
import random
from pathlib import Path

import numpy as np
import pandas as pd


def load_pattern(filepath):
    pat = pd.read_csv(filepath)
    return pat

def tokenize_pattern(pat, with_note=True):
    if with_note:
        seperators = ['!', '$', '#', '&', '%', '=']
    else:
        seperators = ['$', '#', '&', '%', '=']
    s = ''

    for i, row in pat.iterrows():
        for sep, col in zip(seperators, pat.columns[1:]):
            s += str(row[col]) + sep

        s += '\n'

    return  s


def note_string(pat):
    return ''.join(pat['note'].tolist())


def dump_patterns(in_path, out_filename, order=1):
    """
    Tokenize and dump all 303 patterns in `in_path` to a single txt file.
    """
    #if not os.path.exists(out_path):
    #    Path(out_path).mkdir(parents=True, exist_ok=True)
    num = 0
    with open(out_filename, 'w') as out_file:
        paths = sorted(Path(in_path).rglob('*.csv'))
        for i, file in enumerate(paths):
            for j in range(order):
                
                print('converting pattern file', i, 'at', file)
                pat = load_pattern(file)

                if j != 0:
                    pat2 = pd.DataFrame()
                    for k in range(10):
                        pat2 = load_pattern(random.choice(paths))
                        if len(pat2) == len(pat): 
                            break
                    if len(pat2) != len(pat):
                        continue
                    pat.note = pat2.note

                #if len(pat) > 4:
                #    continue
                # repeat until 16 steps
                pat = pd.concat([pat] * max(1,math.floor(16 / len(pat))))
                if len(pat) != 16:
                    pat = pat.iloc[:16]

                pat_str = tokenize_pattern(pat.drop(columns=['note']), with_note=False)

                #pat_str = note_string(pat)

                out_file.write(pat_str)
                out_file.write('~\n')
                #out_file.write('~')
                num += 1
    print(num, 'total patterns.')




if __name__ == "__main__":
    dump_patterns('../data/processed/', '../Aicd/meta_patterns.txt', order=1)
    filepath = '../data/processed/midi/1.csv'
