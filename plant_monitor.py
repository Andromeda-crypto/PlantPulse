# purpose of this file is to simulate and generate fake sensor which will create data
# such as soil moisture, light, temperature) over 7 days with hourly readings (168 total points).
import os
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
import random
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set matplotlib backend early
plt.switch_backend('TkAgg')

# Configuration
CONFIG = {
    'hours': 168,
    'moisture_threshold': 30,
    'light_threshold': 200,
    'temp_hot_threshold': 28,
    'csv_dir': 'csv_runs',
    'csv_filename': 'plant_data_latest.csv',
    'start_time': datetime.datetime(2025, 3, 1, 0, 0),
}

# Create output directory
os.makedirs(CONFIG['csv_dir'], exist_ok=True)

np.random.seed(42)

# Generate time points
time_points = [CONFIG['start_time'] + timedelta(hours=i) for i in range(CONFIG['hours'])]

def add_moisture_simulation():
    moisture = [50]
    watered_hours = [0]
    rain_hour = random.randint(20, 148) if random.random() < 0.05 else None

    for i in range(1, CONFIG['hours']):
        drop = random.uniform(0.5, 2.0)
        next_moisture = moisture[-1] - drop

        if i == rain_hour:
            next_moisture += random.uniform(20, 30)
            next_moisture = min(100, next_moisture)

        if next_moisture <= 20:
            next_moisture = 70
            watered_hours.append(i)
        moisture.append(next_moisture)

    return moisture

def add_light_simulation():
    light = []
    cloudy_starts = [i for i in range(0, CONFIG['hours'], 24) if random.random() < 0.10]
    cloudy_durations = {start: random.randint(3, 6) for start in cloudy_starts}

    for i in range(CONFIG['hours']):
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
    temperature = []
    heat_wave_start = random.randint(0, CONFIG['hours'] - 12) if random.random() < 0.075 else None
    heat_wave_duration = random.randint(12, 24) if heat_wave_start is not None else 0
    cold_snap_start = random.randint(0, CONFIG['hours'] - 12) if random.random() < 0.05 else None
    cold_snap_duration = random.randint(6, 12) if cold_snap_start is not None else 0

    for i in range(CONFIG['hours']):
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

def check_health(moisture, light, temperature):
    if moisture < CONFIG['moisture_threshold']:
        return 'Low moisture Plant needs more water'
    if light < CONFIG['light_threshold']:
        return 'Low light Plant needs more light'
    if temperature > CONFIG['temp_hot_threshold']:
        return 'Too Hot Plant should be exposed to less heat'
    return 'Plant is healthy All Good!'

def plot_plant_data(data):
    plt.figure(figsize=(12, 10))

    # Soil moisture
    plt.subplot(3, 1, 1)
    plt.plot(data['Timestamp'], data['Soilmoisture'], color='blue', label='Soil Moisture')
    low_moisture = data[data['Health_status'] == 'Low moisture Plant needs more water']
    plt.scatter(low_moisture['Timestamp'], low_moisture['Soilmoisture'], color='red', label='Low Moisture', s=50)
    plt.xlabel('Time')
    plt.ylabel('Moisture (%)')
    plt.title('Soil Moisture Over Time')
    plt.legend()
    plt.grid(True)

    # Light level
    plt.subplot(3, 1, 2)
    plt.plot(data['Timestamp'], data['Lightlevel'], color='orange', label='Light Level')
    low_light = data[data['Health_status'] == 'Low light Plant needs more light']
    plt.scatter(low_light['Timestamp'], low_light['Lightlevel'], color='yellow', label='Low Light', s=50)
    plt.xlabel('Time')
    plt.ylabel('Light (lux)')
    plt.title('Light Level Over Time')
    plt.legend()
    plt.grid(True)

    # Temperature
    plt.subplot(3, 1, 3)
    plt.plot(data['Timestamp'], data['Temperature'], color='red', label='Temperature')
    too_hot = data[data['Health_status'] == 'Too Hot Plant should be exposed to less heat']
    plt.scatter(too_hot['Timestamp'], too_hot['Temperature'], color='purple', label='Too Hot', s=50)
    plt.xlabel('Time')
    plt.ylabel('Temperature (°C)')
    plt.title('Temperature Over Time')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()

# Simulate data
moisture_level = add_moisture_simulation()
light = add_light_simulation()
temperature = add_temperature_simulation()

# Create DataFrame
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

# Save to CSV
csv_path = os.path.join(CONFIG['csv_dir'], CONFIG['csv_filename'])
Data.to_csv(csv_path, index=False)
logger.info(f"Data saved to {csv_path}")

# Watering prediction
last_moisture = Data['Soilmoisture'].iloc[-1]
drop_rate = Data['Soilmoisture'].iloc[-10:].diff().mean()
logger.info(f"Last moisture: {last_moisture:.2f}%")
logger.info(f"Drop rate: {drop_rate:.2f}%/hour")

if last_moisture < 20:
    logger.info(f"Water now at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}!")
else:
    hours_to_20 = (20 - last_moisture) / drop_rate
    hours_to_20_rounded = round(hours_to_20)
    next_time = datetime.datetime.now() + timedelta(hours=hours_to_20)
    logger.info(f"Water in {hours_to_20_rounded} hours at {next_time.strftime('%Y-%m-%d %H:%M')}")

# Plot initial data
plt.ion()
plot_plant_data(Data)
plt.show()

# Interactive menu
while True:
    print("\nWhat do you want to do?")
    print("1: Query hour")
    print("2: Zoom plot")
    print("3: Exit")
    choice = input("Enter choice (1-3): ")

    if choice == '1':
        try:
            hour = int(input("Enter hour (0-167): "))
            if 0 <= hour < CONFIG['hours']:
                row = Data.iloc[hour]
                print(f"\nHour {hour}:")
                print(f"Timestamp: {row['Timestamp']}")
                print(f"Soilmoisture: {row['Soilmoisture']:.2f}%")
                print(f"Lightlevel: {row['Lightlevel']:.2f} lux")
                print(f"Temperature: {row['Temperature']:.2f}°C")
                print(f"Health_status: {row['Health_status']}")
            else:
                print(f"Hour must be between 0 and {CONFIG['hours']-1}!")
        except ValueError:
            print("Please enter a valid number!")

    elif choice == '2':
        try:
            start_hour = int(input("Enter start hour (0-167): "))
            end_hour = int(input("Enter end hour (0-167): "))
            if not (0 <= start_hour <= 167 and 0 <= end_hour <= 167):
                print("Hours must be between 0 and 167!")
            elif start_hour > end_hour:
                print("Start hour must be less than or equal to end hour!")
            else:
                zoomed_data = Data.iloc[start_hour:end_hour + 1]
                plt.figure(figsize=(12, 10))
                plt.ion()
                plot_plant_data(zoomed_data)
                plt.show()
        except ValueError:
            print("Please enter valid numbers!")

    elif choice == '3':
        print("Exiting—see you next time!")
        break

    else:
        print("Invalid choice—pick 1, 2, or 3!")







    







