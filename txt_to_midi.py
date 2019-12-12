from music21 import *
from glob import glob
from math import *

"""
Converts txt files into midi music files.
Reads from "generated songs/text-raws/gen/" and outputs to "generated songs/".
"""

baseOff = 0.5

for txtfile in glob("generated songs/text-raws/gen/*.txt"):
    try:
        f = open(txtfile)
        line = f.readline()
        outputNotes = []
        offset = 0.0
        # read each note
        while line:
            if line == "REST\n": # calculate rest offset
                offset += baseOff
            elif ':' in line: # many pitches (chord)
                pitches = line.split(':')
                chordNotes = []
                for p in pitches: # set pitches
                    newNote = note.Note(p)
                    newNote.duration.quarterLength = 1.25 # set duration
                    newNote.volume.velocity = 100
                    newNote.storedInstrument = instrument.Piano()
                    chordNotes.append(newNote)
                newChord = chord.Chord(chordNotes)
                newChord.offset = offset # set offset
                outputNotes.append(newChord)
            else: # single pitch
                txtNote = line.split("\n")
                newNote = note.Note(txtNote[0]) # set pitch
                newNote.duration.quarterLength = 1.25 # set duration
                newNote.volume.velocity = 100
                newNote.offset = offset # set offset
                # offset += baseOff # TEMP
                newNote.storedInstrument = instrument.Piano() # TODO: guitar?
                outputNotes.append(newNote)
            # offset += baseOff # add regular offset
            line = f.readline()
        #convert to midi
        midiStream = stream.Stream(outputNotes)
        midiStream.write('midi',
                         fp="generated songs/" +
                         txtfile.split("/")[3].split(".")[0]
                         + ".mid")
    finally:
        f.close()
