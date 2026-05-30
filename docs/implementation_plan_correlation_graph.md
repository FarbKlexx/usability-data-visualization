# Implementation Plan — Interactive Multi-Measure & Correlation Graph

> **Companion to** `implementation_plan_m1_baseline.md` and
> `implementation_plan_interactivity.md`. Those are implemented and deployed.
> This is a small, focused addition: turn the main time-series graph into one
> where the user picks any combination of recorded measures, overlays them, and
> inspects whether they correlate (e.g. PM2.5 vs. temperature). Scope is
> functional; styling comes later.

---

## 0. Core idea

A Shape-A sensor stores every measure of a given moment in the **same row with
the same timestamp** (`temp1`, `pm2_5`, `pm10_0`, `co2`, `inn_temp`, `inn_hum`,
`inn_pres`). So comparing two measures of the same sensor needs no time
alignment — they are already paired per row. The feature is essentially: let the
user select 2+ measures from the metric registry, then render them in a way that
exposes their relationship.

The one thing to solve is that measures have very different units and ranges
(µg/m³, °C, ppm, hPa, %). Three rendering modes cover this, and the user chooses
between them.

---

## A. Measure selection

- A **multi-select** lists the measures available for the currently selected
  sensor. Availability is derived from the metric registry (§2 of the baseline
  plan) intersected with the columns that actually carry data for that sensor
  (stationary units expose `temp1`/PM/CO2/climate; mobile units expose PM + GPS).
- The selection drives a single `load_timeseries(mac, metrics, start, end,
  bucket)` call with the chosen metric list — the loader already accepts multiple
  metrics, so no new SQL is needed.
- The central sentinel cleaning stays applied (the 999.9 PM ceiling and the
  85 °C `temp1` faults would otherwise dominate any correlation). The existing
  raw/cleaned toggle remains available so the user can switch.

---

## B. Rendering modes

The user picks one of three modes for the selected measures.

### B1. Normalized overlay (shape comparison)
Each selected measure is scaled to a common 0–1 range (min–max per measure over
the visible window) and drawn as an overlaid line on a single axis. This makes
the *shapes* of the curves directly comparable — the user sees whether peaks and
troughs line up in time. A caption notes that values are normalized and gives the
real min/max per measure so the absolute scale is recoverable.

### B2. Dual-axis overlay (two measures, real units)
For exactly two measures, draw measure A on the left axis and measure B on the
right axis, each in its true unit. Both axes are labeled with their measure and
unit. This keeps real values readable while still letting the user eyeball
co-movement.

### B3. Scatter / correlation view (the relationship itself)
Plot measure A on X and measure B on Y, one point per aligned sample, optionally
colored by time (so trends within the period are visible). This is the mode that
actually shows correlation. On top of it:

- a fitted trend line (least-squares),
- the **Pearson r** and sample size **n**, computed via pandas `df[[a, b]].corr()`
  on rows where both values are present,
- optionally **Spearman ρ** for monotonic (non-linear) relationships.

If more than two measures are selected in this mode, render a **correlation
matrix heatmap** (Viridis, with the r values printed in each cell) instead of a
single scatter.

---

## C. Data alignment

- **Same sensor (primary case):** measures are already paired per row. Build the
  comparison frame by selecting the chosen columns from the loader result and
  dropping rows where any selected measure is NULL.
- **Across sensors (optional extension):** resample each sensor's series to a
  common bucket via the existing `bucket` parameter, then merge on the bucket
  timestamp. Reuse the comparison-builder set from
  `implementation_plan_interactivity.md` (A5) for choosing the sensors.

---

## D. Optional extensions

- **Lagged correlation:** a small offset control shifts measure B by *k* buckets
  before computing r, so the user can probe whether one measure leads another
  (e.g. temperature rise preceding a PM change). Implemented with pandas
  `.shift(k)`.
- **Window-scoped stats:** the r value recomputes whenever the brush window from
  the cross-filter state (A1 of the interactivity plan) changes, so correlation
  is always reported for exactly what is on screen.
- **Persist a comparison:** save the chosen measures + mode as a named entry via
  the existing `dashboard_saved_views` table (B6 of the interactivity plan).

---

## E. New / extended functions

| Function | Layer | Purpose |
| --- | --- | --- |
| `available_metrics(mac)` | `src/utils` | metrics in the registry that carry data for this sensor |
| `build_comparison_frame(df, metrics)` | `src/data` | select chosen columns, drop NULL rows, return aligned frame |
| `compute_correlation(frame, method)` | `src/utils` | Pearson/Spearman r + n; matrix when >2 metrics |
| `normalize_frame(frame)` | `src/utils` | per-measure min–max scaling for the overlay mode |

`compute_correlation` uses pandas for r; if p-values are wanted later, add
`scipy.stats.pearsonr` (`uv add scipy`).

---

## F. Build order

1. **Selection + loader wiring:** measure multi-select → `available_metrics(mac)`
   → `load_timeseries` with the chosen list → `build_comparison_frame`.
2. **Mode B1 (normalized overlay):** `normalize_frame` + overlaid lines.
3. **Mode B3 (scatter + Pearson r):** the primary correlation view, two measures.
4. **Correlation matrix:** heatmap path for 3+ measures.
5. **Mode B2 (dual-axis):** two-measure real-unit overlay.
6. **Optional (D):** lagged correlation, window-scoped recompute, persisted
   comparisons.

Each step is a self-contained prompt, matching the structured workflow used so
far.
