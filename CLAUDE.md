# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

An **Air Quality dashboard** built with Streamlit, delivered for a
university **Usability course**. The deliverable is judged on how
well the UI applies established usability theory — not just on whether
it ships features.

The full theoretical brief lives in [CONTEXT.md](CONTEXT.md). Skim it
before designing any new view. Key constraints that should shape every
PR:

- **Miller's 7±2** — at most ~7 KPIs/widgets per view; group the rest into tabs/drill-downs.
- **Color is never the only channel** — pair with shape/label/position; the categorical palette is Okabe-Ito (see `src/utils/palette.py`), sequential is Viridis.
- **Direct manipulation** — prefer brush/zoom/click-legend over separate filter panels.
- **Shneiderman #3 (feedback) and #6 (reversal)** — every filter shows confirmation; "Reset" must always be reachable.
- **Honest data** — no truncated Y-axes without a notice; no chart junk.
- **44×44 px** minimum touch targets.

## Commands

This project uses [uv](https://docs.astral.sh/uv/) for dependency
management. The lockfile (`uv.lock`) is the source of truth;
`requirements.txt` is a generated fallback for pip-only environments.

```bash
uv sync                                # install / update deps from uv.lock
uv run streamlit run app.py            # dev server (http://localhost:8501)
uv run python scripts/check_db.py      # smoke-test the DB connection
uv run pytest                          # run all tests
uv run pytest tests/test_smoke.py::test_palette_is_colorblind_safe   # single test
uv add <pkg>                           # add runtime dep + update lockfile
uv add --dev <pkg>                     # add dev dep
uv export --format requirements-txt --no-hashes --no-dev \
  --output-file requirements.txt       # regenerate requirements.txt after adding deps
```

Database commands:

```bash
./scripts/setup-db.sh                  # idempotent: copy pgsql/ -> pgdata/ + patch config
./scripts/setup-db.sh --force          # nuke pgdata/ and recopy
docker compose up -d                   # start Postgres 13 container
docker compose logs -f db              # tail logs
docker compose down                    # stop (data preserved in pgdata/)
docker exec -it usability-db psql \
  -U smartmonitoring_airquality -d smartmonitoring_airquality
```

Python is pinned to `>=3.12` in `pyproject.toml`. uv will provision a
compatible interpreter on first `uv sync` if none is available.

## Architecture

```
app.py              ── thin router: page_config + st.navigation
app_pages/*.py      ── one module per page; UI only
src/
  components/       ── reusable UI primitives (KPI tile, filter bar…)
  data/             ── @st.cache_data loaders; pages never do I/O directly
  db/               ── cached SQLAlchemy engine + reusable SQL
  utils/            ── palette tokens, formatters, a11y helpers
.streamlit/config.toml  ── theme (colorblind-safe palette, light + dark)
docker-compose.yml  ── Postgres 13 + PostGIS (imresamu/postgis:13-3.5) + pgweb browser UI on :8081
scripts/setup-db.sh ── idempotent: copy pgsql/ -> pgdata/ + patch Windows-era config
docs/data_schema.md ── reverse-engineered schema reference (read this before writing SQL)
```

The split is enforced by convention, not tooling:

- **Pages are dumb.** A page file imports from `src/` and composes
  widgets. No SQL, no `requests`, no heavy pandas pipelines in a page.
- **Data loaders are cached.** Anything in `src/data/` that touches
  disk/DB returns a tidy DataFrame and is wrapped in
  `@st.cache_data(ttl=...)`. This keeps reruns cheap (Streamlit
  re-executes the entire script on every interaction).
- **Components own their own state prefix.** When a component needs
  `st.session_state`, namespace keys (e.g. `filterbar_pollutant`) so
  pages don't collide.

### Navigation

`app.py` registers pages explicitly via `st.navigation([...])` with
`position="top"`. The pages directory is named **`app_pages/`, not
`pages/`**, on purpose — `pages/` would trigger Streamlit's legacy
auto-discovery and double-register every page.

To add a page: create `app_pages/<name>.py`, then append an
`st.Page(...)` entry to the `PAGES` list in `app.py`.

### Theming

All visual styling goes through `.streamlit/config.toml`. **Do not
use `st.markdown(..., unsafe_allow_html=True)` or `st.html()` with
`<style>` blocks** — it bypasses the design system and breaks dark
mode. If a color or radius needs to change, change it in the config.

The categorical palette in the config mirrors `OKABE_ITO` in
`src/utils/palette.py`; keep them in sync when editing.

## Data source

The dataset is a frozen **PostgreSQL 13 data directory** (PGDATA, not
a `pg_dump` file) shipped at `pgsql/` — about 1.8 GB, gitignored. It
was created on a Windows install years ago, so a few Windows-isms
need patching before a Linux container can boot it:

- `dynamic_shared_memory_type = windows` → `posix`
- `lc_*` = `'German_Germany.1252'` → `'C'`
- `pg_hba.conf` needs a wider trust rule (Docker bridges from a
  non-localhost IP)
- Database-level locale `German_Germany.1252` baked into every row of
  `pg_database`. `setup-db.sh` rewrites it to `C` via a one-shot
  single-user `UPDATE pg_database`, running inside a throw-away
  `postgres:13-alpine` container (musl libc is permissive about the
  legacy locale name and lets us open the DBs long enough to fix
  them). Once repaired, the main `imresamu/postgis:13-3.5` container
  (glibc) opens the databases normally and PostGIS works.

`scripts/setup-db.sh` handles all the above. It copies `pgsql/` into
`pgdata/` (gitignored, the container's actual storage) and applies the
patches. Run once after `git clone`; idempotent on re-runs.

**Always read [`docs/data_schema.md`](docs/data_schema.md) before
writing SQL** — the schema is non-obvious (per-MAC sensor tables, soft
references without FK constraints, three distinct sensor table shapes).

## Conventions

- **Imports from pages use absolute paths** from the repo root
  (`from src.utils.palette import OKABE_ITO`), never relative.
- **No `if __name__ == "__main__"` in Streamlit files** — Streamlit
  re-runs the whole module on every interaction; the guard is a noop
  at best and confusing at worst. Fine in `src/` helpers for ad-hoc
  testing.
- **Material icons** in titles/labels (`":material/dashboard:"`) for
  visual consistency. Requires Streamlit ≥ 1.53 (we use ≥ 1.53).
