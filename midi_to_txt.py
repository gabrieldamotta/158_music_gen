from music21 import *
from glob import glob
from math import *

"""
Converts midi music files into a txt file.
Reads from "songs/midi/" and outputs to "/songs/text".
"""
# for each midi file, read with music21
for midifile in glob("songs/midi/*.mid"):
    parsedfile = converter.parse(midifile)
    notesIt = parsedfile.flat.notes

    # iterate through notes and write them to file
    f = open("songs/text/" + midifile.split("/")[2].split(".")[0] + ".txt", "w")
    prevOffset = 0
    for n in notesIt:
        if isinstance(n, note.Note):
            f.write(str(n.pitch) + " %.4f" %(n.offset-prevOffset) +
            " %.4f" %(n.duration.quarterLength) + "\n")
            prevOffset = n.offset
        else: # handle chords
            for an in n.pitches:
                f.write(str(an) + " %.4f" %(n.offset-prevOffset) +
                " %.4f" %(n.duration.quarterLength) + "\n")
                prevOffset = n.offset
    f.close()
