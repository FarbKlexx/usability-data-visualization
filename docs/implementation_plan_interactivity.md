# Implementation Plan — Interactivity Layer

> **Companion to** `implementation_plan_m1_baseline.md`. The baseline pages and
> data loaders exist. This document adds two strands of interactivity:
> **(A) UI interactivity** — the user shapes how the data is presented — and
> **(B) database interactivity** — the user writes changes back to the database.
> Scope here is *functional*: what gets built and how it wires into the existing
> `src/` layers. Styling and refinement come afterwards, based on what the agent
> produces.

---

## 0. Guiding idea

The existing loaders already return tidy DataFrames. UI interactivity is mostly
about feeding those loaders different parameters in response to user input and
re-rendering. Database interactivity is the new architectural piece: a small
**write layer** alongside the existing read layer, plus a few **new tables** for
user-generated content so the measurement data stays untouched.

---

## A. UI interactivity (user shapes the view)

### A1. Linked cross-filtering between charts and map
Selecting a region on one chart drives the others. Concretely:

- A brush/drag selection on the time-series chart sets a `(start, end)` window
  in `st.session_state`; the KPI tiles and any secondary charts re-read from
  `load_timeseries(...)` with that window.
- Clicking a marker on the map writes the chosen `mac` into session state and
  routes the user to the Time Series page pre-loaded with that sensor.

Implementation: a single `st.session_state` namespace (e.g. `xfilter_*`) that all
pages read; one helper `get_active_window()` / `set_active_window()` in
`src/utils/` so pages share the same state contract.

### A2. Adjustable aggregation and smoothing
The user picks how the series is condensed:

- **Aggregation bucket** selector (raw / minute / hour / day) → passed straight
  into the existing `bucket` parameter of `load_timeseries`.
- **Rolling-average window** slider (e.g. 0–60 samples) → applied client-side on
  the returned DataFrame via pandas `.rolling(...).mean()`, drawn as an overlay
  line on top of the raw series.

Both are pure read-path parameters; no new SQL beyond what already exists.

### A3. Raw / cleaned toggle
A switch that controls whether the central sentinel filter from `src/utils/clean.py`
is applied. When raw is selected, the loader returns unfiltered rows so the user
can inspect the saturation values directly. A small caption reports how many
points the filter would remove.

### A4. Interactive thresholds
The user sets a value (e.g. PM2.5 = 50) and the chart draws a horizontal
reference line; points above it are emphasized. Threshold values live in session
state for the UI-only version, and can later be persisted (see B5). This reuses
the metric registry (§2 of the baseline plan) for default values per measure.

### A5. Comparison builder
On the Comparison page, an "add sensor" control appends sensors to a working set
held in session state; each added sensor pulls its own `load_timeseries(...)` and
the results are concatenated for grouped bars / overlaid lines. Removing a sensor
drops it from the set and re-renders.

### A6. Data export of the current view
A download control that serializes whatever DataFrame is currently displayed
(post-filter, post-aggregation) to CSV via `df.to_csv(...)` and hands it to
`st.download_button`. This makes any view reproducible outside the app.

### A7. Saved views via URL query params
The active filter state (sensor, measures, window, bucket) is mirrored into
`st.query_params`. Loading a URL with those params restores the exact view. This
gives shareable/bookmarkable states with no database involvement, and becomes the
serialization format reused by the persisted version in B6.

---

## B. Database interactivity (user writes back)

### B0. Architecture: a write layer next to the read layer
Add `src/db/write.py` (or extend `src/db`) with:

- A **transactional `execute(stmt, params)`** helper using the existing cached
  engine, wrapped in `with engine.begin()` so each write is atomic.
- An **editable-target allowlist**: an explicit map of `{table: [editable
  columns]}`. Any write validates its table+columns against this map before
  touching the database, mirroring the read-side table allowlist already in
  place.
- **Cache invalidation**: after a successful write, call the relevant
  `st.cache_data.clear()` (or a scoped clear) so the read loaders pick up the
  change on the next rerun.

Writes fall into two groups: edits to a small set of existing metadata tables,
and inserts into new user-content tables.

### B1. Edit device metadata (`tbl_observedobject`)
Editable columns: `name`, `description`, `icon`, `datacapture`. A form on the
Devices page loads the current row, lets the user change these fields, and writes
an `UPDATE ... WHERE id = :id`. The 40-row table is small, so a full reload after
save is cheap.

### B2. Edit and add locations (`tbl_location` + `tbl_location_join_oo`)
The user edits address fields (`name`, `city`, `street`, `postcode`) and the
PostGIS point. Two entry paths:

- A form for the text fields → `UPDATE tbl_location`.
- A map interaction where dragging or clicking places a marker; the resulting
  lon/lat is written into `coordinates` via
  `ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)`.

Adding a location also inserts the matching `tbl_location_join_oo` row to bind it
to an object.

### B3. Feature toggles (`tbl_systemconfiguration`)
This table already holds key/value feature flags with an `active` boolean. A
small admin panel lists the `func_*` rows and lets the user flip `active`. The
app reads these flags on load to show/hide optional modules — turning the table
into a live configuration surface.

### B4. Annotations on time ranges (new table)
Add `smartmonitoring.dashboard_annotations`:

```
id          bigserial PK
mac         varchar          -- which sensor (normalized)
ts_from     timestamp
ts_to       timestamp        -- nullable for point annotations
label       varchar
note        text
created_at  timestamp default now()
```

The user selects a span on a time-series chart and saves a note; saved
annotations are loaded by `load_annotations(mac)` and drawn as shaded regions /
markers on the chart. Pure additive feature — measurement tables are never
written.

### B5. Reading flags (new table)
Add `smartmonitoring.dashboard_reading_flags`:

```
id          bigserial PK
table_name  varchar          -- validated against the read allowlist
reading_id  bigint           -- the id within that sensor table
flag        varchar          -- e.g. 'suspect', 'confirmed', 'ignore'
note        text
created_at  timestamp default now()
```

Lets the user mark individual points (for example the 999.9 sentinels) without
altering the source rows. A loader joins these flags back onto the displayed
series so flagged points can be styled or excluded on demand.

### B6. Persisted thresholds and saved views (new tables)
Promote A4 and A7 to the database so they survive sessions:

```
dashboard_thresholds(id PK, metric varchar, value float8, label varchar, created_at)
dashboard_saved_views(id PK, name varchar, params_json jsonb, created_at)
```

Thresholds load on chart render; saved views list as named entries the user can
apply (which sets the same query params from A7).

### B7. Migration for the new tables
Add an idempotent migration (e.g. `scripts/add-dashboard-tables.sh` or a Python
migration alongside the `ts`-index script from the baseline plan) that runs
`CREATE TABLE IF NOT EXISTS ...` for the four `dashboard_*` tables in the
`smartmonitoring` schema. Idempotent so re-runs after `git clone` are safe.

---

## C. New loaders and writers (summary)

| Function | Layer | Purpose |
| --- | --- | --- |
| `get_active_window()` / `set_active_window()` | `src/utils` | shared cross-filter state |
| `load_annotations(mac)` | `src/data` | read annotations for a sensor |
| `load_reading_flags(table, ids)` | `src/data` | read flags for displayed points |
| `load_thresholds()` / `load_saved_views()` | `src/data` | read persisted UI state |
| `execute(stmt, params)` | `src/db/write` | transactional write helper |
| `update_object(id, fields)` | `src/db/write` | edit `tbl_observedobject` |
| `update_location(id, fields, lon, lat)` | `src/db/write` | edit `tbl_location` |
| `set_feature_flag(ckey, active)` | `src/db/write` | toggle `tbl_systemconfiguration` |
| `add_annotation(...)` / `add_reading_flag(...)` | `src/db/write` | insert user content |
| `save_threshold(...)` / `save_view(...)` | `src/db/write` | persist UI state |

Each writer validates against the editable-target allowlist and clears the
relevant read cache on success.

---

## D. Build order

1. **Write foundation:** `src/db/write.py` (transactional `execute`, editable
   allowlist, cache invalidation). Smoke-test with one harmless `UPDATE` on
   `tbl_observedobject`.
2. **Metadata edits (B1, B2):** Devices page gets edit forms; Map page gets the
   coordinate-set interaction.
3. **New tables migration (B7):** create the four `dashboard_*` tables.
4. **Annotations (B4)** and **reading flags (B5):** loaders + writers + chart
   overlays.
5. **UI interactivity (A1–A6):** cross-filter state, aggregation/smoothing
   controls, raw/cleaned toggle, threshold lines, comparison builder, CSV export.
6. **Persistence (A7 → B6):** query-param views, then promote thresholds and
   saved views to the database.
7. **Feature toggles (B3):** admin panel driving optional modules.

Each step is a self-contained, documentable prompt, matching the structured
workflow used so far.
