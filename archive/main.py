import matplotlib.pyplot as plt
import numpy as np
import PIL
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

import pathlib


from PIL import Image
import os, sys
# 80% for training, 20% for validation
# training dataset
data_dir = 'trash_dataset/'

path = "trash_dataset/"
dirs = os.listdir(path)

def resize():
    for dir in dirs:
        for item in os.listdir(path+dir+'/'):
            fullpath = path+dir+'/'+item
            print(fullpath)
            if os.path.isfile(fullpath):
                im = Image.open(fullpath)
                f, e = os.path.splitext(fullpath)
                imResize = im.resize((256,256), Image.LANCZOS)
                # we save it, your own extension here (in my case was jpg)
                imResize.convert('RGB').save(f + '.jpg', 'JPEG', quality=100) 
resize()

train_ds = tf.keras.utils.image_dataset_from_directory(
  data_dir,
  batch_size=32,
  image_size=(256,256),
  seed=123,
  validation_split=0.2,
  subset='training',
)

val_ds = tf.keras.utils.image_dataset_from_directory(
  data_dir,
  batch_size=32,
  image_size=(256,256),
  seed=123,
  validation_split=0.2,
  subset='validation',
)

