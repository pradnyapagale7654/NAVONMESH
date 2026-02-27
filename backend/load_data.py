import pandas as pd
import sqlite3
import os

# paths
DATASET_PATH = "dataset/machine_energy.csv"
DB_PATH = "database/energy.db"


def create_database_folder():
    if not os.path.exists("database"):
        os.makedirs("database")


def clean_columns(df):
    """
    Rename columns safely for SQLite compatibility
    """

    rename_map = {
        "Load_%": "Load_percent",
        "Load%": "Load_percent",
        "Load": "Load_percent"
    }

    df = df.rename(columns=rename_map)

    return df


def create_table(conn):
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS energy_data (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        Machine_ID TEXT,
        Machine_Model TEXT,
        Rated_Capacity_kW REAL,

        Timestamp TEXT,

        Power_kW REAL,
        Energy_kWh REAL,
        Production_Output REAL,

        Load_percent REAL,
        Power_Factor REAL,
        Temperature REAL,

        Operating_Status TEXT,
        Shift TEXT,
        Operator_ID TEXT,

        Electricity_Tariff REAL,
        Maintenance_Cost_per_hour REAL,

        CO2_Emission_Factor REAL

    )
    """)

    conn.commit()


def load_csv_to_db():

    print("Reading dataset...")

    df = pd.read_csv(DATASET_PATH)

    df = clean_columns(df)

    create_database_folder()

    conn = sqlite3.connect(DB_PATH)

    print("Creating table...")
    create_table(conn)

    print("Inserting data...")

    df.to_sql(
        "energy_data",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print("SUCCESS: energy.db created and dataset loaded.")


if __name__ == "__main__":
    load_csv_to_db()