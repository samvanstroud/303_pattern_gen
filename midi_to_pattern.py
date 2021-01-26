"""
    Convert MIDI data to 303 style patterns.
    Author: @samvanstroud

    Usage: 
    - set paths at the end of the script.
    - run `python midi_to_patttern.py`
"""

from pathlib import Path
import os

import mido
import numpy as np
import pandas as pd

from common import note_value_to_char


beats = 16
time_per_beat = 24

note_default = -1
gate_default = 0
accent_default = 0
tie_default = 0
slide_default = 0



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


def midi_to_pattern(midi, n_beats=16, debug=False):
    """
    Convert midi messages to 303 style pattern.
    """
    
    # get midi track (should just be one)
    assert(len(midi.tracks) == 1)
    track = midi.tracks[0]

    # setup
    df = get_empty_pattern_df(n_beats)
    notes_on = 0
    on_beat = 1.0
    ended = False

    # loop over midi messages
    for msg in track:
        if msg.is_meta:
            continue

        # increment time
        on_beat += msg.time / time_per_beat

        # get a new note, fill the info
        if msg.type == 'note_on':      
            
            # keep count of unfinished notes
            notes_on += 1
                
            # fill info of the new note
            df.loc[int(on_beat), 'note'] = msg.note
            df.loc[int(on_beat), 'gate'] = 1
            df.loc[int(on_beat), 'accent'] = int(msg.velocity > 126)

            # if we had a rest since the previous note
            if msg.time / time_per_beat > 0.5 and notes_on == 1:

                # calculate how long the rest was
                rest_len = int(msg.time / time_per_beat) + 1

                # loop back through steps that were rested
                for i in range(1, rest_len):
                    
                    # if we hit the beginning of the pattern,
                    # just write this new note as the first note
                    if int(on_beat) - rest_len == 0:
                        df.loc[int(on_beat) - i, 'note'] = msg.note
        
                    else: # otherwise, fill the last note played before the start of the rest
                        df.loc[int(on_beat) - i, 'note'] = df.loc[int(on_beat) - rest_len, 'note']
                    
                    # check that gate is closed for all rest steps
                    assert(df.loc[int(on_beat) - i, 'gate'] == 0)

        # finish a note
        elif msg.type == 'note_off':

            # if we hit a note off at the end of the sequence, 
            # the last note is tied
            if on_beat == n_beats + 1:
                df.loc[n_beats, 'slide'] = 1
                on_beat = n_beats + 0.5
                ended = True

            # the finished note is not the same as the note playing on this step
            if df.loc[int(on_beat), 'note'] != msg.note:

                # only one note is playing, the ending note must have lasted more
                # than one step
                if notes_on == 1 and not msg.time == 0:
                    # this steps note is still set to the default of -1, 
                    # we can fill it now
                    df.loc[int(on_beat), 'note'] = msg.note

                # loop back to find the start of this note
                # (must be at least 2 steps back)
                i = 1
                while True:
                    # read the previous step's note
                    scan_note = df.loc[int(on_beat) - i, 'note']

                    # ok to modify
                    df.loc[int(on_beat) - i, 'note'] = msg.note
                    df.loc[int(on_beat) - i, 'slide'] = 1
                    
                    # if we find the beginning of the note, break
                    if scan_note == msg.note:
                        break
                    
                    # count steps
                    i += 1

            # if we finish the just started note, there can be no tie on this step
            # (unless we already reached the end of the pattern)
            else:
                if not ended:
                    df.loc[int(on_beat), 'slide'] = 0
            
            # keep count of unfinished notes
            notes_on -= 1
        
    # sanity check
    assert(notes_on == 0)
    
    # if we didn't fill any note info, it's because of rests, forward fill
    df.loc[df['note'] == -1, 'note'] = np.NaN
    df['note'] = df['note'].fillna(method='ffill')
    df = df.astype(int)
    
    return df


def convert_note_to_note_octave(pat):
    """
    Convert absolute midi note information to relative pitch + octave offset.
    Shift note information to be based around the mean pitch. In this way, 
    patterns shifted by n octaves will be identical.
    """
    # where is the pattern located?
    mean_octave = round(pat.note.mean() / 12)
    
    # calculate relative note and octave offsets
    notes = (pat.note - 36) % 12
    octaves = np.floor( pat.note / 12).astype(int) - mean_octave

    # add / update pattern
    pat['note'] = [note_value_to_char[n] for n in notes]
    pat['up'] = np.clip(octaves, 0, 4)
    pat['down'] = np.clip(octaves, -4, 0).abs()
    pat = pat[['note', 'up', 'down', 'gate', 'slide', 'accent']]

    return pat


def convert_midi_file(midi_filepath, out_filepath):
    """
    Read a single midi file and convert to 303 style pattern.
    """    
    if not os.path.exists(midi_filepath):
        raise FileNotFoundError('Could not find file', midi_filepath)
        
    # read midi
    midi = mido.MidiFile(midi_filepath, type=0)

    # convert the midi 
    pat = midi_to_pattern(midi)
    pat = convert_note_to_note_octave(pat)

    pat.to_csv(out_filepath)


def convert_all_midi(in_path, out_path):
    """
    Convert all midi files in a folder to 303 style patterns in csv.
    Files are searched for recursively.
    """

    if not os.path.exists(out_path):
        Path(out_path).mkdir(parents=True, exist_ok=True)

    for i, file in enumerate(sorted(Path(in_path).rglob('*.mid'))):
        print('converting midi file:', file)
        convert_midi_file(file, out_path + str(i) + '.csv')


if __name__ == "__main__":
    convert_all_midi('../data/raw/midi', '../data/processed/midi/')