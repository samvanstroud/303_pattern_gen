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


def is_short_ABL3(filename):
    with open(filename) as file:
        for line in file:
            if ';' not in line.rstrip('\n'):
                n_cols = len(line.split(' '))
                break
    
    if n_cols == 4:
        return True
    else:
        return False


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
                      

def convert_ABL3_short(filename):
    """
    Convert an ABL3 pattern with columns 'note', 'gate', 'slide', 'accent'
    into common pattern representation.
    """

    pat = load_ABL3_short(filename)

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


def load_ABL3_long(filename):
    """
    Load ABL3 pattern with columns: 'note', 'down', 'up', 'accent', 'slide', 'gate'
    """
    with open(filename) as file:
        n_skip = sum([';' in line.rstrip('\n') for line in file])
        
    pat = pd.read_csv(filename, sep=' ', index_col=False, skiprows=n_skip, names=['note', 'down', 'up', 'accent', 'slide', 'gate'])
    pat.index += 1
    pat.index.name = 'step'

    return pat


def convert_ABL3_long(filename):
    """
    Convert an ABL3 pattern with columns 'note', 'down', 'up', 'accent', 'slide', 'gate'
    into common pattern representation.
    """

    pat = load_ABL3_long(filename)

    pat.loc[pat['note'] < 0, 'note'] += 12
    pat.loc[pat['note'] == 12, 'up'] += 1
    pat.loc[pat['note'] == 12, 'note'] = 0
    pat = pat[['note', 'up', 'down', 'gate', 'slide', 'accent']]

    return pat


def convert_ABL3(filename, out_filepath):

    if is_short_ABL3(filename):
        pat = convert_ABL3_short(filename)
    else:
        pat = convert_ABL3_long(filename)

    pat.to_csv(out_filepath)


def convert_all_ABL3(in_path, out_path):
    """
    Convert all midi files in a folder to 303 style patterns in csv.
    Files are searched for recursively.
    """
    if not os.path.exists(out_path):
        Path(out_path).mkdir(parents=True, exist_ok=True)

    for i, file in enumerate(sorted(Path(in_path).rglob('*.pat'))):
        print('converting midi file:', file)

        skip = False
        with open(file) as file_:
            for line in file_:
                if 'xml' in line:
                    skip = True
        if skip:
            continue
        
        convert_ABL3(file, out_path + str(i) + '.csv')


if __name__ == '__main__':

    convert_all_ABL3('../data/raw/ABL3', '../data/processed/ABL3/')
