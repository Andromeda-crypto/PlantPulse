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

BASE_DIR = Path(__file__).resolve().parent
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Set matplotlib backend early
# plt.switch_backend('TkAgg')
# Configuration
CONFIG = {
    'hours': 168,
    'moisture_threshold': 30,
    'light_threshold': 200,
    'temp_hot_threshold': 28,
    'csv_dir': BASE_DIR / 'csv runs',  # Updated to match your directory
    'csv_filename': 'plant_data_latest.csv',
    'start_time': datetime.datetime(2025, 3, 1, 0, 0),
}
# Create output directory
DATASET_PATH = BASE_DIR / 'dataset' / 'PlantVillage'
data_set = pd.DataFrame(BASE_DIR.glob('**/*.jpg'))
# need to get the contents of the dataset
# currently it is just the path of the images
print(data_set)

