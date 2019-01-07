import os
import random
import time

from tqdm import tqdm

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.callbacks import TensorBoard

import numpy as np

LOAD_TRAIN_FILES = False
LOAD_TRAINED_MODEL = False
PREV_MODEL_NAME = ""
MIN_HALITE = 4200
TRAIN_BATCH_SIZE = 100
VALIDATION_COUNT = 50
NUM_EPOCHS = 5

NAME = f"phase1-{int(time.time())}"

TRAIN_DATA_DIR = 'training_data'

train_file_names = []

for data in os.listdir(TRAIN_DATA_DIR):
    halite_amt = int(data.split('-')[0])
    if halite_amt > MIN_HALITE:
        train_file_names.append(os.path.join(TRAIN_DATA_DIR, data))

random.shuffle(train_file_names)

if LOAD_TRAIN_FILES:
    test_x = np.load('test_x.npy')
    test_y = np.load('test_y.npy')
else:
    test_x = []
    test_y = []

    for f in tqdm(train_file_names[:VALIDATION_COUNT]):
        data = np.load(f)

        for d in data:
            test_x.append(np.array(d[0]))
            test_y.append(d[1])

    np.save('test_x.npy', test_x)
    np.save('test_y.npy', test_y)

test_x = np.array(test_x)

# batch loading phase
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

if LOAD_TRAINED_MODEL:
    model = model = tf.keras.models.load_model(PREV_MODEL_NAME)
else:
    model = Sequential()

    model.add(Conv2D(64, (3, 3), padding='same', input_shape=test_x[0].shape))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))

    model.add(Conv2D(64, (3, 3), padding='same'))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))

    model.add(Conv2D(64, (3, 3), padding='same'))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))

    model.add(Conv2D(64, (3, 3), padding='same'))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))

    model.add(Flatten())

    model.add(Dense(5))
    model.add(Activation('sigmoid'))

opt = tf.keras.optimizers.Adam(lr=1e-3, decay=1e-3)
model.compile(loss='sparse_categorical_crossentropy', 
              optimizer=opt,
              metrics=['accuracy'])

train_file_chunks = chunks(train_file_names[VALIDATION_COUNT:], 500)

for e in range(NUM_EPOCHS):
    print(f"currently on epoch {e}")

    for idx, train_files in enumerate(train_file_chunks):
        print(f"working on data chunk {idx+1}/{round(len(train_file_names)/500,2)}")

        if LOAD_TRAIN_FILES or e > 0:
            X = np.load(f"X-{idx}.npy")
            y = np.load(f"y-{idx}.npy")
        else:
            X = []
            y = []

            for f in tqdm(train_files):
                data = np.load(f)

                for d in data:
                    X.append(np.array(d[0]))
                    y.append(d[1])

            def balance(x, y):
                _0 = []
                _1 = []
                _2 = []
                _3 = []
                _4 = []

                for x, y in zip(x, y):
                    if y == 0:
                        _0.append([x, y])
                    elif y == 1:
                        _1.append([x, y])
                    elif y == 2:
                        _2.append([x, y])
                    elif y == 3:
                        _3.append([x, y])
                    elif y == 4:
                        _4.append([x, y])

                shortest = min([len(_0), len(_1), len(_2), len(_3), len(_4)])

                _0 = _0[:shortest]
                _1 = _1[:shortest]
                _2 = _2[:shortest]
                _3 = _3[:shortest]
                _4 = _4[:shortest]

                balanced = _0 + _1 + _2 + _3 + _4
                random.shuffle(balanced)

                print(f"The shortest file was {shortest}, total balanced length is {len(balanced)}")

                xs = []
                ys = []

                for x, y in balanced:
                    xs.append(x)
                    ys.append(y)

                return xs, ys

            X, y = balance(X, y)
            test_x, test_y = balance(test_x, test_y)

            X = np.array(X)
            y = np.array(y)
            test_x = np.array(test_x)
            test_y = np.array(test_y)

            np.save(f"X-{idx}.npy", X)
            np.save(f"y-{idx}.npy", y)

            model.fit(X, y, batch_size=32, epochs=1, validation_data=(test_x, test_y))