from glob import glob
from numpy import *
from keras import *
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import Activation
from keras.layers import BatchNormalization as BatchNorm
from keras.utils.np_utils import to_categorical
from keras.callbacks import ModelCheckpoint

"""
Generate neural net inputs and outputs from txt files
TODO: Timing/Duration
"""
inputLength = 50

pitches = []
# read in all pitches in txt files
for txtfile in glob("songs/text/*.txt"):
    try:
        f = open(txtfile)
        line = f.readline()
        while line:
            pitch = line.split(" ")[0]
            pitches.append(pitch)
            line = f.readline()
    finally:
        f.close()

# str to int dictionary
pitchRef = set(p for p in pitches)
strToInt = dict((p,i) for i,p in enumerate(pitchRef))
intToStr = dict((i,p) for i,p in enumerate(pitchRef))
# convert str to ints
numPitches = [strToInt[p] for p in pitches]

# generate nn training data
inputs = []
labels = []
for i in range(0, len(pitches) - inputLength, 1):
    inputs.append([numPitches[i : i+inputLength]])
    labels.append(numPitches[i+inputLength])

# port training data to lstm accepted format
# (normalised in, one-hot encoded out)
networkInput = reshape(inputs, (len(inputs), inputLength, 1))/float(len(pitchRef))
networkOutput = to_categorical(labels)

# define model
# TODO: will play around with hyper paremeters more
model = Sequential()
model.add(LSTM(
    256,
    input_shape=(networkInput.shape[1], networkInput.shape[2]),
    return_sequences=True
))
model.add(Dropout(0.3))
model.add(LSTM(512, return_sequences=True))
model.add(Dropout(0.3))
model.add(LSTM(256))
model.add(Dense(256))
model.add(Dropout(0.3))
model.add(Dense(len(pitchRef)))
model.add(Activation('softmax'))
model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

# train model
filepath = "weights-improvement-{epoch:02d}-{loss:.4f}-bigger.hdf5"
checkpoint = ModelCheckpoint(
    filepath, monitor='loss',
    verbose=0,
    save_best_only=True,
    mode='min')

callbacks_list = [checkpoint]
model.fit(networkInput, networkOutput, epochs=200,
          batch_size=64, callbacks=callbacks_list)

# generate from random starting point in input
start = numpy.random.randint(0, len(networkInput)-1)
pattern = networkInput[start]
genSong = []
# generate 500 notes
for i in range(500):
    predictionInput = numpy.reshape(pattern, (1, len(pattern), 1))/float(len(pitchRef))
    prediction = model.predict(predictionInput, verbose=0)

    # add to current generated song
    index = numpy.argmax(prediction)
    result = intToStr[index]
    genSong.append(result)

    # move pattern over by 1
    pattern.append(index)
    pattern = pattern[1:len(pattern)]

print(genSong)

f = open("songs/text/genSong.txt", w)
for p in genSong:
    f.write(p + " 0.5000 0.5000")
