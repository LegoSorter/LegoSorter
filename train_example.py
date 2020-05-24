import pandas as pd
from keras import Model
from keras.applications import ResNet50
from keras.models import Sequential
from keras.layers import Convolution2D, Dropout
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from tensorboard.plugins.hparams import keras
from keras.preprocessing.image import ImageDataGenerator
from tensorflow import optimizers

restnet = ResNet50(include_top=False, weights='imagenet', input_shape=(224, 224, 3))

restnet.trainable = True
set_trainable = False
for layer in restnet.layers:
    if layer.name in ['res5c_branch2b', 'res5c_branch2c', 'activation_97']:
        set_trainable = True
    if set_trainable:
        layer.trainable = True
    else:
        layer.trainable = False
layers = [(layer, layer.name, layer.trainable) for layer in restnet.layers]
pd.DataFrame(layers, columns=['Layer Type', 'Layer Name', 'Layer Trainable'])

classifier = Sequential()
classifier.add(restnet)
classifier.add(Flatten())
classifier.add(Dense(output_dim=22, activation='softmax'))

classifier.compile(loss='categorical_crossentropy',
                   optimizer='adam',
                   metrics=['accuracy'])

train_datagen = ImageDataGenerator(rescale=1. / 255,
                                   shear_range=0.2,
                                   zoom_range=0.2,
                                   horizontal_flip=True)

test_datagen = ImageDataGenerator(rescale=1. / 255)

training_set = train_datagen.flow_from_directory('dataset/train',
                                                 target_size=(224, 224),
                                                 batch_size=12,
                                                 class_mode='categorical')

test_set = test_datagen.flow_from_directory('dataset/val',
                                            target_size=(224, 224),
                                            batch_size=12,
                                            class_mode='categorical')

classifier.fit_generator(training_set,
                         samples_per_epoch=3600,
                         nb_epoch=25,
                         validation_data=test_set,
                         nb_val_samples=960)
