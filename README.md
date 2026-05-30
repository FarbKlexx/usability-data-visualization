# Air Quality Usability Dashboard

A Streamlit air-quality dashboard for a network of particulate-matter
sensors (around Minden, plus two external feeds and two **mobile** units),
built for a university **Usability course**. It is judged on how well the UI
applies established usability theory — those principles live in
[CONTEXT.md](CONTEXT.md) and drive every design decision.

- **Using the app?** → [docs/USER_MANUAL.md](docs/USER_MANUAL.md) — what you can
  see and do on every page, plus common tasks.
- **Working on the code?** → [CLAUDE.md](CLAUDE.md) for architecture &
  conventions, [CONTEXT.md](CONTEXT.md) for the usability rubric.
- **Deploying?** → [DEPLOY.md](DEPLOY.md) — Streamlit Community Cloud + a hosted
  Postgres + PostGIS instance.

## What you can do

Six pages, reachable from the top navigation bar:

| Page | What it's for |
| --- | --- |
| **Dashboard** | Adaptive hub: pick any device → a plain-language air-quality status + **one** headline visual — a PM trend + location marker for stationary/fixed sensors, or a **segmented route map** (PM-coloured trips) for mobile ones. Secondary tabs hold KPIs/measures, a verdict-first **correlation** view, and (for mobile) route tools. |
| **Time Series** | Deep single-sensor exploration: aggregation bucket, rolling average, raw/clean toggle, reference thresholds, CSV export, bookmarkable URLs; optional annotations, reading flags, and a particle-size drill-down. |
| **Map** | Sensor locations (coloured by computed CAQI) + mobile tracks; details-on-demand with a hand-off to Time Series; edit a location. |
| **Comparison** | One measure across many sensors — average bars + distribution box plots + CSV. |
| **Devices & Data Quality** | Device catalogue, data-availability timeline, an honest audit of the data's quirks; edit device metadata. |
| **Manage** | Toggle optional modules; manage saved thresholds and saved views. |

The full, screen-by-screen walkthrough is in
**[docs/USER_MANUAL.md](docs/USER_MANUAL.md)**.

> **Note on dates:** the dataset is *frozen* (it ends in late 2025), so the
> time-range presets ("last 24 h / 7 d / 30 d") are relative to the newest
> reading in the data, not today.

## Quickstart

Requires [uv](https://docs.astral.sh/uv/), Docker, and Python ≥ 3.12.

```bash
# 1. Install Python dependencies
uv sync

# 2. Materialise the Postgres data directory (copies pgsql/ -> pgdata/
#    and patches Windows-era config so the Linux container can boot).
#    Idempotent; pass --force to recreate.
./scripts/setup-db.sh

# 3. Start the Postgres + PostGIS container (binds pgdata/)
docker compose up -d

# 4. Configure credentials
cp .env.example .env          # default targets the local container

# 5. Verify the DB is reachable
uv run python scripts/check_db.py

# 6. Run the app
uv run streamlit run app.py
```

The app opens at <http://localhost:8501>. The database is exposed on
`localhost:5432` (no password — trust auth for local development). A
browser-based DB explorer (pgweb) runs alongside at <http://localhost:8081> —
auto-connects on startup, no login. The authoritative, live-verified schema
reference is [`docs/data_schema_full.md`](docs/data_schema_full.md)
(`docs/data_schema.md` is a superseded earlier draft).

### Optional: write-back features

Time Series annotations & reading flags, saved thresholds, and saved views
(plus the Manage page's persisted state) need four extra `dashboard_*` tables:

```bash
uv run python scripts/add_dashboard_tables.py    # --dry-run to preview, --drop to reverse
```

Without them the app runs **read-only** and says so plainly; the feature-flag
toggles on the Manage page still work. An optional index migration speeds up
time-range queries:

```bash
uv run python scripts/add_ts_indexes.py
```

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
uv run pytest                   # the whole suite
```

The suite splits into **pure** tests (no DB — registry / cleaning / CAQI /
correlation / route-segmentation logic) and **DB-gated** integration tests
that **skip cleanly** when Postgres is unreachable, so it still passes in
pip-only or CI environments.

## Deployment

Streamlit Community Cloud can't reach a local Docker container, so a deploy
needs a **hosted Postgres + PostGIS** instance and a `DATABASE_URL` secret.
The full walkthrough (export the schema, load it into a Neon free-tier DB,
point the app at it) is in **[DEPLOY.md](DEPLOY.md)**. `requirements.txt` is
the pip-only fallback Streamlit Cloud installs from — regenerate it after
adding dependencies (see [CLAUDE.md](CLAUDE.md)).

## Project layout

| Path | Purpose |
| --- | --- |
| `app.py` | Entry point — registers the six pages via `st.navigation` + a DB-health guard. |
| `app_pages/` | One module per page (dashboard, timeseries, map, comparison, devices, manage); UI only. |
| `src/components/` | Reusable UI primitives — charts, KPI tiles, the filter-bar toolbar. |
| `src/data/` | Cached loaders (the only place pages get data). |
| `src/db/` | Cached SQLAlchemy engine, the SQL-injection allowlist, and the transactional write-back API. |
| `src/utils/` | Palette, metric registry, sentinel cleaning, CAQI, correlation maths, cross-page state. |
| `docs/` | [User manual](docs/USER_MANUAL.md), authoritative [schema](docs/data_schema_full.md), and the implementation plans. |
| `scripts/` | `setup-db.sh`, the migrations, the deploy export, and `check_db.py`. |
| `tests/` | Pytest suite (pure + DB-gated). |
| `.streamlit/` | Theme + runtime config (styling goes here, never via raw CSS). |
| `docker-compose.yml` | Local Postgres 13 + PostGIS service (binds `pgdata/`). |
| `DEPLOY.md` / `requirements.txt` | Hosted-deploy guide + the pip-only dependency fallback. |

## Status

Feature-complete across the planned phases — baseline dashboard →
interactivity → database write-back → consolidation (dashboard-as-hub) →
adaptive device view & mobile routes — and **deployable** to Streamlit
Community Cloud against a hosted Postgres + PostGIS database.
