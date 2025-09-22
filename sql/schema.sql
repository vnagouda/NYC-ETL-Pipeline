CREATE TABLE IF NOT EXISTS trips_raw (
    vendor_id               INT,
    tpep_pickup_datetime    TIMESTAMP,
    tpep_dropoff_datetime   TIMESTAMP,
    passenger_count         INT,
    trip_distance           DOUBLE PRECISION,
    ratecode_id             INT,
    store_and_fwd_flag      TEXT,
    pu_location_id          INT,
    do_location_id          INT,
    payment_type            INT,
    fare_amount             DOUBLE PRECISION,
    extra                   DOUBLE PRECISION,
    mta_tax                 DOUBLE PRECISION,
    tip_amount              DOUBLE PRECISION,
    tolls_amount            DOUBLE PRECISION,
    improvement_surcharge   DOUBLE PRECISION,
    total_amount            DOUBLE PRECISION,
    congestion_surcharge    DOUBLE PRECISION,
    airport_fee             DOUBLE PRECISION
);

-- Cleaned/analytics table
CREATE TABLE IF NOT EXISTS trips_clean (
    pickup_ts               TIMESTAMP,
    dropoff_ts              TIMESTAMP,
    duration_min            DOUBLE PRECISION,
    distance_mi             DOUBLE PRECISION,
    passenger_count         INT,
    total_amount            DOUBLE PRECISION,
    tip_amount              DOUBLE PRECISION,
    pu_location_id          INT,
    do_location_id          INT
);

