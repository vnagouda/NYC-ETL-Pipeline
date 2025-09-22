import os
from dotenv import load_dotenv

load_dotenv()

PG_USER = os.getenv("POSTGRES_USER", "nyc_user")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "nyc_pass")
PG_DB   = os.getenv("POSTGRES_DB", "nyc_taxi")
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

NYC_YEAR  = os.getenv("NYC_YEAR", "2023")
NYC_MONTH = os.getenv("NYC_MONTH", "01")

# NYC tripdata URL pattern (Yellow taxi)
CSV_URL = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{NYC_YEAR}-{NYC_MONTH}.parquet"
# Some months are CSV; we’ll handle parquet via pandas.
LOCAL_RAW = f"data/raw/yellow_{NYC_YEAR}_{NYC_MONTH}.parquet"

