# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

An **Air Quality dashboard** built with Streamlit, delivered for a
university **Usability course**. The deliverable is judged on how
well the UI applies established usability theory — not just on whether
it ships features.

It has grown past the baseline read-only dashboard: there is now an
**interactivity layer** (cross-filter hand-offs, bookmarkable URL
state, adjustable aggregation, reference thresholds, CSV export) and a
**database write-back layer** (device/location edits, annotations,
reading flags, saved views, feature flags). It is also **deployable to
Streamlit Community Cloud** against a hosted Postgres+PostGIS instance
(see [Deployment](#deployment)).

The full theoretical brief lives in [CONTEXT.md](CONTEXT.md). Skim it
before designing any new view. Key constraints that should shape every
PR:

- **Miller's 7±2** — at most ~7 KPIs/widgets per view; group the rest into tabs/drill-downs.
- **Color is never the only channel** — pair with shape/label/position; the categorical palette is Okabe-Ito (see `src/utils/palette.py`), sequential is Viridis.
- **Direct manipulation** — prefer brush/zoom/click-legend over separate filter panels.
- **Shneiderman #3 (feedback) and #6 (reversal)** — every filter and every write shows confirmation; "Reset" must always be reachable, and every write must be deletable/revertible.
- **Honest data** — no truncated Y-axes without a notice; no chart junk; saturation sentinels are hidden *and disclosed* (counted, never silently dropped); derived quantities (CAQI) are labelled as computed.
- **44×44 px** minimum touch targets.

## Prompt logbook

Every user prompt in this project is recorded in
[`docs/prompt_logbook.md`](docs/prompt_logbook.md). **For each new
prompt the user gives, append a new entry** at the bottom of that file,
incrementing the heading number, with three parts:

- **Title** — a short `##`-level label summarizing the request.
- **Prompt** — the user's concrete prompt, verbatim, as a blockquote.
- **Summary of changes** — a bulleted list of what was actually done in
  response (files created/edited, behavior changed).

Do this as part of fulfilling the request, not as a separate step the
user has to ask for. If a prompt produces no code change (a question,
a clarification), still log it and note that in the summary.

## Commands

This project uses [uv](https://docs.astral.sh/uv/) for dependency
management. The lockfile (`uv.lock`) is the source of truth;
`requirements.txt` is a generated fallback for pip-only environments
**and the file Streamlit Community Cloud installs from** — regenerate
it after adding deps.

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

Migrations & deploy export (all idempotent unless noted):

```bash
# create the dashboard_* user-content tables + seed feature flags
uv run python scripts/add_dashboard_tables.py     # --dry-run to preview, --drop to reverse
# add ts btree indexes to populated sensor tables (faster time-range queries)
uv run python scripts/add_ts_indexes.py
# dump the smartmonitoring schema (data + PostGIS line) for a hosted DB
./scripts/export_for_deploy.sh                    # -> deploy/smartmonitoring.sql (gitignored)
```

The migration scripts honor `$DATABASE_URL`, so the same command
migrates a hosted DB:
`DATABASE_URL=… uv run python scripts/add_dashboard_tables.py`.

Tests split into **pure** (no DB; allowlist/registry/cleaning/CAQI
logic) and **DB-gated** (skip cleanly when Postgres is unreachable or
the `dashboard_*` tables aren't migrated). `uv run pytest` runs both.

Python is pinned to `>=3.12` in `pyproject.toml`. uv will provision a
compatible interpreter on first `uv sync` if none is available.

## Architecture

```
app.py              ── thin router: page_config + st.navigation + a cached DB-health guard
app_pages/*.py      ── one module per page; UI only (dashboard [hub], timeseries, map, devices, settings). comparison.py is no longer a top-level page — it exposes render_compare(), mounted in the Dashboard's Compare tab.
src/
  components/       ── reusable UI primitives
    charts.py       ──   plotly builders (line/small_multiples/grouped_bar/box/map/route_map/particle/coverage + correlation: normalized_overlay/scatter_correlation/correlation_heatmap)
    kpi.py          ──   metric_tile + aqi_tile
    filter_bar.py   ──   global sensor + time-range toolbar (returns a FilterState; group_by_type for the unified picker)
    skeleton.py     ──   content-shaped loading placeholders (hero/tiles/tiles_stack/block/lines); styled by the .aq-skel* CSS in app.py
  data/
    loaders.py      ──   @st.cache_data loaders; pages never do I/O directly (incl. load_routes + pure segment_routes for mobile trips)
  db/
    connection.py   ──   cached SQLAlchemy engine + URL resolution (secrets → env → local)
    queries.py      ──   read_sql + the sensor-table SQL-injection allowlist
    write.py        ──   transactional write-back API + EDITABLE_TARGETS column allowlist
  utils/
    palette.py      ──   Okabe-Ito + Viridis tokens
    metrics.py      ──   the metric registry (single source of truth: labels/units/ranges/sentinels)
    clean.py        ──   saturation-sentinel cleaning + disclosure strings
    aqi.py          ──   EU CAQI band classification (derived) + plain-language quality word/advice (hub status)
    correlate.py    ──   normalize_frame + Pearson/Spearman compute_correlation (scipy-free) + lay |r| correlation_verdict (hub)
    state.py        ──   cross-filter window + sensor hand-off + URL query-param sharing
    text.py         ──   escape_md (markdown-injection guard for user text)
    accessibility.py──   a11y helpers (placeholder)
.streamlit/config.toml          ── theme (colorblind-safe palette, light + dark)
.streamlit/secrets.toml.example ── DATABASE_URL template (copy to secrets.toml, gitignored)
docker-compose.yml              ── Postgres 13 + PostGIS (imresamu/postgis:13-3.5) + pgweb UI on :8081
scripts/setup-db.sh             ── idempotent: copy pgsql/ -> pgdata/ + patch Windows-era config
scripts/add_dashboard_tables.py ── idempotent migration for the dashboard_* tables + feature flags
scripts/export_for_deploy.sh    ── pg_dump the smartmonitoring schema for a hosted DB
docs/data_schema_full.md        ── AUTHORITATIVE reverse-engineered schema (verified against live DB)
docs/data_schema.md             ── legacy schema notes (superseded; kept for history)
DEPLOY.md                       ── step-by-step Community Cloud + Neon deployment guide
```

The split is enforced by convention, not tooling:

- **Pages are dumb.** A page file imports from `src/` and composes
  widgets. No SQL, no `requests`, no heavy pandas pipelines, no writes
  in a page — call a loader (`src/data`) or a writer (`src/db/write`).
- **Data loaders are cached.** Anything in `src/data/` that touches
  the DB returns a tidy DataFrame wrapped in `@st.cache_data(ttl=...)`.
  Frozen measurement data uses long TTLs (600–3600s); runtime-mutable
  user content (`dashboard_*`, feature flags) uses a short 60s TTL.
- **Components own their own state prefix.** When a component needs
  `st.session_state`, namespace keys: `filter_bar` uses
  `{prefix}_sensors` / `{prefix}_range`, and pages pass distinct
  prefixes (`ov` / `ts` / `cmp`) so instances don't collide.

### Pages

Registered explicitly in `app.py`; each is read-only unless noted.

| Page | Purpose | Write-back |
|------|---------|-----------|
| **Dashboard** *(adaptive cockpit)* | Fixed top-to-bottom hierarchy: **hero card** (the only `st.subheader`, *names the active device* + plain-language CAQI verdict + dominant-PM number) → **KPI strip** (the canonical 6-tile snapshot, lifted above the fold) → **`[2,1]` bento** (PM trend / route map *beside* a near-square location map / trip-stats card) → one divider → **tabs**: *Compare* (folded-in multi-sensor comparison), *Correlation* (verdict-first \|r\|), and *Routes* (mobile: split-gap + per-route PM). Operating hints are tooltips; only honesty disclosures stay as captions. | — |
| **Time Series** | Deep single-sensor exploration: aggregation bucket, rolling avg, raw/clean toggle, thresholds, CSV, bookmarkable URL state. The annotation / raw-inspector / particle-drilldown modules now render **always** (no longer feature-gated). | annotations, reading flags, saved views |
| **Map** | Locations + mobile tracks, layer toggles; details-on-demand = a single CAQI tile + "Open in Time Series" hand-off (the full KPI snapshot lives on the Dashboard, not duplicated here) | edit location (address + coords) |
| **Devices & Data Quality** | Device catalog, coverage timeline, honest data-quality audit (known-issue detail in expanders) | edit device metadata |
| **Settings** | Slim admin surface: persisted thresholds (used as Time Series reference lines) + a saved-views expander (apply/delete). *Feature-flag toggles removed — the optional modules are always on.* | thresholds, views |

Comparison is no longer a page: `app_pages/comparison.py` exposes
`render_compare()`, mounted in the Dashboard's **Compare** tab.

### Navigation

`app.py` registers pages explicitly via `st.navigation({...})` with
`position="sidebar"`; `set_page_config(initial_sidebar_state="collapsed")`
makes it a **left burger menu** (collapsed by default, opened via the `»`
control). `PAGES` is a **dict of two labelled sections** — *Monitor &
Analyse* (Dashboard, Time Series, Map) and *Reference & Settings* (Devices
& Data Quality, Settings) — so the menu reads as two sense-clusters rather
than a flat list (Hick/Miller at the menu level).
The pages directory is named **`app_pages/`, not `pages/`**, on purpose —
`pages/` would trigger Streamlit's legacy auto-discovery and
double-register every page.

To add a page: create `app_pages/<name>.py`, then add an `st.Page(...)`
entry to the relevant section list in the `PAGES` dict in `app.py`.

`app.py` also runs a cached `check_connection()` health check before
`page.run()`; if the DB is unreachable it shows a friendly "can't
reach its database" message (raw error in an expander) and
`st.stop()`s, instead of letting every page throw a traceback.

### Theming

All visual styling goes through `.streamlit/config.toml`. **Do not
use `st.markdown(..., unsafe_allow_html=True)` or `st.html()` with
`<style>` blocks** — it bypasses the design system and breaks dark
mode. If a color or radius needs to change, change it in the config.

**The documented exceptions:** a small `st.html(<style>)` in `app.py`
plus one tiny JS scroll-watcher (`components.html` in `dashboard.py`),
for chrome behaviours Streamlit gives no config hook for, all verified
theme-safe in light **and** dark:

1. swaps the sidebar burger glyph (`»` expand control → Material Symbols
   `menu` ☰) — only the glyph changes (`::after` inherits the icon font +
   current colour);
2. makes the **Dashboard** filter bar (`.st-key-ov_bar`, via the
   `key="ov_bar"` hook) **sticky on scroll**, where it condenses and
   **full-bleeds across the main content column**, reverting to the
   contained card when scrolled back up.
   - Sticky is set on the bar's `stLayoutWrapper` (`:has()`), since the
     bar's own wrapper is too short to stick; `top: 3.5rem` clears
     Streamlit's 56px fixed header.
   - The morph is a **`.ov-stuck` class + CSS transition**, NOT a
     scroll-driven animation: `animation-timeline: scroll()` is
     Chromium-only, and there it degraded to "always morphed" in
     Safari/Firefox. A 0-height same-origin `components.html` iframe runs
     a watcher that toggles `.ov-stuck` when the bar reaches the top, so
     the morph works in every browser.
   - `.ov-stuck` (CSS) only does the non-geometry morph (padding,
     `border-radius:0`, shadow) + `light-dark()` background (no theme var
     exists). The full-bleed **geometry** is set inline by the watcher
     from `stMain`'s `clientWidth`/left (not `vw`), so it spans the main
     column and **not an open sidebar**; `max-width` is overridden inline
     too (Streamlit clamps these blocks to `max-width:100%`). A
     `MutationObserver` re-binds across reruns and a `ResizeObserver` on
     `stMain` re-syncs when the sidebar opens/closes or the window resizes.
3. **Skeleton loaders** (`.aq-skel*` in `app.py`, markup from
   `src/components/skeleton.py`): content-shaped grey placeholders shown
   while a data load is in flight. Streamlit ships no `st.skeleton` widget
   and the config exposes no token, so the markup is emitted as class'd
   divs and styled here — a shimmer keyframe over a flat `light-dark()`
   fill, with a `prefers-reduced-motion` guard. Pages reserve an
   `st.empty()` slot, fill it with a skeleton, run the (cached) loader, then
   swap the real content into the same slot; on a cache hit the swap is
   instant, so a skeleton only shows during a genuine fetch. The shapes
   mirror the real widgets (tile-shaped for a tile, chart-shaped for a
   chart) so the layout never jumps. Currently wired across the **Dashboard**
   (hero, KPI strip, bento, Correlation tab) and its **Compare** tab.

All degrade gracefully (no JS → contained sticky bar, never broken;
no skeleton CSS → a plain empty slot, never broken).
**Don't grow this into general CSS/JS styling** — anything theme-able
still belongs in the config; these hooks are only for chrome the
framework doesn't expose.

The categorical palette in the config mirrors `OKABE_ITO` in
`src/utils/palette.py`; keep them in sync when editing.

### Data-access layer (read)

- `src/db/connection.py` builds one cached SQLAlchemy engine. The URL
  resolves **secrets → env → local default** (see [Deployment](#deployment)).
- `src/db/queries.py` exposes `read_sql(sql, params)` (tidy DataFrame,
  `:name` bind parameters) and the **sensor-table allowlist**
  (`sensor_table_allowlist` / `is_sensor_table` / `safe_sensor_table`).
- `src/data/loaders.py` is the only place pages get data. Notable:
  `load_timeseries(..., clean=True)` (sentinels removed *before*
  aggregation; pass `clean=False` for raw inspection),
  `load_devices()` (joined catalog + per-table coverage),
  `load_comparison()`, `load_latest()`, `load_routes()` (mobile GPS track
  → time-gap-segmented trips with PM, via the pure `segment_routes`),
  plus the dashboard loaders
  (`load_annotations`, `load_reading_flags`, `load_thresholds`,
  `load_saved_views`, `load_feature_flags`, `feature_enabled`,
  `dashboard_tables_ready`).

### Metric registry, cleaning, CAQI

These three modules enforce consistency and honesty everywhere:

- **`src/utils/metrics.py`** — the single source of truth. A `Metric`
  record carries `key`, labels, corrected `unit` (PM is µg/m³, **not**
  ppm), plausible `vmin`/`vmax`, the saturation `sentinel`, a stable
  Okabe-Ito `color`, icon, decimals, group, and per-shape
  `source_columns`. Charts/KPIs/tooltips pull from here — never
  hard-code a label, unit, or color. `HEADLINE_KPIS` is the ≈7 KPI row.
- **`src/utils/clean.py`** — replaces device saturation ceilings
  (PM2.5 ≥ 999.9, PM10 ≥ 1999.9, temp1 ≥ 85) with NaN and **counts**
  what it hid so the UI can disclose it (`hidden_notice`). Nothing is
  dropped silently.
- **`src/utils/aqi.py`** — EU CAQI band (CiteAir hourly grid, worse of
  PM2.5/PM10). A `CAQIBand` is triple-encoded (icon + text + color) and
  flagged as a *computed* quantity.

### Interactivity & write-back

The plan is in
[docs/implementation_plan_interactivity.md](docs/implementation_plan_interactivity.md);
strands **A** (UI interactivity) and **B** (database write-back).

- **Cross-page state** (`src/utils/state.py`): `hand_off_to_timeseries`
  (map → time series), `set/get/clear_active_window`, and
  `seed_session_defaults` / `publish_query_params` for **bookmarkable
  URL state** (Time Series mirrors sensor/range/measures/bucket into
  `st.query_params`).
- **Writes go through `src/db/write.py`** — every write is
  transactional (`engine.begin()`), validated against an allowlist,
  and clears the affected `@st.cache_data` loaders on success.
  - `EDITABLE_TARGETS` is an explicit `{table: {columns}}` allowlist —
    only `tbl_observedobject` (name/description/icon/datacapture),
    `tbl_location` (name/city/street/postcode), and
    `tbl_systemconfiguration` (active) are writable. Measurement tables
    are never editable. Location coordinates go through a dedicated
    `ST_SetSRID(ST_MakePoint(...), 4326)` path, not the column allowlist.
  - User content lives in four `dashboard_*` tables (below):
    `add_annotation`/`delete_annotation`, `add_reading_flag`/
    `delete_reading_flag` (flag ∈ `READING_FLAGS` =
    {suspect, confirmed, ignore}), `save_threshold`/`delete_threshold`,
    `save_view`/`delete_view`. Functions that name a sensor table
    validate it through `is_sensor_table` first.
- **Feature flags** are rows in `tbl_systemconfiguration` with
  `ckey LIKE 'func\_%'`. The toggle UI was **removed** in the IA
  consolidation: the three optional Time Series modules
  (`func_dashboard_annotations`, `func_dashboard_raw_inspector`,
  `func_dashboard_particle_drilldown`) now render **unconditionally**
  (gated only by `dashboard_tables_ready()` / sensor shape), so a lay
  user faces no on/off decision. The `set_feature_flag` /
  `feature_enabled` / `load_feature_flags` helpers still exist in
  `src/` for programmatic use, but no page calls them.

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

**Always read [`docs/data_schema_full.md`](docs/data_schema_full.md)
before writing SQL** — it is the authoritative, live-verified schema
reference (`data_schema.md` is the superseded earlier draft). The
schema is non-obvious:

- **Per-MAC sensor tables in four shapes.** Measurements live one
  table per device (`sensor_<mac>` / `ext_sensor_<mac>`):
  **Shape A** SENSORpi air-quality (16 tables, 3 physical variants),
  **Shape B** hi-res particle sensor (`sensor_781c3ce6ad3c`,
  axis-swapped coords), **Shape C** Polish external feed
  (`sensor_pollish_external`, non-PostGIS lat/lon), **Shape Ext**
  sensor.community import (`ext_sensor_47589`). `load_devices` /
  `shape_of` abstract this; never assume a uniform column set.
- **Soft references, no FK constraints** — join on **MAC**, never on
  human labels (the `m12`/`m13` label-vs-comment mismatch is real).
- **8 registered mobile devices have no table** (`m13`–`m20`); the
  allowlist cleanly rejects them.
- **Saturation sentinels** (PM ceilings) are device limits, not
  readings — `src/utils/clean.py` hides and counts them.

The user-content layer adds four tables in the `smartmonitoring`
schema (created by `scripts/add_dashboard_tables.py`):
`dashboard_annotations`, `dashboard_reading_flags` (with a
`flag IN ('suspect','confirmed','ignore')` CHECK), `dashboard_thresholds`,
and `dashboard_saved_views` (params as JSONB). They use implicit
(allowlist-validated) references, not FKs, consistent with the rest of
the schema.

## Deployment

Streamlit Community Cloud runs on Streamlit's servers and **cannot
reach your laptop's Docker container** — so a working deploy needs a
**hosted Postgres + PostGIS** instance. [DEPLOY.md](DEPLOY.md) has the
full walkthrough (Neon free tier). The shape:

1. Create a hosted DB, enable PostGIS, grab its connection string.
2. `./scripts/export_for_deploy.sh` → `deploy/smartmonitoring.sql`,
   then `psql "$DATABASE_URL" -f deploy/smartmonitoring.sql` to load it.
3. Point the app at it with a `DATABASE_URL` **secret** and (re)deploy.

`src/db/connection.py` resolves the URL **secrets → env → local
default**: `st.secrets["DATABASE_URL"]` → `$DATABASE_URL` →
`postgresql+psycopg://…@localhost:5432/…`. A bare `postgresql://` (or
`postgres://`) URL is accepted — the scheme is rewritten to
`postgresql+psycopg://` so SQLAlchemy uses psycopg 3. Prepared-
statement caching is disabled (`prepare_threshold=None`) so a
**pgbouncer transaction-pooled** endpoint (e.g. Neon's `-pooler` host)
works. Community Cloud runners are IPv4-only — prefer the **pooled**
endpoint there.

To test a hosted DB locally, copy `.streamlit/secrets.toml.example` to
`.streamlit/secrets.toml` (gitignored) with the same `DATABASE_URL`.
Community Cloud auto-redeploys on push to the deployed branch; only
**secret changes** require a manual reboot. Write-back features are
live on a public deploy (the in-context edit forms on Map/Devices and
the **Settings** thresholds/views). **Never commit a real connection
string**; rotate
the DB password if one leaks.

## Conventions

- **Imports from pages use absolute paths** from the repo root
  (`from src.utils.palette import OKABE_ITO`), never relative.
- **No `if __name__ == "__main__"` in Streamlit files** — Streamlit
  re-runs the whole module on every interaction; the guard is a noop
  at best and confusing at worst. Fine in `src/` helpers and `scripts/`.
- **Material icons** in titles/labels (`":material/dashboard:"`) for
  visual consistency. Requires Streamlit ≥ 1.53 (we use ≥ 1.53).
- **SQL safety is non-negotiable.** Table/column names are interpolated
  *only* after validation against an allowlist (`safe_sensor_table`,
  `EDITABLE_TARGETS`); every user value travels as a `:name` bind
  parameter. Never f-string a user value into SQL.
- **Escape user text before `st.markdown`.** Annotation labels, view
  names, threshold labels etc. pass through `escape_md` so user input
  can't inject markdown.
- **Pages do no I/O and no writes directly** — go through `src/data`
  (read) or `src/db/write` (write); writers clear the relevant caches.
