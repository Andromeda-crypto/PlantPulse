import sqlite3
import pandas as pd
import glob
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE_DIR, 'csv runs')

def init_db():
    conn = sqlite3.connect('plantpulse.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS readings(
                 timestamp TEXT,
                 soil_moisture REAL,    
                 light_level REAL,
                 temperature REAL,
                 health_status TEXT
                 )''')
    conn.commit()
    conn.close()

def migrate_csv_to_sqlite():
    init_db()
    csv_files = glob.glob(os.path.join(CSV_DIR,'plant_data_*.csv'))
    if not  csv_files:
        print("No CSVs found.")
        return
    latest_csv = max(csv_files,key=os.path.getctime)
    df =pd.read_csv(latest_csv)
    conn = sqlite3.connect('plantpulse.db')
    df.to_sql('readings', conn , if_exists='replace', index=False)
    conn.close()
    print(f"Migrate {latest_csv} to SQLite")

if __name__ =='__main__':
    migrate_csv_to_sqlite()
