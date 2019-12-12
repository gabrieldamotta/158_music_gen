import os
from music21 import *
from glob import glob
from math import *

"""
Converts midi music files into a txt file.
Reads from "songs/midi/" and outputs to "songs/text/".
"""

def roundLimit(x):
    if x >= 1.5:
        x = 1.5
    elif x >= 1.0:
        x = 1.0
    elif x < 0.5:
        x = 0.25
    else:
        x = 0.5
    return x

def restNum(x, f):
    num = round(x / 0.75)
    for i in range(0,num):
        f.write("REST\n")

# for each midi file, read with music21
for midifile in glob("songs/midi/*.mid"):
    parsedfile = converter.parse(midifile)
    notesIt = parsedfile.flat.notes

    # iterate through notes and write them to file
    f = open("songs/text/" + midifile.split("/")[2].split(".")[0] + ".txt", "w")
    prevOffset = 0
    inChord = 0
    for n in notesIt:
        # calculate number of rests (.5)
        restNum(n.offset-prevOffset, f)
        # limit duration possibilities
        newDur = roundLimit(n.duration.quarterLength)

        # UNUSED: handle same offset
        # if n.offset-prevOffset == 0:
        #     f.seek(-1, os.SEEK_END)
        #     f.truncate()

        if isinstance(n, note.Note):
            f.write(str(n.pitch) + "\n") # + " %.4f" %(newDur) + "\n")
        else: # handle chords
            firstAn = 1
            for an in n.pitches:
                if not firstAn:
                    f.write(":")
                f.write(str(an))
                firstAn = 0
            f.write("\n")
        prevOffset = n.offset
    f.close()
