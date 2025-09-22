# NYC Taxi — ETL → Postgres → FastAPI (Portfolio Project)

**An end-to-end, production-style data pipeline** that ingests millions of NYC Yellow Taxi trips each month, cleans & models the data, loads it into a warehouse (Postgres), and serves KPIs via a small API.

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.13-blue" />
  <img alt="Postgres" src="https://img.shields.io/badge/Postgres-16-316192" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-live-green" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow" />
</p>

## Highlights

- **ETL at scale:** 3M+ rows/month (Jan 2023 alone ≈ 3.06M).
- **Warehouse design:** `trips_raw` (ingestion) + `trips_clean` (analytics).
- **API for metrics:** FastAPI endpoints (avg fare/mile, etc.).
- **Ops realism:** Handles schema drift, Postgres parameter limits, container networking, Windows quirks.

---

## Architecture

```
NYC TLC Trip Data (parquet, monthly, public)
        │
   [Extract]  download parquet → data/raw/
        │
   [Transform]  clean + derive: duration_min, distance_mi, etc.
        │
   [Load]
   ├── trips_raw  (append-only, near-source schema)
   └── trips_clean (curated analytics table)
        │
   [Serve]  FastAPI KPIs  +  (optional) Metabase dashboards
```

---

## Tech Stack

- **Python** (pandas, **polars** for parquet on Windows/Py 3.13)
- **SQLAlchemy + psycopg (v3)** for Postgres
- **Docker Compose** (Postgres, Adminer, Metabase)
- **FastAPI + Uvicorn** for a small analytics service

> Prefect is included but not required on Python 3.13. The ETL runner is plain Python; you can switch to Prefect easily if you use Python 3.12.

---

## Dataset

NYC TLC Yellow Taxi monthly parquet files (public). Example used: **2023-01**.

---

## Project Structure

```
nyc-taxi-etl-warehouse/
├─ docker-compose.yml
├─ .env.example  → copy to .env
├─ requirements.txt
├─ README.md
├─ src/
│  ├─ etl_flow.py        # plain-Python ETL runner (3.13-friendly)
│  ├─ extract.py         # downloads parquet
│  ├─ transform.py       # cleans + features (uses polars→pandas)
│  ├─ load.py            # safe chunked inserts into Postgres
│  ├─ db.py              # SQLAlchemy engine (psycopg v3)
│  └─ settings.py        # env + dataset URL builder
├─ sql/
│  └─ schema.sql         # creates trips_raw + trips_clean
├─ api/
│  ├─ main.py            # FastAPI endpoints
│  └─ Dockerfile
└─ data/
   ├─ raw/
   └─ processed/
```

---

## Quickstart (Windows / CMD)

### 0) Prereqs

- Docker Desktop
- Python 3.13 (works), pip

### 1) Install deps

```bat
pip install -r requirements.txt
```

### 2) Configure environment

Copy and edit:

```bat
copy .env.example .env
```

**.env** (defaults are fine for local host runs):

```
POSTGRES_USER=nyc_user
POSTGRES_PASSWORD=nyc_pass
POSTGRES_DB=nyc_taxi
POSTGRES_HOST=localhost   # host runs use localhost; inside Docker use 'postgres'
POSTGRES_PORT=5432

NYC_YEAR=2023
NYC_MONTH=01
```

### 3) Start infrastructure

```bat
docker compose up -d --build
```

- Postgres → `localhost:5432`
- Adminer → http://localhost:8080
- Metabase → http://localhost:3000

### 4) Create tables

> On Windows, feed the SQL file into `psql`:

```bat
docker exec -i nyc_pg psql -U nyc_user -d nyc_taxi < sql\schema.sql
```

### 5) Run the ETL

```bat
python -m src.etl_flow
```

You should see: _ETL complete ✅_

### 6) Verify in Adminer

Open **http://localhost:8080**.  
Login (because Adminer runs **in Docker**):

- System: **PostgreSQL**
- Server: **postgres**
- Username: `nyc_user`
- Password: `nyc_pass`
- Database: `nyc_taxi`

Run:

```sql
SELECT COUNT(*) AS raw_rows   FROM trips_raw;
SELECT COUNT(*) AS clean_rows FROM trips_clean;
SELECT AVG(total_amount/NULLIF(distance_mi,0)) AS avg_fare_per_mile
FROM trips_clean WHERE distance_mi>0 AND total_amount>0;
```

### 7) Run the API (host)

```bat
uvicorn api.main:app --reload --port 8000
```

- Health: `GET http://localhost:8000/health`
- KPI: `GET http://localhost:8000/kpis/avg_fare_per_mile`
- Docs: `http://localhost:8000/docs`

> If you run the API **in Docker**, set `POSTGRES_HOST=postgres` in `.env`, then `docker compose up -d --build`.

---

## Optional: More API Endpoints

Add these (or use the provided version in `api/main.py`):

- `GET /kpis/avg_tip_pct`
- `GET /kpis/median_duration_min`
- `GET /kpis/trips_by_hour`
- `GET /kpis/top_routes?limit=10`

They return JSON for dashboards / demos. Open `/docs` for Swagger UI.

---

## Loading More Months

Append another month without editing files:

```bat
set NYC_YEAR=2023 && set NYC_MONTH=02 && python -m src.etl_flow
set NYC_YEAR=2023 && set NYC_MONTH=03 && python -m src.etl_flow
```

Both `trips_raw` and `trips_clean` will grow.

---

## (Optional) Metabase

With Compose running:

- Open http://localhost:3000
- Add a Postgres connection:
  - **Host:** `postgres`
  - **DB:** `nyc_taxi`
  - **User/Pass:** from `.env`

Suggested starter questions/charts:

- Trips by pickup hour
- Avg tip % by hour
- Top (PU, DO) routes (count + avg duration)
- Distribution of duration (box / histogram)

---

## Troubleshooting

**Adminer: “connection refused to localhost:5432”**  
Use **Server: `postgres`** (Adminer runs in Docker). From host tools (psql, Python), use `localhost`.

**pandas parquet read fails on Python 3.13**  
We use **polars** to read parquet, then convert to pandas—no `pyarrow` build needed.

**SQLAlchemy error `e3q8` (too many parameters)**  
Postgres caps query parameters at 65,535. We insert with **safe chunk sizes** in `load.py`. If needed, reduce `chunksize` further.

**SQLAlchemy error `f405` (column mismatch)**  
Raw loader aligns parquet columns to the table schema (`load.py`), including renames (e.g., `VendorID` → `vendor_id`).

**Reset tables after partial loads**

```bat
docker exec -it nyc_pg psql -U nyc_user -d nyc_taxi -c "TRUNCATE trips_clean, trips_raw;"
```

---

## What This Shows (for your Resume)

- Built a monthly **ETL** that ingests **3M+ rows**/month of NYC taxi trips, cleans & models data, and loads **raw** and **analytics** tables in **Postgres**.
- Exposed **KPIs via FastAPI** (avg fare/mile, tip %, median duration, trips by hour); added indexes for snappy queries.
- Solved real-world issues: parquet ingestion on Windows/Python 3.13 (no pyarrow), **Postgres parameter limit**, container networking (Adminer/Metabase vs host).

---

## Next Steps

- Switch to **Prefect** orchestration (use Python 3.12), add schedules & retries.
- Add **dbt** models + tests for `trips_clean`.
- Train a small **ML model** (predict `duration_min`) and serve it with FastAPI.
- Add **GitHub Actions** (lint/test/build), Dockerize the ETL job container.

---

**License:** MIT
**Author:** Viresh Nagouda — happy to accept PRs/issues ✨
