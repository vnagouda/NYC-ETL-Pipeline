# Plain-Python ETL runner (no Prefect) for Python 3.13 compatibility

from .extract import download_raw
from .transform import clean
from .load import load_raw, load_clean
from .db import execute_sql

def ensure_schema():
    with open("sql/schema.sql", "r", encoding="utf-8") as f:
        execute_sql(f.read())

def run_monthly_etl():
    print("Ensuring schema...")
    ensure_schema()

    print("Extracting raw parquet...")
    raw_path = download_raw()

    print("Transforming data...")
    df_clean = clean(raw_path)

    print("Loading raw into trips_raw...")
    load_raw(raw_path)

    print("Loading cleaned into trips_clean...")
    load_clean(df_clean)

    print("ETL complete ✅")

if __name__ == "__main__":
    run_monthly_etl()
