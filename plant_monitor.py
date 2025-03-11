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
    hours = 168
    moisture = [50]  
    watered_hours = [0]

    rain_hour = random.randint(20, 148) if random.random() < 0.05 else None
    for i in range(1, hours):  
        drop = random.uniform(0.5, 2.0)
        next_moisture = moisture[-1] - drop

        if i == rain_hour:
            next_moisture += random.uniform(20, 30)
            if next_moisture > 100:
                next_moisture = 100

        if next_moisture <= 20:
            next_moisture = 70
            watered_hours.append(i)
        moisture.append(next_moisture)

    return moisture
       

def add_light_simulation():
    hours = 168
    light = []
    cloudy_starts = [i for i in range(0, hours, 24) if random.random() < 0.10]
    cloudy_durations = {start: random.randint(3, 6) for start in cloudy_starts}

    for i in range(hours):  # 168 iterations
        base_light = 500 + 500 * np.sin(2 * np.pi * (i % 24) / 24)
        if any(start <= i < start + cloudy_durations[start] for start in cloudy_starts):
            light_level = min(base_light, random.uniform(300, 500))
        else:
            light_level = base_light
        noise = random.uniform(-200, 200)
        light_level = max(0, min(1000, light_level + noise))
        light.append(light_level)

    return light


def add_temperature_simulation():
    hours = 168
    temperature = []
    heat_wave_start = random.randint(0, 156) if random.random() < 0.075 else None
    heat_wave_duration = random.randint(12, 24) if heat_wave_start is not None else 0
    cold_snap_start = random.randint(0, 156) if random.random() < 0.05 else None
    cold_snap_duration = random.randint(6, 12) if cold_snap_start is not None else 0

    for i in range(hours):  # 168 iterations
        base_temp = 22 + 5 * np.sin(2 * np.pi * (i % 24) / 24)
        if heat_wave_start and heat_wave_start <= i < heat_wave_start + heat_wave_duration:
            temp = random.uniform(29, 32)
        elif cold_snap_start and cold_snap_start <= i < cold_snap_start + cold_snap_duration:
            temp = random.uniform(14, 16)
        else:
            temp = base_temp
        noise = random.uniform(-2, 2)
        temp = max(10, min(35, temp + noise))
        temperature.append(temp)

    return temperature




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

# Debug lengths
print(f"Length of time_points: {len(time_points)}")
print(f"Length of moisture_level: {len(moisture_level)}")
print(f"Length of light: {len(light)}")
print(f"Length of temperature: {len(temperature)}")

Data = pd.DataFrame({
    'Timestamp': time_points,
    'Soilmoisture': moisture_level,
    'Lightlevel': light,
    'Temperature': temperature
})
Data['Health_status'] = Data.apply(
    lambda row: check_health(row['Soilmoisture'], row['Lightlevel'], row['Temperature']),
    axis=1
)
plot_plant_data(Data)

current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
filename = f'plant_data_{current_time}.csv'
Data.to_csv(filename, index=False)
print(f"Data saved to {filename}")

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



print(Data.head())
print(Data.iloc[10:15]) # midday peak
print(Data.iloc[22:26]) # midnight low
print(Data.iloc[70:75])
print(Data.iloc[163:168]) # testing to see the last 5 data points'''


