import os
import tempfile
from matplotlib import pyplot as plt
import tensorflow as tf
from keras import layers, models
import keras
from PIL import Image
import streamlit as st
import numpy as np
import cv2

mnist = keras.datasets.mnist
(x_train, y_train), (x_test, y_test) = mnist.load_data()

X_train = keras.utils.normalize(x_train, axis=1)
X_test = keras.utils.normalize(x_test, axis=1)

model = models.Sequential([
    layers.Flatten(input_shape=(28, 28)), #Flatten 2D images into 1 dimensional vector of pixel values, input is of size 28 by 28
    layers.Dense(128, activation='relu'), #learns features from the images with 128 units.
    layers.Dropout(0.2), #randomly sets 20% of the neurons to 0 to reduce overfitting,
    layers.Dense(10) # Output layer with 10 units and softmax activation
])

model.compile(
    optimizer='adam', # Use the ADAM optimizer for this neural network
    loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=['accuracy']
)

model.fit(x_train, y_train, epochs=5) # fit the model using 5 epochs and the training data

test_loss, test_acc = model.evaluate(x_test, y_test, verbose=2) #Determine appropriateness of the model.
print(f'The model was {test_acc *100}% accurate')

prob_model = keras.Sequential([model, layers.Softmax()]) # Create a model that can be used to predict the digit a certain image is showing
preds = prob_model.predict(x_test) # Test this model using testing data


def classify_digit(image):
    img = cv2.imread(image)[:,:,0]
    img = (1 - img / 255.0) * 255
    img = np.array([img])
    prediction = prob_model.predict(img)
    return prediction

def resize_image(image, target_size):
    img = Image.open(image)
    img = img.convert('L')  # Convert to grayscale
    resized_image = img.resize(target_size, resample=Image.BILINEAR)
    return np.array(resized_image)


plt.figure(figsize=(10,5))
for i in range(5):
    plt.subplot(1, 5, i+1)
    plt.grid(False)
    plt.xticks([])
    plt.yticks([])
    plt.imshow(x_test[i], cmap=plt.cm.binary)
    pred_label = tf.argmax(preds[i]).numpy()
    real = y_test[i]
    if pred_label == real:
        color = 'green'
    else:
        color = 'red'
    plt.xlabel(f"{pred_label} ({real})", color=color)
    plt.show()
