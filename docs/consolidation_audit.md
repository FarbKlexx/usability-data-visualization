# Stage 1 — Audit & Consolidation Proposal

> Deliverable for **`implementation_plan_consolidation.md` Stage 1 (§A)**.
> This document **only proposes** — no page was edited or deleted. Removal
> and restructuring happen in Stage 2, on the subset you approve.
> Open questions for you are collected in **§7**.

---

## 0. The rubric (re-read of `CONTEXT.md`)

The concrete criteria each page is judged against below — the lens, not a
final glance:

| # | Criterion (source) | Concrete test applied per page |
|---|--------------------|--------------------------------|
| R1 | **Miller 7±2** | ≤ ~7 glanceable modules per view; the rest in tabs/expanders/drill-down |
| R2 | **Grouping / split-attention** | related things spatially together; legends/units on the chart, not in a side table |
| R3 | **Placement / mental models** | most important top-left; time on the X-axis; lead with the answer |
| R4 | **Color never alone** | every colour paired with label/shape/position (≈8% CVD) |
| R5 | **Match the real world / plain language** | a non-expert understands *what* and *so-what* before reading an axis |
| R6 | **Feedback & closure (Shneiderman #3/#4)** | every filter/write visibly takes effect |
| R7 | **Reversal & reset reachable (#6, ethics)** | Reset/undo always present; no "roach motel" |
| R8 | **Honest data (ethics)** | no truncated axes w/o notice; sentinels disclosed; derived values labelled |
| R9 | **Hick's law / progressive disclosure** | few options per level; reveal detail on demand |
| R10 | **Fitts / 44×44, responsive** | large targets, edge toolbars, works narrow |
| R11 | **Consistency (#1)** | same component library, terms, icons everywhere |

---

## 1. Page inventory (features × loaders)

Seven pages today (`app.py` `PAGES`): Overview · Time Series · Map ·
Comparison · Correlation · Devices & Data Quality · Manage.

### Overview — `app_pages/overview.py` *(default landing page)*
| Module | Widget(s) | Data loader / source |
|--------|-----------|----------------------|
| Global filter | `filter_bar` (single sensor, range, Reset) — pool = **stationary Shape-A only** | `load_devices` |
| KPI row | 5 `metric_tile` + 1 `aqi_tile` | `load_latest(table)` |
| Headline trend | `line_chart` PM2.5 + PM10 | `load_timeseries` |
| Mini map | `map_figure` (no labels) + `page_link` → Map | `load_locations` |

**~4 modules.** Single sensor only. No plain-language status; no correlation.

### Time Series — `app_pages/timeseries.py`
| Module | Widget(s) | Loader |
|--------|-----------|--------|
| Filter | `filter_bar` (single) | `load_devices` |
| Measures | `multiselect` | `available_metrics` |
| Display controls | bucket select · rolling-avg slider · raw toggle | — |
| Charts | one `line_chart` per unit group | `load_timeseries` |
| Thresholds | expander, per-measure line | `load_thresholds` |
| Export / save | CSV download · "Save view" popover | `save_view` |
| Annotations *(flagged)* | expander, shaded bands | `load_annotations` / `add/delete_annotation` |
| Raw inspector + flags *(flagged)* | expander, dataframe + flag form | `load_raw_readings` / `load_reading_flags` |
| Particle drill-down *(flagged, Shape-B)* | bars | `load_particle_sizes` |
| URL state | `publish_query_params` | — |

Many modules, but the optional three are **feature-gated + in expanders**
(R9 satisfied). The deepest, most "expert" surface — appropriately so.

### Map — `app_pages/map.py`
| Module | Widget(s) | Loader |
|--------|-----------|--------|
| Layers | `pills` (stationary / mobile) | — |
| Map | `map_figure` markers (CAQI-banded) + tracks | `load_locations`, `load_latest` **(looped per located sensor)**, `load_tracks` |
| Details on demand | `selectbox` + **KPI row (5 `metric_tile` + `aqi_tile`)** + "Explore in Time Series" | `load_latest(chosen)` |
| Edit location | fields + live preview map → save | `update_location` (write) |

### Comparison — `app_pages/comparison.py`
| Module | Widget(s) | Loader |
|--------|-----------|--------|
| Filter | `filter_bar` (**multi** sensor) | `load_devices` |
| Measure | `selectbox` (only measures common to all selected) | `available_metrics` |
| Charts | tabs: grouped-bar averages / box-plot distribution | `load_comparison` |
| Numbers | CSV download + "Show the numbers" expander | — |

Clean, focused, honest (hidden disclosed, box plots). **~4 modules.**

### Correlation — `app_pages/correlation.py` *(added in the previous task)*
| Module | Widget(s) | Loader |
|--------|-----------|--------|
| Filter | `filter_bar` (single) | `load_devices` |
| Measures | `multiselect` (≥2) | `available_metrics` |
| Controls | bucket · method (Pearson/Spearman) · raw toggle | — |
| View mode | `segmented_control` (Scatter/Normalized/Dual, or Matrix/Normalized for 3+) | — |
| Chart | scatter / overlay / dual-axis / matrix heatmap | `load_timeseries` → `build_comparison_frame` |
| Stats | `r` + `n` + worded relationship; lag slider (scatter) | `compute_correlation` |
| URL state | `publish_query_params` | — |

**Chart/mode-first**, with the coefficient *below* the chart — the
plan (B3) wants this **inverted to verdict-first**.

### Devices & Data Quality — `app_pages/devices.py`
| Module | Widget(s) | Loader |
|--------|-----------|--------|
| Summary | 4 `metric` tiles | `load_devices` |
| Coverage | `coverage_timeline` Gantt | `load_devices` |
| Catalog | `dataframe` | `load_devices` |
| Quality audit | sentinel-count table + prose | `load_comparison` **×2 over 2023→2026, all stationary tables** |
| Edit metadata | form → save | `update_object` (write) |

**5 modules**, and the audit runs two wide-range aggregations on every
load (spinner present, but heavy).

### Manage — `app_pages/manage.py`
| Module | Widget(s) | Loader |
|--------|-----------|--------|
| Feature flags | toggles (dashboard + "other" expander) | `load_feature_flags` / `set_feature_flag` |
| Thresholds | list + add form | `load_thresholds` / `save_threshold` |
| Saved views | list, **Apply (→ Time Series only)** / Delete | `load_saved_views` / `delete_view` |

---

## 2. Per-page audit against `CONTEXT.md`

| Page | Strong | Concrete deviations |
|------|--------|---------------------|
| **Overview** | R7 (Reset), R8 (hidden notice), R1 (~4 modules) | **R5**: leads with numeric tiles, no worded "air quality is good" sentence. **R3**: the air-quality *verdict* (CAQI tile) sits **bottom-right of the KPI row**, not top-left where the headline answer belongs. **Hub gap**: single sensor; no correlation; doesn't pull up subpage signals — it's "an Overview among equals," exactly what the plan targets. |
| **Time Series** | R9 (expanders + flags), R6/R7, R8, R2 (units on chart) | R1: a lot on one page, but mitigated by disclosure. Minor R3: thresholds/annotations live below the fold (acceptable). |
| **Map** | R4 (CAQI colour + legend + label), R6, direct manipulation | **Efficiency**: `load_latest` looped over every located sensor each run (cached, but N queries). **Duplication**: the details-on-demand KPI row is the **same tiles/loader as Overview** (R11 consistency, but redundant). R7: no explicit Reset for the layer pills (default both-on is the de-facto reset). Mixed concern: a write surface (edit location) on an exploration page. |
| **Comparison** | R2, R7, R8, R1 (~4), honest box plots | Minor R4: grouped bars are single-hue — fine (one measure, value labels present). Solid overall. |
| **Correlation** | R4, R7, R8 (dual-axis caveat shown), direct manipulation | **R3/R5**: coefficient + words appear **after** the chart; a lay reader meets the scatter before the verdict. Plan B3 wants verdict-first. **R5**: 5-band wording (`negligible…very strong`) is finer than the lay 3-band scheme the plan asks for. |
| **Devices** | R8 (the honesty showcase), R6 | R1: 5 modules + a write form (borderline). **Efficiency**: 2× wide-range `load_comparison` on every load. Mixed concern: reference catalog + write surface together. |
| **Manage** | R6, R7, R11, R9 ("other flags" in expander) | Saved views **Apply only to Time Series** (so a correlation view couldn't round-trip — see §4). Otherwise sound for an admin surface. |

---

## 3. Feature classification

**Core** (the app's main purpose — "what's the air quality, and why?"):
- Plain-language air-quality status + CAQI band (`aqi.py`, `aqi_tile`)
- Latest KPIs (`load_latest`, `metric_tile`)
- Headline PM trend (`load_timeseries`, `line_chart`)
- Correlation **verdict** (does PM track temperature, etc.)
- Time Series deep-dive; Map spatial view

**Supporting** (useful, secondary):
- Comparison (one measure × many sensors)
- Correlation detail modes (normalized overlay, dual-axis, matrix), lag
- Devices catalog + coverage timeline + quality audit
- Write surfaces: edit location, edit device metadata, annotations, flags, thresholds, saved views, feature flags
- Particle-size drill-down (Shape-B only)

**Redundant / low-value as currently placed:**
- **Map's details-on-demand KPI row** — duplicates the Overview KPI row (same component + `load_latest`). Value is the *spatial context*, not the tiles.
- **Overview mini-map** — a teaser of the Map page; acceptable *as a link*, but it is a second map instance to maintain.
- **Standalone Correlation page** — per plan B3 the correlation feature is meant to live **on the dashboard, verdict-first**, "instead of a standalone page" (see §5 / §7-A).

---

## 4. Duplication & sprawl map

1. **KPI snapshot rendered twice** — Overview KPI row ≈ Map details-on-demand row (identical tiles + `load_latest`). *The hub should own the canonical KPI snapshot.*
2. **Two map instances** — full Map page + Overview mini-map. Fine as a teaser→link, but it is duplicated rendering config.
3. **"Multi-X analysis" siblings** — Comparison (one measure × many **sensors**) and Correlation (many **measures** × one sensor) are *orthogonal*, not redundant; both earn their keep, but the hub should make the distinction obvious and link to each.
4. **Three scattered write surfaces** — edit-location (Map), edit-metadata (Devices), config (Manage). Editing *in context* is defensible (R3 — edit where you see it); noted, **not** proposed for change under "keep the subpages."
5. **Saved views are Time-Series-shaped** — `params_json` carries `table/measures/range/bucket`; Manage's *Apply* hard-routes to Time Series. A correlation/comparison view can't round-trip today. *Constrains how "save this view" can work on the hub.*
6. **Single-feature page** — Correlation exists to host one feature; the plan wants that feature on the hub.

---

## 5. Proposed target structure (dashboard as hub on top)

Moderate consolidation: **subpages stay**; the dashboard is rebuilt as the
hub that answers the core question first and pulls up the key signals.

### The hub (rebuilt `overview.py`, landing page) — ≤ ~7 modules (R1)
1. **Plain-language status (B1)** — *top, leads* (R3/R5). Per active sensor: a sentence + CAQI band ("**Air quality: Good** · CAQI Low — PM levels are well within the healthy range"), from `aqi.py`. The worded verdict, not a tile, is the first thing seen.
2. **Latest KPIs (B2)** — the canonical KPI row (`metric_tile` × headline + `aqi_tile`), with **"Open in Time Series →"** linking through. This becomes the *one* KPI snapshot (Map stops re-rendering it — see §7-C).
3. **Headline trend (B2)** — PM2.5/PM10 line (already here) + **"Open in Time Series →"** link (currently missing).
4. **Correlation, verdict-first (B3/B4)** — measure multiselect → **colour-coded |r| verdict per pair** (word **and** colour **and** sign, R4) → supporting chart underneath, **replace-in-place** in one slot (B4). Reuses `compute_correlation` / `build_comparison_frame` / the chart builders.
5. **Mini-map** — kept as the spatial teaser → "Open full map →".

Status · KPIs · trend · correlation · mini-map = **5 modules** (R1 ✓).

### Subpages — kept, lightly adjusted
- **Time Series** — unchanged (the deep-dive / "expand" target for KPIs + trend).
- **Map** — keep spatial view + edit-location; **drop the redundant KPI tile row** from details-on-demand, keeping the selector + "Explore in Time Series" hand-off (or keep tiles if you prefer — §7-C). Map's job is *where*, not *what's the number*.
- **Comparison** — unchanged.
- **Devices & Data Quality** — unchanged structurally (optionally narrow the audit's date window for load time — §7 note).
- **Manage** — unchanged.

### The one removal up for approval
- **Correlation page** → folded into the hub (B3, build-order step 5). See **§7-A** for the two ways to do this and the trade-off.

---

## 6. Trade-offs for each proposed removal/merge

| Change | What's lost | Why acceptable |
|--------|-------------|----------------|
| **Fold Correlation into the hub, remove the page** (Option A1) | A dedicated URL and a roomy canvas for the 3 render modes + lag | Plan B3's explicit intent; replace-in-place keeps every mode reachable on the hub; net page count returns to pre-correlation (6). *Mitigation:* keep all modes inline, or keep a slim page (Option A2). |
| **Drop Map's KPI tile row** | At-a-glance numbers without leaving Map | The hub owns the canonical KPI snapshot (§4-1); Map keeps the selector + hand-off, so the number is one click away and the duplication/`load_latest` loop shrinks. |
| **Reframe Overview → hub** | The familiar "Overview" name | The page becomes genuinely more capable (status + correlation + links); naming is §7-D. |
| **(Optional) narrow Devices audit window** | Sentinel counts over the full 2023→2026 history | Counts over the active data window are representative and the page loads faster; full history still derivable. *Only if you want it.* |

Nothing else is removed: Comparison, Time Series, Devices, Manage, and all
write surfaces stay (R: "keep the subpages").

---

## 7. Decisions for you (gate to Stage 2)

The plan keeps deletion/restructuring with you. Please pick:

- **A. Correlation page**
  - **A1 (plan-literal, recommended):** fold the full feature into the hub (verdict-first, replace-in-place) and **remove** the standalone page.
  - **A2 (most conservative):** keep a **slim** Correlation page for power users (all modes + lag + CSV) **and** add the verdict-first summary on the hub, linking through.
  - **A3:** leave the Correlation page exactly as-is; hub gets only a small correlation teaser.

- **B. |r| strength cut-offs for the lay verdict (B3)**
  - **B1 (plan default):** *no/weak* `|r| < 0.3` · *moderate* `0.3–0.7` · *strong* `> 0.7`, with sign for direction.
  - **B2:** keep the existing finer 5-band wording (`negligible / weak / moderate / strong / very strong`).
  - (Custom cut-offs welcome.)

- **C. Map's details-on-demand KPI tile row**
  - **C1:** drop the tiles (hub owns the KPI snapshot); keep selector + "Explore in Time Series".
  - **C2:** keep the tiles on Map (accept the duplication for spatial convenience).

- **D. Hub naming** — rename **Overview → "Dashboard"** (signals "this is the hub") **or** keep **"Overview"**.

Once you approve a subset, Stage 2 proceeds in the plan's build order:
hub status (B1) → pull-up values (B2) → correlation inline (B3/B4) →
apply approved removals (update `app.py` `PAGES`) → a plain-language pass (§C).

---

## 8. Stage 2 — applied (your approved subset)

**Decisions:** A1 (fold correlation into the hub, remove the page) ·
B1 (lay bands 0.3 / 0.7 + sign) · C2 (Map KPI tiles kept as-is) ·
rename **Overview → "Dashboard"**.

**Changes made:**

- **`aqi.py`** — each `CAQIBand` now carries a plain-language `quality`
  word (Good / Fair / Moderate / Poor / Very poor) + a one-line `advice`
  sentence, for the hub's worded status (B1).
- **`correlate.py`** — `interpret_r` (finer 5-band) **replaced** by
  `correlation_verdict` → 3-band lay reading (no/weak `<0.3` · moderate
  `0.3–0.7` · strong `>0.7`) with signed arrow + neutral grey→blue→violet
  badge (colour never alone).
- **`charts.py`** — `dual_axis_lines` **removed** (not in the hub spec;
  the dual-axis pattern is the one CONTEXT flags as deceptive).
  `normalized_overlay` / `scatter_correlation` / `correlation_heatmap`
  kept (the hub uses them).
- **`app_pages/dashboard.py`** *(new, replaces `overview.py`)* — the hub:
  B1 status band → B2 KPIs + trend with an "Open this sensor in Time
  Series" hand-off → B3/B4 verdict-first correlation (per-pair verdict
  lines, then one replace-in-place slot: scatter/overlay for two
  measures, matrix for 3+) → mini map. Bookmarkable via query params.
- **`app_pages/overview.py`** and **`app_pages/correlation.py`** —
  **deleted**. `app.py` `PAGES` now: Dashboard (default) · Time Series ·
  Map · Comparison · Devices · Manage (**6 pages**).
- **Map / Comparison / Devices / Manage** — unchanged (per "keep the
  subpages"; C2 keeps Map's KPI tiles).

**Trade-off accepted:** the standalone Correlation page's expert extras —
dual-axis view and the lag-offset control — are retired with the page.
The lay-facing essentials (scatter, normalized overlay, matrix, Pearson/
Spearman) live on the hub; Pearson/Spearman/lag maths remain in
`correlate.py` if a deeper view is wanted later.

*Not applied (not approved this round): dropping Map's KPI tiles (C1),
narrowing the Devices audit window.*
