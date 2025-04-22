import sqlite3
import pandas as pd
import glob
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE_DIR, 'csv runs')
DB_PATH = os.path.join(BASE_DIR, 'plantpulse.db')

def init_db():
    """Create readings table in SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS readings (
        timestamp TEXT,
        soil_moisture REAL,
        light_level REAL,
        temperature REAL,
        health_status TEXT
    )''')
    conn.commit()
    conn.close()

def migrate_csv_to_sqlite():
    """Migrate the latest CSV from csv runs to SQLite."""
    init_db()
    csv_files = glob.glob(os.path.join(CSV_DIR, 'plant_data_*.csv'))
    if not csv_files:
        print("No CSV files found in csv runs")
        return
    latest_csv = max(csv_files, key=os.path.getctime)
    try:
        df = pd.read_csv(latest_csv)
        # Rename CSV columns to match table
        column_mapping = {
            'Timestamp': 'timestamp',
            'Soilmoisture': 'soil_moisture',
            'Lightlevel': 'light_level',
            'Temperature': 'temperature',
            'Health_status': 'health_status'
        }
        df = df.rename(columns=column_mapping)
        # Validate columns
        expected_cols = ['timestamp', 'soil_moisture', 'light_level', 'temperature', 'health_status']
        if not all(col in df.columns for col in expected_cols):
            print(f"Error: CSV {latest_csv} missing required columns: {expected_cols}")
            return
        conn = sqlite3.connect(DB_PATH)
        df.to_sql('readings', conn, if_exists='replace', index=False)
        conn.close()
        print(f"Migrated {latest_csv} to {DB_PATH}")
    except Exception as e:
        print(f"Error during migration: {str(e)}")

if __name__ == '__main__':
    migrate_csv_to_sqlite()