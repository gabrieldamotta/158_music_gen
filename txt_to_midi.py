from music21 import *
from glob import glob
from math import *

for txtfile in glob("songs/text/gen/*.txt"):
    try:
        f = open(txtfile)
        line = f.readline()
        outputNotes = []
        offset = 0.0
        # read each note
        while line:
            txtNote = line.split(" ")
            newNote = note.Note(txtNote[0]) # pitch
            newNote.offset = offset
            offset += float(txtNote[1]) # add offset NOT FULLY RIGHT
            newNote.storedInstrument = instrument.Piano()
            outputNotes.append(newNote)
            line = f.readline()
        #convert to midi
        midiStream = stream.Stream(outputNotes)
        midiStream.write('midi',
                         fp="songs/midi/gen/" +
                         txtfile.split("/")[3].split(".")[0]
                         + ".mid")
    finally:
        f.close()
