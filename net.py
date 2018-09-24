from sklearn.preprocessing import normalize
from sklearn.utils import shuffle
from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from keras.callbacks import ModelCheckpoint
import csv
import numpy as np

# 20 features, binary labels
X = []
y = []

# read data
with open('data/voice.csv') as f:
    # skip header row
    next(f)

    # read dataset
    reader = csv.reader(f)
    for row in reader:
        # append all values, except for the label, and convert to float
        X.append([float(i) for i in row[0:20]])

        # setup labels
        if row[20] == "male":
            y.append([0])
        else:
            y.append([1])

# shuffle dataset
X, y = shuffle(X, y)

# normalize data
X = normalize(X)

# build model
model = Sequential()

model.add(Dense(units=64, activation='relu', input_dim=20))
model.add(Dropout(0.25))

model.add(Dense(units=256, activation='relu'))
model.add(Dropout(0.25))

model.add(Dense(units=256, activation='relu'))
model.add(Dropout(0.25))

model.add(Dense(units=64, activation='relu'))
model.add(Dropout(0.25))

model.add(Dense(units=1, activation='sigmoid'))

model.compile(loss='binary_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

# setup callbacks
filepath="model-{epoch:02d}-{val_acc:.2f}.hdf5"
checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')
callbacks_list = [checkpoint]

# run model    
model.fit(np.array(X), np.array(y),
          batch_size=1,
          epochs=500,
          verbose=1, validation_split=0.33,
          callbacks=callbacks_list)