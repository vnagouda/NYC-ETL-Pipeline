import polars as pl
import pandas as pd

def clean(path: str) -> pd.DataFrame:
    # Read parquet via Polars (no pyarrow needed), then convert to pandas
    pl_df = pl.read_parquet(path)
    df = pl_df.to_pandas()  # keep the rest of the pipeline in pandas

    rename_map = {
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
    df = df.rename(columns=rename_map)

    # Basic data quality filters
    df = df[
        (df["tpep_dropoff_datetime"] >= df["tpep_pickup_datetime"]) &
        (df["trip_distance"] >= 0) &
        (df["total_amount"].notna())
    ].copy()

    # Compute analytics columns
    df["duration_min"] = (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60.0
    df["distance_mi"] = df["trip_distance"]

    keep = [
        "tpep_pickup_datetime", "tpep_dropoff_datetime", "duration_min",
        "distance_mi", "passenger_count", "total_amount",
        "tip_amount", "pu_location_id", "do_location_id"
    ]
    clean_df = df[keep].copy().rename(columns={
        "tpep_pickup_datetime": "pickup_ts",
        "tpep_dropoff_datetime": "dropoff_ts"
    })

    return clean_df
