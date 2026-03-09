# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A containerized 3-tier web app for tracking personal health telemetry (calories, weight, steps). All services are orchestrated via Docker Compose and use Containerfiles (not Dockerfiles).

## Services

| Service | Tech | Port |
|---|---|---|
| `db` | PostgreSQL 16 (Alpine) | 5432 |
| `telemetry-api` | FastAPI + Python 3.12 + uv | 8000 |
| `frontend` | Static HTML/JS (nginx) | 8081 |

## Running the Stack

```bash
# Requires a .env file at the root with DATABASE_URL and Postgres credentials
docker compose up --build      # Build and start all services
docker compose up --build -d   # Detached mode
docker compose down            # Stop services
docker compose down -v         # Stop and remove volumes (wipes DB)
```

Health check endpoints:
- `GET http://localhost:8000/healthz` — API liveness
- `GET http://localhost:8000/db-healthz` — DB connectivity check

## telemetry-api Development

The API uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
cd telemetry-api

# Install dependencies
uv sync

# Run locally (requires DATABASE_URL env var set)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Add a dependency
uv add <package>
```

No test framework is currently configured.

## API Architecture

```
app/
  main.py          # FastAPI app entry point, mounts router
  api/routes.py    # All route handlers (healthz, db-healthz, POST /metrics)
  core/config.py   # DATABASE_URL read from environment
  schemas/telemetry.py  # Pydantic model: MetricPayload(user_id, metric_name, metric_value)
```

Routes use raw `psycopg` (v3) connections — no ORM. Each request opens and closes its own connection.

## Database Schema

Two tables: `users` (id, username, email, created_at) and `metrics` (id, user_id FK, metric_name, metric_value, recorded_at). A default `admin` user (id=1) is seeded by `database/init.sql` on first boot.

## Environment Variables

The root `.env` file (gitignored) is passed to both `db` and `telemetry-api` services. It must contain:
- `DATABASE_URL` — psycopg connection string for the API
- Standard Postgres env vars (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`) for the db service