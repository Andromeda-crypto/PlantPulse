# purpose of this file is to simulate and generate fake sensor which will create data
# such as soil moisture, light, temperature) over 7 days with hourly readings (168 total points).

import random
import datetime
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
import math

np.random.seed(42)

start_time = datetime.datetime(2025,3,1,0,0)
time_points = [start_time + datetime.timedelta(hours=i) for i in range(168)]

print(time_points[:5])

def add_moisture_simulation():
    moisture = []
    for i in range(168):
        if i < 24:
            moisture.append(random.uniform(0, 30))  # Introduce randomness within range
        elif i < 40:
            moisture.append(random.uniform(30, 50))
        elif i < 60:
            moisture.append(random.uniform(50, 70))
        elif i < 80:
            moisture.append(random.uniform(70, 90))
        else:
            moisture.append(random.uniform(90, 100))
    return moisture


    


