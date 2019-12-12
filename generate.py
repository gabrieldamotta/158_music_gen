import pickle
import numpy
from datetime import datetime
from music21 import instrument, note, stream, chord
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import BatchNormalization as BatchNorm
from keras.layers import Activation

"""
Generates a song with genLength notes using the trained
weights "weights.hdf5" and pitches file in "data/". Outputs
song as txt file to "generated songs/text-raws".
"""

genLength = 1500

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
networkInput = []
output = []
for i in range(0, len(pitches) - sequenceLength, 1):
    sequenceIn = pitches[i:i + sequenceLength]
    sequenceOut = pitches[i + sequenceLength]
    networkInput.append([strToInt[char] for char in sequenceIn])
    output.append(strToInt[sequenceOut])

patternNum = len(networkInput)

# reshape the input into a format compatible with LSTM layers
normalizedInput = numpy.reshape(networkInput, (patternNum, sequenceLength, 1))
# normalize input
normalizedInput = normalizedInput / float(vocab)

# rebuild same model
model = Sequential()
model.add(LSTM(
    512,
    input_shape=(normalizedInput.shape[1], normalizedInput.shape[2]),
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
model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

# load trained weights to model
model.load_weights('weights.hdf5')

# pick a random sequence from the training set as a starting point for the prediction
start = numpy.random.randint(0, len(networkInput)-1)

# translation dictionary (integers to pitches)
intToStr = dict((number, pitch) for number, pitch in enumerate(pitchref))

pattern = networkInput[start]
genSong = []

# consecutive rest count
rest_count = 0

# generate 500 notes
for i in range(genLength):
    predictionInput = numpy.reshape(pattern, (1, len(pattern), 1))
    predictionInput = predictionInput / float(vocab)

    prediction = model.predict(predictionInput, verbose=0)

    index = numpy.argmax(prediction)
    result = intToStr[index]

    # prevent large rest gaps [COMMENT THIS BLOCK OUT IF HAVING ISSUES]
    if result == "REST\n":
        rest_count += 1
    else:
        rest_count = 0
    if rest_count > 6:
        flatPred = prediction.flatten()
        flatPred.sort()
        result = intToStr[int(flatPred[-2])]

    genSong.append(result)

    # restructure pattern
    pattern.append(index)
    pattern = pattern[1:len(pattern)]

now = datetime.now()
dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
f = open("generated songs/text-raws/genSong-" + dt_string + ".txt", "w")
for p in genSong:
   f.write(p)
