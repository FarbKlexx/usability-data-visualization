# Implementation Plan — Adaptive Device View & Mobile Routes

> **Companion to** the consolidation plan (dashboard-as-hub). The dashboard now
> shows only stationary sensors and presents many controls at once without a
> clear hierarchy. This phase makes the dashboard **adapt to the selected
> device** (stationary *or* mobile), adds real **route segmentation** for mobile
> sensors, and separates **primary information from secondary functions** so the
> view stops feeling overwhelming. Scope is structural and functional; visual
> polish comes after.
>
> **`CONTEXT.md` is the standard for this phase** — especially Miller's 7±2,
> Hick's Law (progressive disclosure), the Sweet Spot (core centered, secondary
> at the edges), and "top-left = most important". The agent re-reads it before
> changing layout.

### Locked decisions

- **Route split threshold:** **1 hour** (gap > 1 h → new route), surfaced as an adjustable control.
- **Route point coloring:** **color points by PM value** (pollution along the path), using the sequential Viridis palette + a legend.
- **Secondary functions:** placed in **tabs** within the dashboard (stronger separation than expanders), keeping the primary view clean.

---

## 0. Guiding idea

Two structural shifts:

1. **One device picker for everything.** The dashboard lists *all* devices that
   carry data — stationary and mobile together — and the page reshapes itself to
   the selected device's type. The user shouldn't have to know in advance which
   "kind" of view they need.
2. **A clear primary/secondary split.** For any selected device, the dashboard
   answers one main question first (with one headline visual), and pushes
   everything else (advanced controls, comparisons, raw toggles) into clearly
   secondary, collapsible places. The user should always be able to tell at a
   glance what the main information is.

---

## A. Unified device picker

- A single selector lists every device that has measurement data, grouped by
  type (e.g. a "Stationary" group and a "Mobile" group) so the two kinds are
  visible but not mixed into one flat list.
- The list is driven by the existing `load_devices()` catalog, filtered to
  devices whose sensor table exists and is non-empty (this naturally excludes the
  10 empty `b827eb*` registrations).
- Selecting a device sets the active device in session state; the rest of the
  dashboard renders according to that device's `ootype` (stationary vs. mobile).
- A sensible default is pre-selected (e.g. the busiest stationary sensor) so the
  dashboard is never empty on first load.

---

## B. Adaptive layout by device type

The dashboard renders one of two primary layouts based on the selected device.

### B1. Stationary device → trend + location
- **Primary:** the plain-language air-quality status (CAQI category) and the
  **PM time-series chart** (as today) for the selected time range.
- **Plus a location map:** a small map showing **where the stationary sensor
  sits** (single marker from `tbl_location`), so the spatial context is present
  even though the device doesn't move.
- Climate measures (temp/humidity/pressure) stay available but secondary (see
  §D).

### B2. Mobile device → segmented routes on a map
- **Primary:** a **map showing the device's routes** — the GPS track split into
  separate trips (see §C), each route drawn as its own path so distinct trips are
  visually distinguishable.
- A time-series PM chart is *not* the headline for a mobile device; if shown at
  all, it is secondary and ideally scoped to a single selected route.
- **Color the route points by PM value** so pollution *along the route* is
  readable: use the sequential Viridis palette with a legend and value tooltips,
  so the air-quality payoff of a mobile sensor is visible at a glance.

### B3. Fixed-position edge case (`sensor_781c3ce6ad3c`)
- This device has GPS but sits at one fixed location (and stores lat/lon
  axis-swapped). Treat it like a **location marker**, not a route: show its single
  position on a map (after swapping axes in the loader) plus its measures.

---

## C. Route segmentation logic (mobile)

Currently a mobile sensor's points form one connected track. Split them into
routes:

1. **Load the track** for the device: rows with non-NULL `pos`, ordered by `ts`.
2. **Deduplicate first** — `sensor_b827eb0fae5c` (A3) contains duplicate rows
   (identical `ts`/values across ids); drop them before segmenting, or the gap
   logic misbehaves.
3. **Split on a time gap:** walk the ordered points; whenever the gap to the
   previous point exceeds the **threshold (default 1 hour)**, start a new route.
   In pandas: sort by `ts`, compute `ts.diff()`, and assign
   `route_id = (diff > threshold).cumsum()`.
4. **Drop trivial routes:** a route with only 1 point (or below a tiny minimum)
   isn't a path; either hide it or mark it as a single point.
5. **Return** a frame carrying `route_id` so the map can render each route as its
   own path and the UI can list/select routes.

The threshold is a single configurable value (default 1 h), surfaced as a control
so the user can adjust how aggressively trips are split.

---

## D. Information hierarchy — primary vs. secondary (the overwhelm fix)

Apply across the dashboard, justified by `CONTEXT.md`:

- **Primary zone (top, centered):** the device picker, the plain-language status,
  and the one headline visual for the device type (chart for stationary, route
  map for mobile). This is what the user sees first and is meant to read at a
  glance — kept within a small module count (Miller).
- **Secondary zone (below, in tabs):** advanced controls, additional measures,
  correlation, raw/cleaned toggle, export, threshold lines. Group them into
  **tabs** within the dashboard (progressive disclosure, Hick's Law) so these are
  reachable but clearly separated from — and not competing with — the primary
  answer.
- **Consistent placement:** the device picker and status live in the same spot
  regardless of device type, so switching devices doesn't move the user's anchor
  (mental-model stability, Shneiderman consistency).
- **One headline visual at a time:** the primary slot shows exactly one main
  chart/map for the selected device — it swaps content with the selection rather
  than stacking more panels.

---

## E. Data-layer changes (`src/data`)

| Function | Change | Purpose |
| --- | --- | --- |
| `load_devices()` | ensure it returns `ootype` (stationary/mobile) and a has-data flag | drives the unified picker + the adaptive branch |
| `load_routes(mac, gap='1h', min_points=2)` | **new** (or extend `load_tracks`) | dedup → order by `ts` → segment by time gap → return points with `route_id` |
| `load_locations()` | reuse | stationary marker(s) on the map |
| `load_timeseries(...)` | reuse | stationary headline chart; optional per-route mobile chart |

Loaders stay `@st.cache_data`; pages do no I/O (per `CLAUDE.md`). The
axis-swap for `781c3ce6ad3c` is handled inside the loader, not in the page.

---

## F. Build order

1. **Unified picker (A):** list all data-bearing devices grouped by type; set
   active device in session state; pick a sensible default.
2. **Adaptive branch (B):** render stationary vs. mobile layout from the selected
   device's `ootype`.
3. **Route segmentation (C):** `load_routes(...)` with dedup + 1 h gap split;
   render routes on the mobile map.
4. **Stationary location map (B1):** add the single-marker map to the stationary
   view; handle the `781c3ce6ad3c` fixed-point case (B3).
5. **Hierarchy pass (D):** move advanced/secondary controls into collapsible
   secondary zones; keep one headline visual in the primary slot.
6. **Review against `CONTEXT.md`:** module count, placement, consistency,
   color+label, reset reachability.

Each step is a self-contained, documentable prompt, matching the structured
workflow used so far.

---

## G. Settled

All three open questions are decided (see "Locked decisions" at the top): route
split threshold **1 hour** (adjustable); route points **colored by PM value**
(Viridis + legend); secondary functions in **tabs**. The only thing to tune
during implementation is the exact set of tabs and which controls land in each —
the agent proposes a grouping and the user confirms.
