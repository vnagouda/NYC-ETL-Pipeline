from fastapi import FastAPI
from sqlalchemy import text
from src.db import pg_engine  # absolute import so it works from host

app = FastAPI(title="NYC Taxi Analytics API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/kpis/avg_fare_per_mile")
def avg_fare_per_mile():
    sql = """
        SELECT AVG(total_amount / NULLIF(distance_mi,0)) AS v
        FROM trips_clean
        WHERE distance_mi > 0 AND total_amount > 0;
    """
    eng = pg_engine()
    with eng.connect() as conn:
        val = conn.execute(text(sql)).scalar()
    return {"avg_fare_per_mile": float(val) if val is not None else None}

@app.get("/kpis/avg_tip_pct")
def avg_tip_pct():
    # tip % of total; simple + robust
    sql = """
        SELECT 100.0 * SUM(tip_amount) / NULLIF(SUM(total_amount),0) AS v
        FROM trips_clean
        WHERE total_amount > 0 AND tip_amount >= 0;
    """
    eng = pg_engine()
    with eng.connect() as conn:
        val = conn.execute(text(sql)).scalar()
    return {"avg_tip_pct": float(val) if val is not None else None}

@app.get("/kpis/median_duration_min")
def median_duration_min():
    sql = """
        SELECT PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY duration_min) AS v
        FROM trips_clean
        WHERE duration_min > 0;
    """
    eng = pg_engine()
    with eng.connect() as conn:
        val = conn.execute(text(sql)).scalar()
    return {"median_duration_min": float(val) if val is not None else None}

@app.get("/kpis/trips_by_hour")
def trips_by_hour():
    sql = """
        SELECT EXTRACT(HOUR FROM pickup_ts)::int AS hour, COUNT(*)::bigint AS trips
        FROM trips_clean
        GROUP BY 1
        ORDER BY 1;
    """
    eng = pg_engine()
    with eng.connect() as conn:
        rows = [dict(r._mapping) for r in conn.execute(text(sql))]
    return {"trips_by_hour": rows}

@app.get("/kpis/top_routes")
def top_routes(limit: int = 10):
    sql = """
        SELECT pu_location_id, do_location_id,
               COUNT(*)::bigint AS trips,
               ROUND(AVG(duration_min)::numeric, 2) AS avg_duration_min
        FROM trips_clean
        GROUP BY pu_location_id, do_location_id
        ORDER BY trips DESC
        LIMIT :lim;
    """
    eng = pg_engine()
    with eng.connect() as conn:
        rows = [dict(r._mapping) for r in conn.execute(text(sql), {"lim": limit})]
    return {"top_routes": rows}
