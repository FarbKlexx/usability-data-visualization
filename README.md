# Air Quality Usability Dashboard

A Streamlit dashboard built for the Usability course. The design
principles that drive every decision — Visual Perception, Gestalt,
Cognitive Load, Shneiderman, Accessibility — live in
[CONTEXT.md](CONTEXT.md). Read it before adding features.

## Quickstart

Requires [uv](https://docs.astral.sh/uv/), Docker, and Python ≥ 3.12.

```bash
# 1. Install Python dependencies
uv sync

# 2. Materialise the Postgres data directory (copies pgsql/ -> pgdata/
#    and patches Windows-era config so the Linux container can boot).
#    Idempotent; pass --force to recreate.
./scripts/setup-db.sh

# 3. Start the Postgres container (binds pgdata/ into postgres:13-alpine)
docker compose up -d

# 4. Configure credentials
cp .env.example .env          # default targets the local container

# 5. Verify the DB is reachable
uv run python scripts/check_db.py

# 6. Run the app
uv run streamlit run app.py
```

The app opens at <http://localhost:8501>. The database is exposed on
`localhost:5432` (no password — trust auth for local development).
A browser-based DB explorer (pgweb) runs alongside at
<http://localhost:8081> — auto-connects on startup, no login.
Schema documentation lives in [`docs/data_schema.md`](docs/data_schema.md).

### Common DB commands

```bash
docker compose up -d            # start
docker compose logs -f db       # tail logs
docker compose down             # stop (data is preserved in ./pgdata)
./scripts/setup-db.sh --force   # nuke pgdata/ and recopy from pgsql/

# Interactive psql
docker exec -it usability-db psql \
  -U smartmonitoring_airquality -d smartmonitoring_airquality
```

## Tests

```bash
uv run pytest
```

## Project layout

| Path              | Purpose                                              |
| ----------------- | ---------------------------------------------------- |
| `app.py`          | Entry point — registers pages via `st.navigation`.   |
| `app_pages/`      | One module per page; UI only, no data wrangling.     |
| `src/components/` | Reusable UI primitives (KPI tile, filter bar, …).    |
| `src/data/`       | Cached loaders for Postgres dump / CSV / Parquet.    |
| `src/db/`         | Cached SQLAlchemy engine + reusable SQL.             |
| `src/utils/`      | Palettes, formatters, accessibility helpers.         |
| `assets/`         | Static files (logos, sample data, images).           |
| `docs/`           | Architecture & data-schema reference.                |
| `scripts/`        | `setup-db.sh` + standalone CLI helpers.              |
| `tests/`          | Pytest suite — start with import smoke tests.        |
| `.streamlit/`     | Theme + runtime config (never customize via CSS).    |
| `docker-compose.yml` | Local Postgres 13 service (binds `pgdata/`).      |

## Status

Foundation only — no features yet.
