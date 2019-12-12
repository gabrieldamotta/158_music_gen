import pickle
import numpy
from music21 import instrument, note, stream, chord
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import BatchNormalization as BatchNorm
from keras.layers import Activation
from keras.utils import np_utils

"""
Evaluates the training accuracy and loss using the trained
weights "weights.hdf5" and pitches file in "data/".
"""

# get pitches used in training
with open('data/pitches', 'rb') as filepath:
    pitches = pickle.load(filepath)

# get all pitch references and number
pitchref = sorted(set(p for p in pitches))
vocab = len(set(pitches))

# translation dictionary (pitches to integers)
strToInt = dict((pitch, number) for number, pitch in enumerate(pitchref))

# same sequence length
sequenceLength = 100

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

# rebuild same model
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
model.add(Dropout(0.3))
model.add(Dense(256))
model.add(Activation('relu'))
model.add(BatchNorm())
model.add(Dropout(0.3))
model.add(Dense(vocab))
model.add(Activation('softmax'))
model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

# load trained weights to model
model.load_weights('weights.hdf5')

# check training accuracy
loss, acc = model.evaluate(networkInput, networkOutput, verbose=1)

# report on results
print("Loss: " + str(loss) + "\nTraining accuracy: " + str(acc))
