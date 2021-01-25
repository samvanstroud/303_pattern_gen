"""
    Convert ABL3 patterns to common 303 formatt.
    Author: @samvanstroud

    Usage: 
"""

from pathlib import Path
import os

import numpy as np
import pandas as pd

from common import note_value_to_char


def load_ABL3_short(filename):
    """
    Load ABL3 pattern with columns: 'note', 'gate', 'slide', 'accent'
    """
    with open(filename) as file:
        n_skip = sum([';' in line.rstrip('\n') for line in file])
        
    pat = pd.read_csv(filename, sep=' ', index_col=False, skiprows=n_skip, names=['note', 'gate', 'slide', 'accent'])
    pat.index += 1
    pat.index.name = 'step'

    return pat



def convert_abl3_note_to_char(note):
    """
    Convert ABL3 short pattern note format to single character:
    - c- -> C
    - c# -> d
    """
    if note[1] == '-':
        return note[0].upper()
    elif note[1] == '#':
        indices = list(note_value_to_char.keys())
        values = list(note_value_to_char.values())
        return values[values.index(note[0].upper()) + 1]
                      

def convert_ABL3_short(pat):
    """
    Convert an ABL3 pattern with columns 'note', 'gate', 'slide', 'accent'
    into common pattern representation.
    """

    note = pat.note.map(lambda x: x[0:2])
    octave = pat.note.map(lambda x: x[2]).astype(int)
    mean_octave = int(octave.mean())
    octave = octave - mean_octave

    pat['note'] = note
    pat['up'] = np.clip(octave, 0, 4)
    pat['down'] = np.clip(octave, -4, 0).abs()
    pat = pat[['note', 'up', 'down', 'gate', 'slide', 'accent']]

    pat['note'] = pat['note'].map(convert_abl3_note_to_char)

    return pat




if __name__ == '__main__':
    filename = '../data/raw/ABL3_patterns/Acid/AcidBassline6.pat'
    pat = load_ABL3_short(filename)
    pat = convert_ABL3_short(pat)
    print(pat)
