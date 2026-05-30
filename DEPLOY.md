# Deploying to Streamlit Community Cloud

The dashboard reads an **air-quality PostgreSQL + PostGIS** database. In
development that database runs in the bundled Docker container
(`docker compose up -d`). Streamlit Community Cloud runs on Streamlit's
servers and **cannot reach your laptop's Docker container or `localhost`**,
and the ~1.8 GB data directory is gitignored — so deploying the repo
as-is gives a running app that errors on every page with *"can't reach
its database."*

To deploy a working app you host the database once, point the app at it
with a secret, and (re)deploy. Three steps.

## 1. Create a hosted Postgres + PostGIS database (Neon)

1. Sign up at <https://neon.tech> and create a project (free tier is
   enough). Pick a region close to you.
2. In the project's **SQL Editor**, enable PostGIS:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```
3. Copy the **connection string** from *Dashboard → Connect*. Prefer the
   **direct** (non-pooled) string; it looks like:
   ```
   postgresql://USER:PASSWORD@ep-xxxx.eu-central-1.aws.neon.tech/DBNAME?sslmode=require
   ```

## 2. Load the data

With the dev container running, export the schema and load it into Neon:

```bash
# 1) dump the smartmonitoring schema (tables + data + the postgis line)
./scripts/export_for_deploy.sh            # -> deploy/smartmonitoring.sql

# 2) load it into Neon (needs the psql client locally)
psql "postgresql://USER:PASSWORD@ep-xxxx.../DBNAME?sslmode=require" \
  -f deploy/smartmonitoring.sql
```

The dump recreates the `smartmonitoring` schema with the sensor tables,
the `tbl_*` reference tables, and the `dashboard_*` user-content tables.
Benign `NOTICE` lines during load are fine. (The `deploy/*.sql` file is
gitignored — it's data, not code.)

> Free-tier storage is ~0.5 GB; the full dataset (~600k rows) fits. If you
> want a lighter demo DB, load a subset and re-run
> `scripts/add_dashboard_tables.py` against Neon to (re)create the
> user-content tables.

## 3. Point the app at the hosted DB and deploy

`src/db/connection.py` resolves the URL in this order:
`st.secrets["DATABASE_URL"]` → `$DATABASE_URL` → the local Docker default.
A bare `postgresql://` URL is accepted (the scheme is rewritten to use
psycopg 3).

On Community Cloud:

1. Push your branch to GitHub and create the app
   (repo, branch, main file `app.py`).
2. **App → Settings → Secrets**, add:
   ```toml
   DATABASE_URL = "postgresql://USER:PASSWORD@ep-xxxx.../DBNAME?sslmode=require"
   ```
3. Reboot the app. It should now connect and render.

To test the hosted DB locally before deploying, copy
`.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` (gitignored)
with the same `DATABASE_URL`, then `uv run streamlit run app.py`.

## Notes

- **Migrations on the hosted DB:** the `dashboard_*` tables come across in
  the dump. If you started from an older dump, run
  `DATABASE_URL=… uv run python scripts/add_dashboard_tables.py` to create
  them (it's idempotent).
- **Write-back features** (device/location edits, annotations, flags) write
  to the hosted DB. On a public deployment anyone with the link can use
  them — disable the optional modules from the **Manage** page if you want
  a read-only demo.
- **`requirements.txt`** is what Community Cloud installs; regenerate it
  after adding deps with the `uv export …` command in `CLAUDE.md`.
