from tensorflow.python.keras.optimizers import Adam
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers.convolutional import Conv2D, Conv2DTranspose
from tensorflow.python.keras.layers.pooling import MaxPooling2D
from tensorflow.python.keras.layers.core import Dense, Dropout
from tensorflow.python.keras.layers import Input
from tensorflow.python.keras.layers.merge import Add
from tensorflow.python.keras.engine.training import Model
from tensorflow.python.keras.models import load_model

import os
import tensorflow as tf
import numpy as np
import scipy as sp
import warnings
import time
import build_data
import sys

NUMBER_OF_CLASSES = 2
IMAGE_SHAPE = (300,300)
EPOCHS = 100
BATCH_SIZE = 1

LEARNING_RATE = 1e-5

# Specify these directory paths

DATA_DIRECTORY = 'dataset'
RUNS_DIRECTORY = './runs'
TRAINING_DATA_DIRECTORY ='dataset/training'
LOG_PATH = './log'

def run(model):
    # Download kitti dataset
    build_data.maybe_download_training_img(DATA_DIRECTORY)

    x, y = build_data.get_data(TRAINING_DATA_DIRECTORY, IMAGE_SHAPE)
    
    if model is None:
        inputs = Input(shape=(IMAGE_SHAPE[0], IMAGE_SHAPE[1], 3))

        # Block 1
        block1_conv1 = Conv2D(
            64, (3, 3), activation='relu', padding='same',
            name='block1_conv1')(inputs)
        block1_conv2 = Conv2D(
            64, (3, 3), activation='relu', padding='same', name='block1_conv2')(block1_conv1)
        block1_pool = MaxPooling2D((2, 2), strides=(2, 2), name='block1_pool')(block1_conv2)

        # Block 2
        block2_conv1 = Conv2D(
            128, (3, 3), activation='relu', padding='same', name='block2_conv1')(block1_pool)
        block2_conv2 = Conv2D(
            128, (3, 3), activation='relu', padding='same', name='block2_conv2')(block2_conv1)
        block2_pool = MaxPooling2D((2, 2), strides=(2, 2), name='block2_pool')(block2_conv2)

        # Block 3
        block3_conv1 = Conv2D(
            256, (3, 3), activation='relu', padding='same', name='block3_conv1')(block2_pool)
        block3_conv2 = Conv2D(
            256, (3, 3), activation='relu', padding='same', name='block3_conv2')(block3_conv1)
        block3_conv3 = Conv2D(
            256, (3, 3), activation='relu', padding='same', name='block3_conv3')(block3_conv2)
        block3_pool = MaxPooling2D((2, 2), strides=(2, 2), name='block3_pool')(block3_conv3)

        # Block 4
        block4_conv1 = Conv2D(
            512, (3, 3), activation='relu', padding='same', name='block4_conv1')(block3_pool)
        block4_conv2 = Conv2D(
            512, (3, 3), activation='relu', padding='same', name='block4_conv2')(block4_conv1)
        block4_conv3 = Conv2D(
            512, (3, 3), activation='relu', padding='same', name='block4_conv3')(block4_conv2)
        block4_pool = MaxPooling2D((2, 2), strides=(2, 2), name='block4_pool')(block4_conv3)

        # Block 5
        block5_conv1 = Conv2D(
            512, (3, 3), activation='relu', padding='same', name='block5_conv1')(block4_pool)
        block5_conv2 = Conv2D(
            512, (3, 3), activation='relu', padding='same', name='block5_conv2')(block5_conv1)
        block5_conv3 = Conv2D(
            512, (3, 3), activation='relu', padding='same', name='block5_conv3')(block5_conv2)
        block5_pool = MaxPooling2D((2, 2), strides=(2, 2), name='block5_pool')(block5_conv3)

        pool5_conv1x1 = Conv2D(2, (1, 1), activation='relu', padding='same')(block5_pool)
        upsample_1 = Conv2DTranspose(2, kernel_size=(4, 4), strides=(2, 2), padding="same")(pool5_conv1x1)

        pool4_conv1x1 = Conv2D(2, (1, 1), activation='relu', padding='same')(block4_pool)
        add_1 = Add()([upsample_1, pool4_conv1x1])

        upsample_2 = Conv2DTranspose(2, kernel_size=(4, 4), strides=(2, 2), padding="same")(add_1)
        pool3_conv1x1 = Conv2D(2, (1, 1), activation='relu', padding='same')(block3_pool)
        add_2 = Add()([upsample_2, pool3_conv1x1])

        upsample_3 = Conv2DTranspose(2, kernel_size=(16, 16), strides=(8, 8), padding="same")(add_2)
        output = Dense(2, activation='softmax')(upsample_3)

        model = Model(inputs, output, name='multinet_seg')
        
        adam = Adam(lr=LEARNING_RATE)
        model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'])

    model.fit(x, y, batch_size=BATCH_SIZE, epochs=EPOCHS)
    model.save('trained_model/trained_model'+ str(time.time()) + '.h5')

if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == '-e':
            model_filename = 'trained_model.h5'
            model_path = os.path.join('trained_model', model_filename)
            build_data.save_inference_samples(DATA_DIRECTORY, IMAGE_SHAPE, model_path)
        else:
            print("continue traning...")
            model_filename = sys.argv[1]
            model_path = os.path.join('.', model_filename)
            if not os.path.exists(model_path):
                print("Model not found!")
            else:
                run(load_model(model_path))
    else:
        run()
           
