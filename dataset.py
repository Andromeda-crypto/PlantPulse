# this file is to load data from dataset to train the model
# downloaded and unzipped the dataset


import os
import pandas as pd
import sqlite3
import glob
import numpy as np
import random
import datetime
from datetime import timedelta
import logging
from pathlib import Path

BASE_DIR = Path('/Users/omanand/Downloads/plantvillage dataset/grayscale')
DATASET_PATH = BASE_DIR / 'dataset' / 'PlantVillage'
data_set = pd.DataFrame(BASE_DIR.glob('**/*.jpg'))
# need to get the contents of the dataset
# currently it is just the path of the images

