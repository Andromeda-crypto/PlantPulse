# purpose of this file is to simulate and generate fake sensor which will create data
# such as soil moisture, light, temperature) over 7 days with hourly readings (168 total points).

import datetime
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
import math


np.random.seed(42)


start_time = datetime.datetime(2025, 3, 1, 0, 0)
time_points = [start_time + timedelta(hours=i) for i in range(168)]

# Create soil moisture data
def add_moisture_simulation():
    moisture = [50]  
    for i in range(167):  
        if (i + 1) % 72 == 0:  
            moisture.append(70)
        else:
            last_value = moisture[-1]  
            new_value = last_value - np.random.uniform(0.5, 2)
            if new_value < 20:
                new_value = 20
            elif new_value > 80:
                new_value = 80
            moisture.append(new_value)
    return moisture

def add_light_simulation():
    light = []
    for i in range(168):
        base_value = 500 + 500 * math.sin(math.pi *i / 12)
        light_value = base_value + np.random.uniform(-50,50)
        if light_value < 0:
            light_value = 0
        elif light_value > 1000:
            light_value = 1000
        else:
            light_value = light_value

        light.append(light_value)

    return light



def add_temperature_simulation():
    # similar logic to light using sin wave to simulate temperature
    temperature = []
    for i in range(168):
        base_value = 20 + 10 * math.sin(math.pi * i/12)
        temperature_value = base_value * np.random.uniform(-5,5)
        if temperature_value < 0:
            temperature_value = 0
        elif temperature_value > 40:
            temperature_value = 40
        else:
            return
        temperature.append(temperature_value)
    return temperature




moisture_level = add_moisture_simulation()
light = add_light_simulation
temperasture = add_temperature_simulation()
Data = pd.DataFrame({
    'Timestamp' : time_points,
    'Soil_moisture' : moisture_level,
    'Light_level' : light,
    'Temperature' : temperasture
})

print(Data.head())
print(Data.iloc[70:75])
    


