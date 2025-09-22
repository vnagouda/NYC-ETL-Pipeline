import polars as pl
import pandas as pd
from .db import pg_engine

# Stay under Postgres' 65535 param limit
MAX_PARAMS = 60000

def _safe_chunksize(num_cols: int) -> int:
    return max(1000, int(MAX_PARAMS / max(1, num_cols)))

# Columns exactly as created in sql/schema.sql
RAW_SCHEMA_COLS = [
    "vendor_id",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "ratecode_id",
    "store_and_fwd_flag",
    "pu_location_id",
    "do_location_id",
    "payment_type",
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "congestion_surcharge",
    "airport_fee",
]

# Map parquet -> table column names
RENAME_MAP = {
    "VendorID": "vendor_id",
    "tpep_pickup_datetime": "tpep_pickup_datetime",
    "tpep_dropoff_datetime": "tpep_dropoff_datetime",
    "passenger_count": "passenger_count",
    "trip_distance": "trip_distance",
    "RatecodeID": "ratecode_id",
    "store_and_fwd_flag": "store_and_fwd_flag",
    "PULocationID": "pu_location_id",
    "DOLocationID": "do_location_id",
    "payment_type": "payment_type",
    "fare_amount": "fare_amount",
    "extra": "extra",
    "mta_tax": "mta_tax",
    "tip_amount": "tip_amount",
    "tolls_amount": "tolls_amount",
    "improvement_surcharge": "improvement_surcharge",
    "total_amount": "total_amount",
    "congestion_surcharge": "congestion_surcharge",
    "Airport_fee": "airport_fee",
    "airport_fee": "airport_fee",
}

def _align_to_raw_schema(df: pd.DataFrame) -> pd.DataFrame:
    # rename to snake_case expected by the table
    df = df.rename(columns=RENAME_MAP)

    # ensure required columns exist; fill missing with NA
    for col in RAW_SCHEMA_COLS:
        if col not in df.columns:
            df[col] = pd.NA

    # keep only the columns the table has, in order
    df = df[RAW_SCHEMA_COLS].copy()

    # cast datetimes
    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
    return df

def load_raw(parquet_path: str):
    # read parquet with Polars (no pyarrow needed), convert to pandas
    pl_df = pl.read_parquet(parquet_path)
    pdf = pl_df.to_pandas()
    pdf = _align_to_raw_schema(pdf)

    eng = pg_engine()
    cs = min(_safe_chunksize(len(pdf.columns)), 2000)  # extra safety
    pdf.to_sql(
        "trips_raw",
        eng,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=cs,
    )

def load_clean(df: pd.DataFrame):
    eng = pg_engine()
    cs = min(_safe_chunksize(len(df.columns)), 4000)
    df.to_sql(
        "trips_clean",
        eng,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=cs,
    )
