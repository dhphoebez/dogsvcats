# -*- coding: utf-8 -*-
"""ML Final Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LKjMbfOlpqwMuEOw6rCGhpQp98lPLPEd

###Import Basic Packages
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import tensorflow as tf
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt
import pickle
# %matplotlib inline  

from sklearn.model_selection import train_test_split

"""###Load the Images
Show some examples of the images
"""

categories = []
filenames = []

for num in range(200):
  filenames.append("/content/train/cat." + str(num+1) + ".jpg")
  categories.append(0)

for num in range(200):
  filenames.append("/content/train/dog." + str(num+1) + ".jpg")
  categories.append(1)

df = pd.DataFrame({'filename' : filenames, 'category' : categories})
df.head()
df['category'].value_counts()
for i in range(10) :
    sample = filenames[i+10]
    image = tf.keras.preprocessing.image.load_img(sample)
    plt.imshow(image)
    plt.title('dog' if categories[i+10]==1 else 'cat')
    plt.show()

#model 
model = keras.models.Sequential()

##  Conv_1
model.add(keras.layers.Conv2D(32, 3,input_shape = [128, 128, 3], activation = 'relu', padding = 'same'))
model.add(keras.layers.BatchNormalization())
model.add(keras.layers.MaxPool2D(2))
model.add(keras.layers.Dropout(0.2))

## Conv_2
model.add(keras.layers.Conv2D(64, 3, activation = 'relu', padding = 'same'))
model.add(keras.layers.BatchNormalization())
model.add(keras.layers.MaxPool2D(2))
model.add(keras.layers.Dropout(0.2))

## Conv_3
model.add(keras.layers.Conv2D(128, 3, activation = 'relu', padding = 'same'))
model.add(keras.layers.BatchNormalization())
model.add(keras.layers.MaxPool2D(2))
model.add(keras.layers.Dropout(0.2))

## Conv_4
model.add(keras.layers.Conv2D(256, 3, activation = 'relu', padding = 'same'))
model.add(keras.layers.BatchNormalization())
model.add(keras.layers.MaxPool2D(2))
model.add(keras.layers.Dropout(0.2))

## Flatten
model.add(keras.layers.Flatten())

## fc_1
model.add(keras.layers.Dense(1024, activation = 'relu'))
model.add(keras.layers.Dropout(0.25))

## fc_2
model.add(keras.layers.Dense(2, activation = 'sigmoid'))

## optimizer and loss
#optimizer = keras.optimizers.RMSprop(lr = 0.01)
model.compile(loss = 'categorical_crossentropy', optimizer = 'rmsprop', metrics = ['accuracy'])

model.summary()

"""###Data Augmentation
We create an ImageDataGenerator object that will create augmented images for the training data set. This was taken from class demo.
"""

def create_datagen():
    datagen = keras.preprocessing.image.ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        zca_epsilon=1e-06,  # epsilon for ZCA whitening
        rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
        # randomly shift images horizontally (fraction of total width)
        width_shift_range=0.1,
        # randomly shift images vertically (fraction of total height)
        height_shift_range=0.1,
        shear_range=0.,  # set range for random shear
        zoom_range=0.,  # set range for random zoom
        channel_shift_range=0.,  # set range for random channel shifts
        # set mode for filling points outside the input boundaries
        fill_mode='nearest',
        cval=0.,  # value used for fill_mode = "constant"
        horizontal_flip=True,  # randomly flip images
        vertical_flip=False,  # randomly flip images
        # set rescaling factor (applied before any other transformation)
        rescale=None,
        # set function that will be applied on each input
        preprocessing_function=None,
        # image data format, either "channels_first" or "channels_last"
        data_format=None,
        # fraction of images reserved for validation (strictly between 0 and 1)
        validation_split=0.0)
    return datagen

"""###Training the model
Classification problem

Encode labels
"""

df['category'] = df['category'].map({0 : 'cat', 1 : 'dog'})

train_df, valid_df = train_test_split(df, test_size=0.2, random_state=42)
train_df = train_df.reset_index(drop=True)
valid_df = valid_df.reset_index(drop=True)
total_train = train_df.shape[0]
total_valid = valid_df.shape[0]
batch_size = 10
valid_data = keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
valid_generator = valid_data.flow_from_dataframe(valid_df, './train/', x_col = 'filename', y_col = 'category', 
                                                 target_size = [128, 128], 
                                                 class_mode = 'categorical', 
                                                 batch_size = batch_size)
train_data = keras.preprocessing.image.ImageDataGenerator(rotation_range=20, rescale = 1./255, horizontal_flip=True)
train_generator = train_data.flow_from_dataframe(train_df,
                                                './train/',
                                                x_col = 'filename',
                                                y_col = 'category',
                                                target_size=[128,128],
                                                class_mode='categorical',
                                                batch_size=batch_size)
epochs = 30
history = model.fit_generator(
    train_generator, 
    epochs=epochs,
    validation_data=valid_generator,
    validation_steps=total_valid//batch_size,
    steps_per_epoch=total_train//batch_size)

"""Saving parameters"""

model.save_weights("model")

"""###Analyzing and comparing training results

Plot both Training and Validation Loss
"""

import numpy as np
plt.plot(history.history['loss'], color='b', label="Training loss")
plt.plot(history.history['val_loss'], color='r', label="validation loss")
plt.xticks(np.arange(1, epochs, 1))
plt.yticks(np.arange(0, 1, 0.1))
plt.legend()
plt.title('Training Loss VS Validation Loss')
plt.show()

"""Plot Training and Validation Accuracy"""

plt.plot(history.history['accuracy'], color='b', label="Training accuracy")
plt.plot(history.history['val_accuracy'], color='r',label="Validation accuracy")
plt.xticks(np.arange(1, epochs, 1))
plt.title('Training Accuracy VS Validation Accuracy')
plt.legend()
plt.show()

"""###Testing a dataset
First we need to prepare the testing dataset
"""

test_df = pd.DataFrame({'filename' : filenames})    
samples = test_df.shape[0]

test_data = keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
test_generator = test_data.flow_from_dataframe(
    test_df, 
    "./test1/", 
    x_col='filename',
    y_col=None,
    class_mode=None,
    target_size=[128,128],
    batch_size=batch_size,
    shuffle=False)

"""Run the prediction model"""

predict = model.predict_generator(test_generator, steps=np.ceil(samples/batch_size))

test_df['category'] = np.argmax(predict, axis=-1)
for index in range(400):
  if test_df['category'][index] == 0:
    test_df['category'][index] = "cat"
  else:
    test_df['category'][index] = "dog"

"""Saving the tested set as result"""

result_df = test_df.copy()
result_df['id'] = result_df['filename'].str.split('.').str[0]
result_df['label'] = result_df['category']
result_df.drop(['filename', 'category'], axis=1, inplace=True)
result_df.to_csv('final_result.csv', index=False)