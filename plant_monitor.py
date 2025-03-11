# purpose of this file is to simulate and generate fake sensor which will create data
# such as soil moisture, light, temperature) over 7 days with hourly readings (168 total points).

import datetime
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
import math
import random

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
        light.append(light_value)

    return light



def add_temperature_simulation():
    # similar logic to light using sin wave to simulate temperature
    temperature = []
    for i in range(168):
        base_value = 22 + 5 * math.sin(math.pi * i/12)
        temperature_value = base_value + np.random.uniform(-1,1)
        if temperature_value < 0:
            temperature_value = 0
        elif temperature_value > 40:
            temperature_value = 40
        
        temperature.append(temperature_value)
    return temperature
    
# health check function

def check_health(moisture,light,temperature):
    # check for moisture first, if it is low no need to check for the rest
    # need to prioritize mositure because it is critical for plant health
    if moisture < 30:
      return 'Low moisture Plant needs more water'
    if light < 200:
        return 'Low light Plant needs more light'
    if temperature > 28:
       return 'Too Hot Plant should be exposed to less heat'
    return 'Plant is healthy All Good!'

def plot_plant_data(data):
    # plotting the data

    plt.figure(figsize=(12, 10))

    # Soilmoisture with Low moisture markers
    plt.subplot(3, 1, 1)
    plt.plot(Data['Timestamp'], Data['Soilmoisture'], color='blue', label='Soil Moisture')
    low_moisture = Data[Data['Health_status'] == 'Low moisture Plant needs more water']
    plt.scatter(low_moisture['Timestamp'],low_moisture['Soilmoisture'], color='red', label='Low Moisture', s=50)
    plt.xlabel('Time')
    plt.ylabel('Moisture (%)')
    plt.title('Soil Moisture Over Time')
    plt.legend()
    plt.grid(True)

    #  Lightlevel with Low light markers
    plt.subplot(3, 1, 2)
    plt.plot(Data['Timestamp'], Data['Lightlevel'], color='orange', label='Light Level')
    low_light = Data[Data['Health_status'] == 'Low light Plant needs more light']
    plt.scatter(low_light['Timestamp'], low_light['Lightlevel'], color='yellow', label='Low light', s=50)
    plt.xlabel('Time')
    plt.ylabel('Light (lux)')
    plt.title('Light Level Over Time')
    plt.legend()
    plt.grid(True)

    #  Temperature with Too Hot markers
    plt.subplot(3, 1, 3)
    plt.plot(Data['Timestamp'], Data['Temperature'], color='red', label='Temperature')
    too_hot = Data[Data['Health_status'] == 'Too Hot Plant should be exposed to less heat']
    plt.scatter(too_hot['Timestamp'], too_hot['Temperature'], color='purple', label='Too Hot', s=50)
    plt.xlabel('Time')
    plt.ylabel('Temperature (°C)')
    plt.title('Temperature Over Time')
    plt.legend()
    plt.grid(True)

    # Adjust layout and show
    plt.tight_layout()
    plt.show()
   
    
# testing
moisture_level = add_moisture_simulation()
light = add_light_simulation()
temperature = add_temperature_simulation()
Data = pd.DataFrame({
    'Timestamp' : time_points,
    'Soilmoisture' : moisture_level,
    'Lightlevel' : light,
    'Temperature' : temperature
    })
Data['Health_status'] = Data.apply(lambda row: check_health(row['Soilmoisture'],row['Lightlevel'],row['Temperature']),axis = 1)

plot_plant_data(Data)
current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')  
filename = f'plant_data_{current_time}.csv'  
Data.to_csv(filename, index=False)
print(f"Data saved to {filename}")

# ADDING A PREDICTIVE MODEL TO TELL US WHEN THE PLANT WILL NEED WATER
# The model will use the moisture data to predict when the plant will need water

last_moisture = Data['Soilmoisture'].iloc[-1]
drop_rate = Data['Soilmoisture'].iloc[-10:].diff().mean()
print(f"Last moisture: {last_moisture}")
print(f"Drop rate: {drop_rate}")

if last_moisture < 20:
    print(f"Water now at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}!")
else:
    hours_to_20 = (20 - last_moisture) / drop_rate
    hours_to_20_rounded = round(hours_to_20)
    next_time = datetime.datetime.now() + timedelta(hours=hours_to_20)
    next_time_str = next_time.strftime('%Y-%m-%d %H:%M')
    print(f"Water in {hours_to_20_rounded} hours at {next_time_str}")


'''print(Data.head())
print(Data.iloc[10:15]) # midday peak
print(Data.iloc[22:26]) # midnight low
print(Data.iloc[70:75])
print(Data.iloc[163:168]) # testing to see the last 5 data points'''


