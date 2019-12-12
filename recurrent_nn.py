import glob
import pickle
import numpy
from music21 import converter, instrument, note, chord
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import Activation
from keras.layers import BatchNormalization as BatchNorm
from keras.utils import np_utils
from keras.callbacks import ModelCheckpoint

"""
Builds and trains a neural network model using the txt files
present in "songs/txt" as training data. Outputs pitches
used to "data/" and weights found in each epoch to "checkpoints/".
"""

# store pitches to train on
pitches = []
# read pitches in txt files
for txtfile in glob.glob("songs/text/*.txt"):
    try:
        f = open(txtfile)
        line = f.readline()
        while line:
            # pitch = line.split(" ")[0]
            pitches.append(line)
            line = f.readline()
    finally:
        f.close()

# save pitches for generation
with open('data/pitches', 'wb') as filepath:
    pickle.dump(pitches, filepath)

vocab = len(set(pitches))

# total length of input
sequenceLength = 100

# get all pitch names
pitchref = sorted(set(p for p in pitches))

 # create a translation dictionary (pitches to integers)
strToInt = dict((pitch, number) for number, pitch in enumerate(pitchref))

# initialize inputs and outputs
networkInput = []
networkOutput = []

# create input sequences and the corresponding outputs
for i in range(0, len(pitches) - sequenceLength, 1):
    sequenceIn = pitches[i:i + sequenceLength]
    sequenceOut = pitches[i + sequenceLength]
    networkInput.append([strToInt[char] for char in sequenceIn])
    networkOutput.append(strToInt[sequenceOut])

patternNum = len(networkInput)

# reshape the input into a format compatible with LSTM layers
networkInput = numpy.reshape(networkInput, (patternNum, sequenceLength, 1))
# normalize input
networkInput = networkInput / float(vocab)

# one hot enconding the labels
networkOutput = np_utils.to_categorical(networkOutput)

model = Sequential()
model.add(LSTM(
    512,
    input_shape=(networkInput.shape[1], networkInput.shape[2]),
    recurrent_dropout=0.3,
    return_sequences=True
))
model.add(LSTM(512, return_sequences=True, recurrent_dropout=0.3,))
model.add(LSTM(512))
model.add(BatchNorm())

# prevent overfitting
model.add(Dropout(0.3))
model.add(Dense(256))
model.add(Activation('relu')) # regularization
model.add(BatchNorm())
model.add(Dropout(0.3))

model.add(Dense(vocab))
model.add(Activation('softmax')) # softmax activation and crossentropy loss
model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

# checkpoint system
filepath = "checkpoints/weights-improvement-{epoch:02d}-{loss:.4f}-bigger.hdf5"
checkpoint = ModelCheckpoint(
    filepath,
    monitor='loss',
    verbose=0,
    save_best_only=True,
    mode='min'
)
callbacks_list = [checkpoint]

# train model
model.fit(networkInput, networkOutput, epochs=200, batch_size=128, callbacks=callbacks_list)
