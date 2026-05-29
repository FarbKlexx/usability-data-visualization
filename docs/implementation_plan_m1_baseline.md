# Implementation Plan — Milestone 1: Baseline Data Visualization

> **Scope of this document.** It defines *which* data from the
> `smartmonitoring_airquality` database is worth showing in a baseline dashboard,
> *how* (which chart type) to show it, *where* it sits on the dashboard, and *in
> what order* it gets built. **Styling/theming is deliberately out of scope** — it
> runs centrally through `.streamlit/config.toml` anyway. This is about data
> selection, visualization candidates, page architecture, and the data-access
> layer.
>
> Based on: `data_schema_full.md` (as of 2026-05-29), `CONTEXT.md` (usability
> theory), `CLAUDE.md` (architecture conventions).

### Locked decisions

- **Scope:** full set — Overview, Time Series, Map **+ Comparison + Devices/Data Quality** (all 5 pages are core).
- **DB copy:** mutable → **a `ts` index will be created** (performance path, see §6.4).
- **AQI:** derived category follows **EU CAQI**.
- **Still open:** external feeds (`ext_sensor_47589`, Polish) — see §8.

---

## 0. Guiding principle of the baseline

We follow Shneiderman's **visual-information-seeking mantra**: *overview first →
zoom & filter → details on demand*. That maps 1:1 onto the page structure
(Overview → Time Series → Map → drill-downs) and automatically respects
**Miller's 7±2**, because each level holds only a few modules.

The second guideline is **data honesty** (CONTEXT.md, ethics): the DB contains
saturation sentinels, duplicates, and swapped coordinates. These quirks are
handled *once, centrally* in the data layer — not re-invented in every
visualization — otherwise inconsistent representations emerge.

---

## 1. Data inventory — what is actually displayable?

### 1.1 Tables with real measurement data (= visualization sources)

| Table | Shape | Rows | Time range | Available measures | Geo? | Role in baseline |
| --- | --- | ---: | --- | --- | --- | --- |
| `sensor_000aeb8337ac` | A2 | 248,651 | 2025-07 → 11 | PM2.5, PM10, CO2, temp1, inn_temp/hum/pres | no (stationary) | **Primary** (workhorse) |
| `sensor_74da38543e94` | A1 | 171,078 | 2025-08 → 11 | same | no | **Primary** |
| `sensor_74da38543e8d` | A1 | 58,168 | 2025-10 → 11 | same | no | **Primary** |
| `sensor_801f02b31e0d` | A1 | 57,566 | 2025-10 | same | no | **Primary** |
| `sensor_b827eb1f5f13` | A1 | 1,761 | 2025-10 | PM2.5/10 + climate + GPS | **yes (track)** | Secondary (map) |
| `sensor_b827eb0fae5c` | A3 ⚠️ | 10,680 | **2023 → 2025** | PM2.5/10 + GPS | **yes (track)** | Secondary (with care, see 1.3) |
| `sensor_781c3ce6ad3c` | B | 424 | 2025-11 | mass_pm*, number_pm*, temp/hum/pres | **yes (point, swap!)** | Specialty (drill-down) |
| `sensor_pollish_external` | C | 68 | 2025-11/12 | PM1/2.5/10, **CAQI**, climate | fixed Gdańsk | Specialty (only CAQI source) |
| `ext_sensor_47589` | Ext | 54 | 2025-11 | PM2.5/10 (often NULL) | fixed Hannover | Optional (sparse) |

**Key takeaway:** the four stationary A-sensors carry ~96 % of all measurement
points and provide the most complete set of measures (including CO2). They are
the baseline. Everything else is a supplement.

### 1.2 Reference / metadata tables (no chart, but essential)

These provide the **device catalog** that feeds all selectors and the map:

- `tbl_observedobject` (40) — device/place registry, `mac`, `ootype_id`.
- `tbl_ootype` (3) — POI / stationary / mobile.
- `tbl_location` (19) + `tbl_location_join_oo` (19) — PostGIS coordinates of the
  stationary locations (for map markers).

### 1.3 Quirks that must be handled *before* display

| # | Problem | Consequence for the dashboard |
| --- | --- | --- |
| 1 | **Saturation sentinels**: `pm2_5` caps at 999.9, `pm10_0` at 1999.9; `temp1` up to 85 °C | Filter/flag centrally (otherwise distorted axes → dishonest). |
| 2 | **`sensor_b827eb0fae5c` (A3)**: duplicate rows, no `id` sequence, reordered columns | **Deduplicate** before display (by `ts`+values). Flag 2023 data if needed. |
| 3 | **`sensor_781c3ce6ad3c`**: lat/lon **swapped** | Swap axes when loading geo. |
| 4 | **PM unit**: registry says "ppm", actually µg/m³ | Label everywhere as **µg/m³**. |
| 5 | **No `ts` index** on any sensor table | Time-range queries = full scan → caching + server-side downsampling mandatory (see §6). |
| 6 | **`mNN` labels do not match** `tbl_observedobject` | Always join **via MAC**, never via label. |
| 7 | MAC casing (`...5f...`) | Normalize before comparison (lower, strip separators). |
| 8 | Stationary A-sensors: `pos`, `temp2/3` all NULL | Don't even offer these measures for stationary devices. |

### 1.4 Deliberately ignored (not air-quality content)

`datajobs*`, `schemes*`, `tbl_navigationroute`, `tbl_systemconfiguration`,
`tbl_card_join_oo`, `tbl_metatype`, `tbl_routes_planned`, and the **10 empty
`b827eb*` mobile devices** (m13–m20). These are app internals, scheduler
leftovers, or empty registrations — nothing to visualize.

---

## 2. Central metric registry (single source of truth)

A small data structure (e.g. `src/utils/metrics.py`) that defines each
displayable measure once. This enforces **consistency** (Shneiderman #1) and
**honest units/limits** project-wide:

| key | Label | Unit | Plausible range | Sentinel/fault | Source shapes |
| --- | --- | --- | --- | --- | --- |
| `pm2_5` | PM2.5 | µg/m³ | 0–500 | ≥ 999.9 | A, B (`mass_pm2_5`), C, Ext |
| `pm10_0` | PM10 | µg/m³ | 0–600 | ≥ 1999.9 | A, B (`mass_pm10`), C, Ext |
| `co2` | CO₂ | ppm | 350–5000 | — | A |
| `temp1` | Outdoor temperature | °C | −30–50 | ≥ 85 | A |
| `inn_temp` | Housing temperature | °C | −10–60 | ≥ 53 suspect | A |
| `inn_hum` | Humidity (housing) | % | 0–100 | — | A |
| `inn_pres` | Pressure | hPa | 950–1050 | — | A |
| `caqi` | CAQI (Common AQI) | index | 0–11 | — | C |
| `mass_pm*` / `number_pm*` | Particle size | µg/m³ resp. #/cm³ | — | — | B |

Each entry also carries its **palette role** (categorical = Okabe-Ito,
sequential = Viridis) and a formatting function. So all charts reference the same
label/unit text → no drift.

> **Derived measure (locked: EU CAQI):** an **AQI category** computed from the EU
> CAQI breakpoints (levels *very low → very high*), primarily from PM2.5/PM10.
> Gives the KPI tiles a label + shape in addition to color (see §3, color
> blindness). Must be marked as *computed* (honesty). The real `caqi` column
> (Polish feed only) serves as a plausibility check.

---

## 3. Visualization candidates (chart type ↔ data ↔ usability rationale)

Each candidate is tied to concrete theory from `CONTEXT.md` — that is the
course's grading criterion.

1. **KPI tiles (latest value)** — *Overview.*
   Each shows value + unit + measure label + trend arrow + AQI-category label.
   *Theory:* overview-first; top-left = most important info (mental models);
   trend communicated via **arrow shape + sign**, not color alone (8 %
   color-deficiency rule). Max ~5–6 tiles (Miller).

2. **Time-series line chart** — *PM2.5/PM10/CO2 over time.*
   *Theory:* time = X-axis left→right (mental model); **direct manipulation** via
   brush-zoom + click-legend to toggle series (instead of a separate filter
   panel); tooltip = value + unit + timestamp (split-attention: legend/values on
   the chart, not in a table beside it); **honest Y-axis** (no truncation; show a
   notice on zoom).

3. **Small multiples / faceted mini-charts** — *climate (temp/humidity/pressure).*
   *Theory:* do **not** force different units onto a dual axis (dual axes mislead
   → dark pattern). Each measure gets its own small panel, shared time axis.

4. **Map with markers + tracks** — *stationary locations + mobile GPS tracks.*
   *Theory:* spatial mental models; markers color-coded by AQI **plus**
   label/tooltip; pan/zoom = direct manipulation; click → details on demand.

5. **Comparison bar chart** — *sensors against each other (avg/current PM).*
   *Theory:* categorical Okabe-Ito palette, **value labels** on bars (color not
   the sole channel); easy direct comparison.

6. **Distribution: box plot / histogram** — *spread of PM values.*
   *Theory:* shows outliers/sentinels **honestly** instead of hiding them; good
   for surfacing the 999.9 ceiling.

7. **Hour×weekday heatmap** — *temporal pattern of pollution.* (stretch)
   *Theory:* Viridis sequential; makes daily/weekly cycles instantly readable.

8. **Particle-size distribution (bar)** — *hi-res sensor `781c3ce6ad3c`.* (drill-down)
   `mass_pm1_0…pm10` resp. `number_pm*` as grouped bars.

9. **Data-availability timeline (Gantt)** — *which sensor has data when.*
   *Theory:* honesty about gaps; belongs on the Devices/Status page.

> **Deliberately *not* in the baseline:** gauge/dial widgets (tend toward chart
> junk, poor value readability) and 3D effects (CONTEXT: extraneous load).

---

## 4. Page structure (pages)

Registration as described in `CLAUDE.md`: one file per page in `app_pages/`, an
entry in the `PAGES` list in `app.py`, `position="top"`, Material icons in the
title.

| # | Page | Icon | Purpose | Baseline priority |
| --- | --- | --- | --- | --- |
| 1 | **Overview** | `:material/dashboard:` | Overview-first: KPIs + 1 headline chart + mini map | **Core** |
| 2 | **Time Series** | `:material/timeline:` | Deep exploration of a sensor/measure selection | **Core** |
| 3 | **Map** | `:material/map:` | Spatial view: locations + mobile tracks | **Core** |
| 4 | **Comparison** | `:material/compare_arrows:` | Compare sensors/measures | **Core** |
| 5 | **Devices & Data Quality** | `:material/sensors:` | Catalog, coverage timeline, sentinel notices | **Core** |

**Locked:** all 5 pages belong to the baseline. Pages 4–5 share the loaders of
1–3, so they need no new data-layer code (only aggregation on top).

---

## 5. Detailed layout per page (where things sit)

### 5.1 Overview
- **Top (sweet spot, edge):** filter bar as a global toolbar — sensor selection +
  time-range preset (24 h / 7 d / 30 d). Active filters visible as "chips",
  **Reset reachable at all times** (Shneiderman #6/#8).
- **Row 1:** 5–6 KPI tiles (PM2.5, PM10, CO2, outdoor temp, humidity, + AQI category).
- **Row 2:** 1 headline time series (PM2.5 + PM10) for the selected range.
- **Row 3:** mini map of the locations (click → jumps to the Map page).
- Number of modules deliberately ≈ 4 logical blocks → Miller respected.

### 5.2 Time Series
- Selectors: sensor (1) + measures (multi) + time range.
- Large line chart with brush-zoom + click-legend.
- Below it, optional small multiples for climate measures (shared X-axis).
- Each axis labeled incl. unit; tooltip for every point; notice banner if
  sentinels were filtered ("n values ≥ measuring range hidden").

### 5.3 Map
- Layer toggle: "Stationary locations" (markers from `tbl_location`) / "Mobile
  tracks" (polylines from the `b827eb*` sensors, deduplicated).
- Markers color-coded by AQI **+ label**; click → popup with the latest values.
- `781c3ce6ad3c` only once the axis swap is handled in the loader.

### 5.4 Comparison
- Several sensors, one measure → grouped bars (avg over range) + optionally
  overlaid lines; below it a box plot of the distribution.

### 5.5 Devices & Data Quality
- Table of all 40 objects: name, type, location, MAC, table present?, rows,
  first/last `ts`. Availability timeline (Gantt). Makes empty devices and
  sentinel shares transparent.

---

## 6. Data-access layer (`src/db` + `src/data`)

Strictly per `CLAUDE.md`: pages do no I/O. Loaders are `@st.cache_data`, return
tidy DataFrames; engine lives in `src/db`.

### 6.1 Engine + security allowlist (`src/db/`)
- Cached SQLAlchemy engine.
- **Table allowlist**: since sensor data lives in `sensor_<mac>` tables, the
  table name is needed dynamically — it *cannot* be a bind parameter. Therefore:
  load the list of real, existing sensor tables once from `pg_class` and
  **validate** every requested name against it (prevents SQL injection + cleanly
  handles the 8 missing m13–m20).

### 6.2 Loaders (`src/data/`)
| Loader | Purpose | Key logic |
| --- | --- | --- |
| `load_devices()` | device catalog (drives all selectors) | Join `tbl_observedobject`×`tbl_ootype`×`tbl_location(_join_oo)`; normalize MAC→table name; flag whether the table exists + row count/coverage. |
| `load_latest(mac)` | latest reading per sensor (KPI tiles) | `ORDER BY ts DESC LIMIT 1`; sentinel filter. |
| `load_timeseries(mac, metrics, start, end, bucket)` | time series for charts | Allowlist check; sentinel filter; **server-side downsampling** via `date_trunc(bucket, ts) … avg(...)` (because of the missing index). |
| `load_locations()` | map markers | `ST_X/ST_Y(coordinates)` from `tbl_location`. |
| `load_tracks(mac)` | mobile GPS track | `ST_X/ST_Y(pos)` where `pos NOT NULL`; **deduplicated** (A3 artefact); axis swap for `781c3ce6ad3c` where needed. |

### 6.3 Central helpers (`src/utils/`)
- `clean.py` — sentinel/fault filter, based on the metric registry (§2).
- `metrics.py` — the registry itself.
- `aqi.py` — derived EU CAQI category (marked as "computed").

### 6.4 Performance: `ts` index (locked)
The schema notes "no usable `ts` index" → every time-range query would be a full
scan over up to 248k rows. Since the working copy is mutable, we add an
**idempotent migration script** (e.g. `scripts/add-ts-indexes.sh` or a Python
migration) that runs `CREATE INDEX IF NOT EXISTS ... ON sensor_<mac> (ts)` for
the 8 populated tables. This makes the Time Series and Comparison pages
noticeably more responsive (CONTEXT: feedback < 100 ms) and is reversible.
Downsampling + TTL cache still stay active as a second layer (large ranges
should never render all raw points).

---

## 7. Build order for milestone 1

1. **Foundation:** engine + table allowlist (`src/db`), metric registry + clean
   helpers (`src/utils`). Smoke-test via `scripts/check_db.py`.
2. **Catalog:** `load_devices()` → provides the data basis for all selectors.
3. **KPIs:** `load_latest()` → KPI-tile component → Overview page (scaffold).
4. **Time series:** `load_timeseries()` with sentinel filter + downsampling →
   headline chart on Overview.
5. **Time Series page:** interactive chart (brush-zoom, click-legend).
6. **Geo:** `load_locations()` + `load_tracks()` → Map page.
7. **Comparison + Devices pages** (same loaders, aggregation on top).

Each step is its own documentable prompt — matching your structured approach.

---

## 8. Remaining open decision

Three points are settled (full 5-page scope, `ts` index allowed, EU CAQI — see
"Locked decisions" above). Still open:

- **External feeds** (`ext_sensor_47589` = Hannover, `sensor_pollish_external` =
  Gdańsk): only 54 resp. 68 rows, partly NULL PM, redundant hourly values.
  *Recommendation:* include them in the **device catalog + map** (they are the
  only sources outside Minden and provide the real `caqi` reference), but **not**
  in the Overview KPI tiles/headline charts — they are too sparse there and would
  distort the sensor comparison. That keeps them visible without tipping the main
  conclusions.
