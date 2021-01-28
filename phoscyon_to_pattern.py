"""
    Convert Phoscyon patterns to 303 style patterns.
    Author: @samvanstroud

    Usage: 
    - set paths at the end of the script.
    - run `python phoscyon_to_pattern.py`
"""

import os
import math
from pathlib import Path

import xml.etree.ElementTree as ET

import pandas as pd

from common import (
    note_value_to_char,
    note_default,
    gate_default,
    accent_default,
    tie_default,
    slide_default
)




def get_empty_pattern_df(n_steps):
    """
    Create a DataFrame representing a blank pattern with n_steps.
    """
    empty_columns={
        'note'  : [note_default]*n_steps,
        'gate'  : [gate_default]*n_steps,
        'accent': [accent_default]*n_steps,
        'slide' : [slide_default]*n_steps,
    }

    index = pd.Index(range(1, n_steps+1), name='step')
    df = pd.DataFrame(empty_columns, index=index)

    return df


def process_phoscyon_pattern(phos):
    pat = get_empty_pattern_df(len(phos))
    for i, step in enumerate(phos):
        note = int(step.attrib['note'])
        down = int(step.attrib['octaveDown'])
        up   = int(step.attrib['octaveUp'])
        if down == up:
            down = up = 0
        if note < 0:
            n_oct = math.ceil(abs(note) / 12)
            note += 12*n_oct
            down += n_oct
        elif note >= 12:
            n_oct = math.floor(abs(note) / 12)
            note -= 12*n_oct
            up += 1

        pat.loc[i+1, 'note'] = note
        pat.loc[i+1, 'down'] = int(down)
        pat.loc[i+1, 'up']   = int(up)

        pat.loc[i+1, 'gate']   = int(step.attrib['gate'])
        pat.loc[i+1, 'slide']  = int(step.attrib['slide'])
        pat.loc[i+1, 'accent'] = int(step.attrib['accent'])

    pat = pat.astype(int)
    pat = pat[['note', 'up', 'down', 'gate', 'slide', 'accent']]
    
    return pat

def process_phoscyon_patterns(filename, out_path):
    if not os.path.exists(out_path):
        Path(out_path).mkdir(parents=True, exist_ok=True)

    tree = ET.parse(filename)
    root = tree.getroot()
    for i, child in enumerate(root):
        print('Processing pattern', i)
        pat = process_phoscyon_pattern(child)
        pat.to_csv(os.path.join(out_path, str(i) + '.csv'))


if __name__ == "__main__":
    in_path  = '../data/raw/phoscyon_default.phptrb'
    out_path = '../data/processed/phoscyon/'
    process_phoscyon_patterns(in_path, out_path)
