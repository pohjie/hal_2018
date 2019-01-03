import os
import random
import time

from tqdm import tqdm

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.callbacks import TensorBoard

LOAD_TRAIN_FILES = False
LOAD_TRAINED_MODEL = False
MIN_HALITE = 4200
TRAIN_BATCH_SIZE = 100
VALIDATION_COUNT = 50

NAME = f"phase1-{int(time.time())}"

TRAIN_DATA_DIR = 'training_data'

train_file_names = []

for data in os.listdir(TRAIN_DATA_DIR):
	halite_amt = int(data.split('-')[0])
	if halite_amt > MIN_HALITE:
		train_file_names.append(os.path.join(TRAIN_DATA_DIR, data))

random.shuffle(train_file_names)