.PHONY: up down init run flow api

up:
\tdocker compose up -d --build

down:
\tdocker compose down -v

init:
\tpsql "postgresql://$${POSTGRES_USER}:$${POSTGRES_PASSWORD}@localhost:$${POSTGRES_PORT}/$${POSTGRES_DB}" -f sql/schema.sql

flow:
\tpython -m src.etl_flow

api:
\tuvicorn api.main:app --reload --port 8000

