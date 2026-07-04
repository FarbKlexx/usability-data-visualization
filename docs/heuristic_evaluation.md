# Heuristic Evaluation — Air Quality Dashboard

**Method:** Heuristic evaluation after Nielsen & Molich (1990) / Nielsen (1994), using the course's 10-heuristic set.
**Evaluator:** 1 (single-evaluator, code-based inspection; the running UI was **not** observed — see §D).
**Date:** 2026-07-01.
**Scope:** `app.py`, all views in `app_pages/` (Overview, Time Series, Map, Comparison, Devices & Data Quality), the shared components in `src/components/`, the UI-relevant utilities in `src/utils/`, the data/DB layer as far as it determines loading/empty/error states (`src/data/loaders.py`, `src/db/`), and the theme (`.streamlit/config.toml`). Design intent was taken from `CLAUDE.md` and `CONTEXT.md`. Behavioural claims about widgets were checked against the installed Streamlit 1.57.0 where they matter (noted inline).

**Severity scale (Nielsen):** 0 = not a problem · 1 = cosmetic · 2 = minor · 3 = major · 4 = catastrophic. Each rating is justified by frequency / impact / persistence.

---

## A. Findings

### Global filter toolbar (all pages using `src/components/filter_bar.py`)

---

**ID**: HE-01
**Problem description**: Time filtering is limited to four fixed presets ("24 h", "7 d", "30 d", "All"). There is no way to select a custom or absolute date range (e.g. "1–15 September 2025" or a specific pollution episode). On the Comparison page this is unmitigable: all statistics (means, quartiles) are computed strictly over the preset window (`comparison.py:57`), and zooming the charts does not re-compute them. On Time Series, drag-zoom offers a partial visual workaround, but the data stays bucket-averaged for the full preset window and KPIs/notices don't follow the zoom.
**Appearance in the system / interaction situation**: `src/components/filter_bar.py:32-37` (`RANGE_PRESETS`), `filter_bar.py:113-116` (segmented control is the only time input); consumed by `app_pages/overview.py:33-36`, `timeseries.py:29-32`, `comparison.py:29-32`.
**Violated heuristic**: 7. Flexibility & Efficiency
**Severity rating**: 3 — frequency: high (bounding an analysis to a specific period is a core dashboard task); impact: high on Comparison (task impossible), medium on Time Series (visual-only workaround); persistence: permanent, no in-app workaround for statistics.
**Verification**: [code-confirmed]

---

**ID**: HE-02
**Problem description**: Filter context does not travel between pages. Each view instantiates its own namespaced filter state with its own defaults (`prefix="ov"` / `"ts"` / `"cmp"`), so a user who selects sensor X and a range on Overview and then follows the invited drill-down ("Overview first — drill down on the other pages", `overview.py:26`) lands on the *default* sensor and *default* range of the next page and must re-build their context manually. The "Open full map" link (`overview.py:79`) likewise carries nothing. If the user does not notice the re-defaulted selector, they read data of the wrong sensor.
**Appearance in the system / interaction situation**: `src/components/filter_bar.py:82-93` (state keyed per page prefix); `app_pages/overview.py:33-36` vs `timeseries.py:29-32` vs `comparison.py:29-32` (independent defaults: 7 d vs 30 d vs 30 d).
**Violated heuristic**: 7. Flexibility & Efficiency (secondary: 6. Recognition over Recall — the user must remember and re-enter their context)
**Severity rating**: 3 — frequency: every cross-page drill-down with a non-default selection; impact: medium (re-selection friction, plus a misreading risk that the filter chips only partially mitigate); persistence: recurs on every navigation, cannot be overcome except by manual re-entry.
**Verification**: [code-confirmed]

---

**ID**: HE-03
**Problem description**: There is no user-facing error state for database failure. No page, loader, or component catches exceptions (`grep` over `app.py`, `app_pages/`, `src/data/`, `src/components/` finds zero `try/except`). Every page's first statement chain hits the DB (`load_devices()`, e.g. `overview.py:28`); if the Dockerised Postgres is not running or a query fails, the user gets Streamlit's raw red traceback (`OperationalError` with connection internals) instead of a plain-language message ("The database is not reachable — start it with `docker compose up -d`") and no path to recovery inside the app.
**Appearance in the system / interaction situation**: all pages; `src/db/connection.py:49-65` (engine built without guard), `src/data/loaders.py` (no error handling in any loader).
**Violated heuristic**: 9. Error Recovery (secondary: 1. Visibility)
**Severity rating**: 3 — frequency: low-to-medium (local Docker DB; wrong start order is easy); impact: catastrophic while it lasts (entire app unusable, developer jargon shown); persistence: until the user diagnoses it outside the app. Averaged: major.
**Verification**: [code-confirmed] (absence of handling provable; exact rendered traceback depends on Streamlit's `client.showErrorDetails` default, which shows details)

---

**ID**: HE-04
**Problem description**: Comparison statistics can silently compare unequal observation windows. The shared window is anchored to the newest reading *across the selection* (`filter_bar.py:134-138`); sensor coverage differs strongly (external feeds have 54–68 rows vs. hundreds of thousands for stationary units, one mobile track ends in 2023). A sensor with no rows in the window still gets a category slot but its mean is NaN → the bar simply does not render, with no on-chart flag; a sensor with *partial* overlap contributes a mean over a shorter effective period that is visually compared 1:1 against full-window means. Per-sensor counts (`n`) are disclosed only inside the collapsed "Show the numbers" expander. Only the everything-empty case is caught (`comparison.py:58-60`).
**Appearance in the system / interaction situation**: `app_pages/comparison.py:57-83` (bars/box from `load_comparison` stats), `src/components/charts.py:119-138` (`grouped_bar` renders NaN as an absent bar without notice), `comparison.py:85-101` (n hidden in expander).
**Violated heuristic**: 5. Error Prevention (secondary: 1. Visibility)
**Severity rating**: 3 — frequency: medium (occurs whenever device kinds with different coverage are mixed, which the multiselect invites); impact: high (wrong analytical conclusions on the page whose entire purpose is fair comparison — against the project's own "honest data" principle); persistence: invisible unless the user opens the expander and interprets `n`.
**Verification**: [code-confirmed] (logic provable; how often real selections trigger it needs data/UI verification)

---

**ID**: HE-05
**Problem description**: The time-range segmented control can be *deselected* (clicking the active segment returns `None` — the widget is not created with `required=True`, and Streamlit 1.57's default is `required=False`). The code then silently falls back to the page default (`range_key = st.session_state[k_range] or default_range`, `filter_bar.py:126`). Result: the control shows **no selected range** while the data is filtered by the default range, and the filter chip asserts a range ("7 d") that the adjacent control visibly does not show. Control state and applied state contradict each other.
**Appearance in the system / interaction situation**: `src/components/filter_bar.py:113-116` (no `required=True`), `filter_bar.py:126` (silent fallback), `filter_bar.py:144-151` (chip renders the fallback value).
**Violated heuristic**: 1. Visibility (secondary: 5. Error Prevention — `required=True` exists precisely to prevent this state)
**Severity rating**: 2 — frequency: low (needs an accidental second click on the active segment); impact: medium (contradictory status display, user may distrust or misread the filter); persistence: until the user re-clicks a preset.
**Verification**: [code-confirmed] (widget semantics verified against installed Streamlit 1.57 source)

---

### Overview (`app_pages/overview.py`)

---

**ID**: HE-06
**Problem description**: The Overview's sensor selector offers only stationary Shape-A units (`pool` filter), while Time Series and Comparison offer every sensor with data. A user who worked with the hi-res Gdańsk sensor or a mobile unit elsewhere will not find it in the Overview selector, and the UI never says why — the help text is a generic "Pick the sensor to display." The (good) editorial reason — sparse feeds would distort headline KPIs — exists only in a code docstring (`overview.py:10-11`).
**Appearance in the system / interaction situation**: `app_pages/overview.py:29-31` (pool restriction) vs `timeseries.py:27` and `comparison.py:22` (full pool); `filter_bar.py:108-111` (unchanged generic help).
**Violated heuristic**: 4. Consistency & Standards (secondary: 10. Help & Documentation — the rationale is not communicated)
**Severity rating**: 2 — frequency: medium (anyone tracking a non-stationary sensor); impact: medium (fruitless searching, apparent "missing device"); persistence: resolvable once the user infers the rule, but nothing helps them infer it.
**Verification**: [code-confirmed]

---

### Time Series (`app_pages/timeseries.py`) — also affects Overview's headline chart

---

**ID**: HE-07
**Problem description**: Chart zoom/pan state is destroyed by every rerun. None of the Plotly figures set `layout.uirevision`, and `st.plotly_chart` is called without stable state preservation, so any widget interaction — adding/removing a measure, toggling anything on the page — rebuilds the figures and resets the user's carefully-set zoom on *all* charts. Direct manipulation (the page's advertised interaction model, `timeseries.py:24`) is therefore not preserved across the very adjustments an exploration loop consists of ("zoom into an episode → add CO₂ to compare → zoom is gone").
**Appearance in the system / interaction situation**: `src/components/charts.py:48-116` (no `uirevision` anywhere in the module); `app_pages/timeseries.py:41-48` (measure multiselect sits above the charts and reruns the script on change); same mechanism on `overview.py:62-66`.
**Violated heuristic**: 3. User Control & Freedom (secondary: 7. Flexibility & Efficiency)
**Severity rating**: 2 — frequency: high during exploratory use; impact: medium (state loss, re-work, breaks the CONTEXT rule "no auto-reload in the middle of an analysis"); persistence: recurs on every widget change; workaround is to set measures first and zoom last, which nothing teaches.
**Verification**: [code-confirmed] (mechanism provable from code; exact reset behaviour is standard Streamlit/Plotly and should be confirmed once in the running UI)

---

### Map (`app_pages/map.py`)

---

**ID**: HE-08
**Problem description**: "Details on demand" is not wired to the map. Markers are not clickable (no `on_select` on `st.plotly_chart`); to see a sensor's readings the user must leave the map, find the same sensor *by name* in a separate dropdown below, and mentally re-link the two. The reverse link is also missing: choosing a sensor in the dropdown does not highlight its marker. Because marker labels are hover-only (`show_text=False` on both map views), locating a *named* sensor on the map means hovering markers one by one.
**Appearance in the system / interaction situation**: `app_pages/map.py:59-63` (chart without selection events), `map.py:73-97` (independent details dropdown), `map.py:60` and `overview.py:84` (`show_text=False`); `src/components/charts.py:196-211` (markers carry hover labels only).
**Violated heuristic**: 7. Flexibility & Efficiency (secondary: 6. Recognition over Recall)
**Severity rating**: 2 — frequency: high for the map's core "inspect this station" task; impact: medium (indirection and visual search instead of direct manipulation — the project's own stated standard); persistence: every use.
**Verification**: [code-confirmed]

---

**ID**: HE-09
**Problem description**: Marker colors mean two different things at once, with overlapping hues. On the Map page, sensors with data are colored by CAQI band while data-less devices fall back to *device-type* colors — both taxonomies share one map and one legend. The hue collisions are exact: orange `#E69F00` = CAQI "Medium" (`aqi.py:61`) **and** device type "External" (`charts.py:233`); vermillion `#D55E00` = CAQI "High" (`aqi.py:62`) **and** type "Mobile" (`charts.py:232`). Additionally, the Overview mini-map colors *all* markers by device type (`build_location_markers(loc)` without bands, `overview.py:82`), so the same marker changes meaning between Overview and Map. A user who scans by color can read "Medium pollution" where the dot means "external device".
**Appearance in the system / interaction situation**: `src/components/charts.py:229-257` (`_TYPE_COLOR` + fallback logic), `src/utils/aqi.py:58-64` (band colors), `app_pages/map.py:35-47` vs `app_pages/overview.py:81-87`.
**Violated heuristic**: 4. Consistency & Standards
**Severity rating**: 2 — frequency: medium (mixed marker populations are the normal case: located but data-less `b827eb*` devices and POIs coexist with banded sensors); impact: medium (color misreads on the central map task; mitigated by legend grouping and hover text); persistence: every map view.
**Verification**: [code-confirmed] (palette overlap provable; which collisions actually co-occur on screen needs UI verification)

---

**ID**: HE-10
**Problem description**: The same CAQI band is encoded with different colors in different components. The "Low" band is Okabe-Ito **yellow** on map markers and legend (`aqi.py:60`) but a **blue** badge on the KPI tile (`kpi.py:34` maps level 1 → `"blue"`), although the installed Streamlit 1.57 supports `:yellow-badge[...]` (verified in `color_util.py`). "Very low"→green and "High"→red are near matches, so the yellow/blue swap stands out as an unexplained category-color change between the Overview/Map KPI tiles and the map itself.
**Appearance in the system / interaction situation**: `src/components/kpi.py:34` (`_BAND_BADGE`), `src/utils/aqi.py:58-64` (band palette); visible wherever `aqi_tile` (Overview, Map details) and band-colored markers (Map) appear together.
**Violated heuristic**: 4. Consistency & Standards
**Severity rating**: 2 — frequency: medium (both encodings visible in one session, on the Map page even on one screen); impact: low-to-medium (band identity is triple-encoded with icon + label, so no information is lost, but the color channel contradicts itself); persistence: constant.
**Verification**: [code-confirmed]

---

**ID**: HE-11
**Problem description**: Toggling both map layers off yields a completely blank map with no message. `markers` becomes `None` and `tracks` empty; `map_figure` then renders bare tiles at a default center/zoom (`charts.py:213-218`) — there is no empty-state notice equivalent to the `_empty(...)` message other charts get.
**Appearance in the system / interaction situation**: `app_pages/map.py:29-33` (pills allow empty selection), `map.py:47-63`; `src/components/charts.py:163-226` (no empty annotation path for maps).
**Violated heuristic**: 1. Visibility
**Severity rating**: 1 — frequency: low (deliberate double-deselect); impact: low (the deselected pills sit directly above the map and reversal is one click); persistence: none.
**Verification**: [code-confirmed]

---

**ID**: HE-12
**Problem description**: On first (uncached) visit, the Map page runs one `load_latest` query **per located sensor** in a Python loop to compute CAQI bands, and this loader has spinners disabled (`show_spinner=False`). During those N sequential DB round-trips the user gets no progress feedback beyond Streamlit's generic running indicator — no "computing air-quality bands…" status, unlike the labeled spinners used elsewhere (`load_devices`, `load_timeseries`, Devices' sentinel audit).
**Appearance in the system / interaction situation**: `app_pages/map.py:36-45` (N+1 loop), `src/data/loaders.py:233` (`@st.cache_data(ttl=600, show_spinner=False)`).
**Violated heuristic**: 1. Visibility
**Severity rating**: 2 — frequency: first visit per session and every cache expiry (TTL 600 s); impact: low-to-medium (perceived freeze on the page most likely to be shown to guests); persistence: recurs. Latency magnitude unknown from code alone.
**Verification**: [code-confirmed] for the missing feedback; [needs UI verification] for actual delay length.

---

### Comparison (`app_pages/comparison.py`)

---

**ID**: HE-13
**Problem description**: The comparable-measure list is a hard-coded subset. `metric_options` filters against `("pm2_5", "pm10_0", "co2", "temp1", "inn_hum", "inn_pres")` — omitting **Housing temperature** (`inn_temp`), which exists on every stationary sensor (`metrics.py:210` includes it in `STATIONARY_METRICS`) and is offered on the Time Series page. A user can plot housing temperature for each sensor individually but cannot compare it across sensors; the selector gives no hint the list is curated ("Only measures available on every selected sensor are offered" is factually wrong here — `inn_temp` *is* available on every default sensor).
**Appearance in the system / interaction situation**: `app_pages/comparison.py:42` (hard-coded tuple) and `comparison.py:52-55` (help text); contrast `timeseries.py:39-45` (offers all available metrics).
**Violated heuristic**: 4. Consistency & Standards (secondary: 7. Flexibility & Efficiency — the comparison task is blocked for that measure)
**Severity rating**: 2 — frequency: low-to-medium (climate comparison is a secondary task); impact: medium (task impossible; help text actively misleading); persistence: permanent.
**Verification**: [code-confirmed]

---

### Devices & Data Quality (`app_pages/devices.py`)

---

**ID**: HE-14
**Problem description**: Developer/implementation jargon leaks into user-facing copy. Examples: a catalog column "Shape" whose full explanation is "A/B/C/Ext column shape" (an internal DB-table classification meaningless to a dashboard user, `devices.py:65`); the KPI help "Mobile m13–m20: registered but never logged." (internal device codes, `devices.py:34`); the audit bullet "**No native `ts` index** — a reversible migration adds one per populated table so time-range queries stay responsive" (pure engineering changelog, `devices.py:117-118`); and on the Map page the caption "The hi-res Gdańsk sensor's stored lat/lon were de-swapped on load" (`map.py:66-67`) — provenance trivia phrased in developer language on an end-user view.
**Appearance in the system / interaction situation**: `app_pages/devices.py:34, 65, 103-120`; `app_pages/map.py:64-68`.
**Violated heuristic**: 2. Match with Real World (secondary: 8. Minimalist Design)
**Severity rating**: 2 — frequency: medium (Devices page is explicitly part of the product; the Map caption is on a primary view); impact: low-to-medium (noise and confusion, though the transparency intent is legitimate); persistence: constant.
**Verification**: [code-confirmed]

---

### Cross-cutting

---

**ID**: HE-15
**Problem description**: Yellow `#F0E442` is used as a data color on light backgrounds: the "CAQI (measured)" metric draws a yellow line on the white chart background (`metrics.py:191`, background `#FFFFFF` per `config.toml:10`), and "Low"-band map markers are yellow on light OSM tiles. A thin yellow-on-white line has extremely low luminance contrast and can be near-invisible — a risk the codebase itself acknowledges: `track_palette` deliberately skips yellow for map lines because of "low contrast on map" (`charts.py:317`), but the same rule is not applied to the metric registry or band markers.
**Appearance in the system / interaction situation**: `src/utils/metrics.py:183-195` (caqi metric color), `src/utils/aqi.py:60` (Low band), `src/components/charts.py:315-319` (own contrast rule, applied only to tracks); visible on Time Series (Gdańsk feed selected) and on the Map.
**Violated heuristic**: 4. Consistency & Standards (contrast standards and the project's own rule, applied inconsistently)
**Severity rating**: 2 — frequency: low-to-medium (caqi plotting requires selecting the Gdańsk feed; Low-band markers are common); impact: medium (data can be effectively invisible); persistence: constant in light mode.
**Verification**: [code-confirmed] for the color choices; [needs UI verification] for perceived severity on screen.

---

**ID**: HE-16
**Problem description**: Core documented interactions rely on click targets far below the project's own 44×44 px minimum. "Click a legend entry to toggle a series" is the advertised series filter (`overview.py:70`, `timeseries.py:83`), but Plotly legend entries are ~12–14 px text rows; map markers — the only hover/selection handle on the map — are 13 px dots (`charts.py:204`, `size=13`). On touch devices (CONTEXT mandates mobile-first) these are difficult or error-prone to hit.
**Appearance in the system / interaction situation**: `src/components/charts.py:77` (legend), `charts.py:204` (marker size); interaction hints at `overview.py:70`, `timeseries.py:83`.
**Violated heuristic**: 7. Flexibility & Efficiency (secondary: 4. Consistency & Standards — violates the project's declared 44 px standard)
**Severity rating**: 2 — frequency: high on touch, medium with mouse; impact: medium (mis-taps, failed toggles); persistence: constant. Rendered sizes depend on Plotly defaults and DPI.
**Verification**: [needs UI verification] (marker size 13 px and legend defaults are code-confirmed; effective on-screen target sizes are not)

---

**ID**: HE-17
**Problem description**: No keyboard path exists for the chart-centric interactions the app is built around. Zooming has a pointer alternative (Plotly modebar buttons remain enabled), but series toggling (legend click), map panning, and marker inspection are pointer-only; no keyboard shortcuts are defined anywhere; and the accessibility helper module intended for "ARIA-friendly labels, keyboard-navigation utilities, and contrast-checking" is an empty placeholder (`src/utils/accessibility.py:1-7`). CONTEXT's checklist #8 ("keyboard navigation and ARIA labels") is unimplemented.
**Appearance in the system / interaction situation**: all chart views; `src/utils/accessibility.py` (placeholder); no `key`-bound shortcuts or focus management anywhere in `app_pages/`.
**Violated heuristic**: 7. Flexibility & Efficiency (universal usability)
**Severity rating**: 2 — frequency: low (affects keyboard/AT users); impact: high for those users (core interactions unusable), partially platform-inherent (Streamlit/Plotly); persistence: permanent.
**Verification**: [code-confirmed] that nothing was implemented; [needs UI verification] for what Streamlit/Plotly provide out of the box.

---

**ID**: HE-18
**Problem description**: Analyses cannot be bookmarked or shared. Filter state (sensor, range, measures, layers) lives only in `st.session_state`; `st.query_params` is never used, so a URL always opens the page defaults. CONTEXT explicitly lists "bookmarks" under easy reversal/efficiency; for a data dashboard, "send a colleague what I'm seeing" is a standard expectation.
**Appearance in the system / interaction situation**: whole app; `grep` finds no `query_params` usage; state seeding in `src/components/filter_bar.py:89-93`.
**Violated heuristic**: 7. Flexibility & Efficiency
**Severity rating**: 2 — frequency: medium; impact: medium (re-describing state manually, no deep links); persistence: permanent.
**Verification**: [code-confirmed]

---

**ID**: HE-19
**Problem description**: In-app help is limited to widget tooltips and a one-line "About" ("Air Quality Usability Dashboard — built for the Usability course.", `app.py:21-23`). There is no help view, glossary, or explanation of the CAQI scale's thresholds — notably, the code *computes* human-readable band ranges (`CAQIBand.range_label`, `aqi.py:47-53`: "PM2.5 15–30 µg/m³") but never displays them anywhere, so a user cannot find out where "Medium" ends and "High" begins. The interaction hint captions ("Drag to zoom · double-click to reset…") are good task-focused micro-help but cover only chart gestures.
**Appearance in the system / interaction situation**: `app.py:21-23` (menu), `src/utils/aqi.py:47-53` (unused `range_label`), band tile help limited to `COMPUTED_NOTE` (`kpi.py:74`, `aqi.py:33`).
**Violated heuristic**: 10. Help & Documentation
**Severity rating**: 2 — frequency: low-to-medium (first-time and occasional users); impact: medium (band judgments can't be calibrated; no central help); persistence: permanent.
**Verification**: [code-confirmed]

---

**ID**: HE-20
**Problem description**: Warning messages carry an *info* icon. All four `st.warning` calls use `icon=":material/info:"` — a yellow warning container with an information glyph — while genuine info messages use the same glyph. The severity signalled by the icon contradicts the severity signalled by the container color, diluting the iconographic language.
**Appearance in the system / interaction situation**: `app_pages/timeseries.py:52`, `app_pages/comparison.py:44-49` and `comparison.py:59`, `src/components/filter_bar.py:129`.
**Violated heuristic**: 4. Consistency & Standards
**Severity rating**: 1 — frequency: low (empty/edge states); impact: low; persistence: momentary.
**Verification**: [code-confirmed]

---

**ID**: HE-21
**Problem description**: Relative time labels ("24 h", "7 d") resolve against the frozen dataset's newest reading (late 2025), not the actual present — "last 24 h" data is months old at evaluation time (2026-07). This is a deliberate, sensible design for a frozen dataset and is disclosed (control help "Window before the most recent reading", `filter_bar.py:115`; resolved date-span chip, `filter_bar.py:146-151`; "Latest reading …" caption, `overview.py:46`), but the preset labels themselves still borrow "recency" language that does not match the real world, and first-time users may initially misread the data as current.
**Appearance in the system / interaction situation**: `src/components/filter_bar.py:16-19` (design note), `:32-37` (labels), `:113-116`, `:144-151`.
**Violated heuristic**: 2. Match with Real World
**Severity rating**: 1 — frequency: first exposure mainly; impact: low (three separate disclosures correct the impression); persistence: low.
**Verification**: [code-confirmed]

---

### Candidates — not counted as findings, need verification on the running UI

- **Responsive/mobile behaviour**: the Overview renders a 6-column KPI row (`overview.py:48`) and Devices a 4-column summary plus a wide table; CONTEXT demands mobile-first. Streamlit stacks columns on small screens, but whether the result is usable (order, scroll length, chart heights) cannot be judged from code.
- **Dark-mode artefacts**: the map legend background is hard-coded near-white (`charts.py:224`) and OSM tiles are always light, while a dark theme is offered (`config.toml:57-63`) — probably a visible clash in dark mode; cosmetic at most.
- **First-load latency overall**: `load_devices` UNION-ALL row-counts across all sensor tables (`loaders.py:136-149`) — spinner exists, magnitude unknown.
- **Plotly modebar discoverability**: whether the zoom-reset affordances are visible enough on hover-less (touch) devices.

---

## B. Summary table

| ID | View | Violated heuristic (primary) | Severity |
|-------|--------------------------|------------------------------|----------|
| HE-01 | All (filter bar) | 7. Flexibility & Efficiency | 3 |
| HE-02 | All (navigation flow) | 7. Flexibility & Efficiency | 3 |
| HE-03 | All (error state) | 9. Error Recovery | 3 |
| HE-04 | Comparison | 5. Error Prevention | 3 |
| HE-05 | All (filter bar) | 1. Visibility | 2 |
| HE-06 | Overview | 4. Consistency & Standards | 2 |
| HE-07 | Time Series, Overview | 3. User Control & Freedom | 2 |
| HE-08 | Map | 7. Flexibility & Efficiency | 2 |
| HE-09 | Map, Overview | 4. Consistency & Standards | 2 |
| HE-10 | Map, Overview | 4. Consistency & Standards | 2 |
| HE-11 | Map | 1. Visibility | 1 |
| HE-12 | Map | 1. Visibility | 2 |
| HE-13 | Comparison | 4. Consistency & Standards | 2 |
| HE-14 | Devices, Map | 2. Match with Real World | 2 |
| HE-15 | Time Series, Map | 4. Consistency & Standards | 2 |
| HE-16 | All charts/map | 7. Flexibility & Efficiency | 2 |
| HE-17 | All charts | 7. Flexibility & Efficiency | 2 |
| HE-18 | All | 7. Flexibility & Efficiency | 2 |
| HE-19 | All | 10. Help & Documentation | 2 |
| HE-20 | TS, Comparison, filter bar | 4. Consistency & Standards | 1 |
| HE-21 | All (filter bar) | 2. Match with Real World | 1 |

## C. Aggregation

**Findings per severity**

| Severity | Count | IDs |
|---|---|---|
| 4 — catastrophic | 0 | — |
| 3 — major | 4 | HE-01, HE-02, HE-03, HE-04 |
| 2 — minor | 14 | HE-05…HE-10, HE-12…HE-19 |
| 1 — cosmetic | 3 | HE-11, HE-20, HE-21 |

**Findings per primary heuristic** (secondary assignments in parentheses)

| Heuristic | Primary count | IDs |
|---|---|---|
| 1. Visibility | 3 | HE-05, HE-11, HE-12 (+ sec: HE-03, HE-04) |
| 2. Match with Real World | 2 | HE-14, HE-21 |
| 3. User Control & Freedom | 1 | HE-07 |
| 4. Consistency & Standards | 6 | HE-06, HE-09, HE-10, HE-13, HE-15, HE-20 (+ sec: HE-16) |
| 5. Error Prevention | 1 | HE-04 (+ sec: HE-05) |
| 6. Recognition over Recall | 0 | (sec: HE-02, HE-08) |
| 7. Flexibility & Efficiency | 6 | HE-01, HE-02, HE-08, HE-16, HE-17, HE-18 (+ sec: HE-07, HE-13) |
| 8. Minimalist Design | 0 | (sec: HE-14) |
| 9. Error Recovery | 1 | HE-03 |
| 10. Help & Documentation | 1 | HE-19 (+ sec: HE-06) |

The profile is characteristic of a theory-driven baseline: the *presentation* heuristics (feedback wording, honesty disclosures, minimalist layout) are largely satisfied, while most debt sits in **Flexibility & Efficiency** (no custom ranges, no state carry-over, no deep links, pointer-only interactions) and **Consistency** (color semantics and option sets drifting between views).

**What to fix first**

1. **HE-03** — wrap data access in a friendly error state (one `try/except` around the loaders with a plain-language message + retry hint). Highest impact-per-effort; a raw traceback is the worst possible first impression.
2. **HE-04** — flag partial/absent coverage directly on the Comparison charts (e.g. per-bar `n`, an on-chart "no data in window" marker, or normalising the window per sensor). The page can currently mislead silently, contradicting the project's honesty principle.
3. **HE-01** — add a custom date-range input (e.g. `st.date_input` pair behind a "Custom…" preset) so analyses aren't locked to four windows.
4. **HE-02** — share sensor/range state across pages (single global filter state or carrying `session_state` keys through navigation) so drill-down keeps context.
5. **HE-07** — set `uirevision` on all figures so zoom survives reruns; this single change makes the advertised direct-manipulation model actually hold during exploration.

## D. Coverage & method notes

**Views fully assessed from code:** Overview, Time Series, Map, Comparison, Devices & Data Quality, plus the shared filter bar, KPI tiles, chart builders, palette/metrics/AQI utilities, theme config, and the navigation shell (`app.py`). For each view the widget tree, defaults, feedback captions, and empty/error paths were reconstructed from source; widget behaviour that matters (segmented-control deselection, badge color support, `menu_items` semantics) was verified against the installed Streamlit 1.57.0 package rather than assumed.

**Assessable only on the running dashboard (evaluator should confirm):**
- Rendered sizes/contrast: effective touch-target sizes (HE-16), yellow-line visibility (HE-15), dark-mode map legend clash (candidate).
- Latency and perceived feedback: Map first-load delay (HE-12), overall first-load with cold caches (candidate).
- Responsive behaviour on phone/tablet widths (candidate).
- Runtime interaction details: exact zoom-reset behaviour after reruns (HE-07), Plotly modebar affordances on touch, actual co-occurrence of colliding marker colors (HE-09) given the live data.

**Heuristics with no primary findings:** 6 (Recognition over Recall) and 8 (Minimalist Design) — both were checked per view, not skipped. Recognition is broadly well served (filter chips echo active state, human-readable sensor labels, legends on-chart, active-filter badges); minimalism is well served (≤ ~7 blocks per view, no chart junk, progressive disclosure via tabs/expanders). Their remaining weaknesses appear as secondary assignments (HE-02, HE-08, HE-14).

**Notable strengths observed (for balance, not scored):** hidden-sentinel disclosure everywhere (`hidden_notice`), unit-honest separate axes instead of dual axes, zero-based concentration axes, triple-encoded CAQI band (icon + label + color), consistent Okabe-Ito metric colors from a single registry, an always-present Reset with echoed filter chips, and labeled spinners on the heavy loaders.

**Limitations.** This is a **single-evaluator, code-based first pass**. Nielsen's own findings apply: one evaluator typically uncovers ~35 % of usability problems, and code inspection cannot observe rendered layout, timing, feel, or real user error patterns. Severity ratings for anything perception- or latency-dependent are provisional until confirmed on the running dashboard (`uv run streamlit run app.py`). One suspected issue was checked and **dismissed** during evaluation (the Devices audit's hard-coded 2023–2026 sentinel window in `devices.py:81-82` does cover the dataset's actual 2025 span, so no undercount occurs) — false positives were actively filtered rather than padded.
