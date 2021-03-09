# -*- coding: utf-8 -*-
"""ACR Model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XZ3bBVnraGvnNVs8EY1BpGcvz-Xz4KE7
"""

# Author: Eyas Hassan
# Guidance of Valerio Velardo

import json
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import tensorflow.keras as keras
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

# specifying json file path
NON_GUITAR_DATA_PATH = "/content/drive/MyDrive/AutoChordRecognition Dataset/non_guitar"
NON_GUITAR_JSON_PATH = os.path.join(NON_GUITAR_DATA_PATH, "non-guitar-2.json")

# hyperparameters
test_size = 0.25
validation_size = 0.2

# loading json data
with open(NON_GUITAR_JSON_PATH, "r") as fp:
  data = json.load(fp)

def get_voicing_library():
  """Generates dictionary of chord voicings (keys) and their int labels (values)."""
  
  label_list = data["mapping"][0]

  voicing_library = {}
  counter = 0

  for chord in label_list:
    if chord not in voicing_library:
      voicing_library[chord] = counter
      # data["labels"].append(voicing_library[chord])
      counter += 1

  return voicing_library

def get_sets(test_size, validation_size):
  """Generate training, validation, and test sets.
      :param test_size (float): Proportion of dataset to allocate for testing set.
      :param validation_size (float): Proportion of training dataset to allocate for validation set.
      """
  
  # set features and targets
  X = np.array(data["MEL"])
  y = np.array(data["labels"])

  # train/test split
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, stratify = y)

  # train/validation split
  X_train, X_validation, y_train, y_validation = train_test_split(X_train, y_train, test_size=validation_size)

  # need to make feature sets into 4D arrays for CNN inputs
  X_train = X_train[..., np.newaxis]
  X_validation = X_validation[..., np.newaxis]
  X_test = X_test[..., np.newaxis]

  return X_train, X_validation, X_test, y_train, y_validation, y_test

def create_model(input_shape):
  """Building the CNN model
      :param input_shape (tuple): shape of input to CNN
      """
  
  # initiate model
  model = keras.Sequential()

  # CNN layer 1
  model.add(keras.layers.Conv2D(32, (3,3), activation="relu", padding="same", input_shape=input_shape, kernel_regularizer=keras.regularizers.l2(0.001)))
  model.add(keras.layers.MaxPool2D((3,3), strides=(2,2), padding="same"))
  model.add(keras.layers.BatchNormalization())

  # CNN layer 2
  model.add(keras.layers.Conv2D(32, (3,3), activation="relu", padding="same", input_shape=input_shape, kernel_regularizer=keras.regularizers.l2(0.001)))
  model.add(keras.layers.MaxPool2D((3,3), strides=(2,2), padding="same"))
  model.add(keras.layers.BatchNormalization())

  # CNN layer 2
  model.add(keras.layers.Conv2D(32, (3,3), activation="relu", padding="same", input_shape=input_shape, kernel_regularizer=keras.regularizers.l2(0.001)))
  model.add(keras.layers.MaxPool2D((3,3), strides=(2,2), padding="same"))
  model.add(keras.layers.BatchNormalization())
  model.add(keras.layers.Dropout(0.3))

  # CNN layer 3
  model.add(keras.layers.Conv2D(64, (3,3), activation="relu", padding="same", input_shape=input_shape, kernel_regularizer=keras.regularizers.l2(0.001)))
  model.add(keras.layers.MaxPool2D((3,3), strides=(2,2), padding="same"))
  model.add(keras.layers.BatchNormalization())
  model.add(keras.layers.Dropout(0.3))

  # Flatten --> Dense Layer
  model.add(keras.layers.Flatten())
  model.add(keras.layers.Dense(128, activation="relu", kernel_regularizer=keras.regularizers.l2(0.001)))
  model.add(keras.layers.BatchNormalization())
  model.add(keras.layers.Dropout(0.3))

  # CNN output
  model.add(keras.layers.Dense(288, activation="softmax"))

  return model

def get_confusion_matrix(true_label, predicted_label, mapped_labels, save_path, dim=16):
  """Plots and saves nxn subset confusion matrices of shape dim of the parent 288x288 confusion matrix.
      :param true_label (list): list of true labels.
      :param predicted_label (list): list of predicted labels.
      :param mapped_labels (dict): Dictionary of the mapping for semantic and numerical labels.
      :param save_path (str): Path to save the plotted figures, a "Figures" folder will be created.
      :param dim (int): dimension of the square subset confusion matrix.
      """

  # pairwise sorting of the true and predicted labels
  y_sorted = sorted(y)
  y_hat_sorted = [label for _,label in sorted(zip(y, y_hat))]

  # creating list of tuples where each tuple holds the start and end index of the true label list where new dim number of classes are observed
  start_end = []

  for i in range(0, len(set(y_sorted)), dim):
    start = y_sorted.index(i)
    if i < len(set(y_sorted)) - dim:
      end = y_sorted.index(i+dim) - 1
    else:
      end = len(y_sorted) - 1
    start_end.append((start, end))

  figure_path = os.path.join(save_path, "Figures")
  os.makedirs(figure_path, exist_ok=True)

  # creating a confusion matrix then plotting and saving the specified subsets of size dimxdim
  for i in range(len(start_end)):
    beg = i * dim
    fin = beg + dim
    
    segment = confusion_matrix(y_sorted, y_hat_sorted, normalize="true")[beg:fin, beg:fin]
    disp = ConfusionMatrixDisplay(confusion_matrix=segment, display_labels=list(mapped_labels.keys())[beg:fin])


    # NOTE: Fill all variables here with default values of the plot_confusion_matrix
    disp.plot(xticks_rotation="vertical", cmap="Reds")
    plt.savefig(os.path.join(figure_path, f"Figure {i}.png"), bbox_inches="tight", pad_inches=0.25)
    plt.show()

  return

if __name__ == "__main__":
  # create train, validation, and test sets
  X_train, X_validation, X_test, y_train, y_validation, y_test = get_sets(test_size, validation_size)

  # create input shape
  input_shape = (X_train.shape[1], X_train.shape[2], X_train.shape[3])

  # create CNN model
  model = create_model(input_shape)

  # compile CNN model
  optimizer = keras.optimizers.Adam(0.0001)
  model.compile(optimizer=optimizer, loss="sparse_categorical_crossentropy", metrics=["accuracy"])

  # train CNN model
  history = model.fit(X_train, y_train, validation_data=(X_validation, y_validation), batch_size=32, epochs=90)

  print(model.summary())

  # evaluate CNN model on test set
  test_error, test_accuracy = model.evaluate(X_test, y_test, verbose=1)
  print(f"Accuracy on test set: {test_accuracy}, Error on test set: {test_error}")

# saving model
model.save(os.path.join(NON_GUITAR_DATA_PATH, "Second_Model"))

# loading model
Second_Model = keras.models.load_model("/content/drive/MyDrive/AutoChordRecognition Dataset/non_guitar/Second_Model")

# getting predicitons from loaded model
predictions = np.argmax((Second_Model.predict(X_test)), axis=1)

# getting mapped chord voicing library
voicing_library = get_voicing_library()

y = y_test
y_hat = predictions

# plotting and saving confusion matrices
get_confusion_matrix(y, y_hat, voicing_library, NON_GUITAR_DATA_PATH)