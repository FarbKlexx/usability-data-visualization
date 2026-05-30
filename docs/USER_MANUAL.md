# Air Quality Dashboard — User Manual

A guide to everything you can **see and do** in the app, page by page.
No code or setup here — just how to use it.

---

## 1. What this app is for

It's an **air-quality dashboard** for a network of particulate-matter
(PM) sensors in and around Minden (Germany), with a couple of external
feeds (Gdańsk, Hannover) and two **mobile** sensors that travelled
routes. You use it to answer questions like:

- *Is the air quality good right now at sensor X?*
- *How have PM2.5 and PM10 changed over the last week / month?*
- *Where are the sensors, and what routes did the mobile ones take?*
- *Which sensor is the most polluted on average?*
- *Do two measures move together (e.g. does PM rise as temperature drops)?*
- *Which devices have data, how clean is it, and what are the known quirks?*

The audience is **non-experts**: every view leads with a plain-language
answer, and the charts are the supporting evidence underneath.

> **About the dates.** The dataset is **frozen** (it ends in late 2025).
> So "last 24 h / 7 d / 30 d" means *relative to the newest reading in the
> data*, not today's date. This is on purpose — otherwise every view would
> look empty.

---

## 2. Getting around

### The top navigation bar
Six pages, always reachable from the bar at the top:

| Page | One-line purpose |
|------|------------------|
| **Dashboard** | The hub — pick any device, get its air-quality answer + headline visual at a glance. |
| **Time Series** | Deep dive into one sensor over time (zoom, smooth, thresholds, export…). |
| **Map** | Where the sensors are + mobile tracks; click for details. |
| **Comparison** | One measure across several sensors, side by side. |
| **Devices & Data Quality** | The full device catalogue + an honest account of data quirks. |
| **Manage** | Turn optional features on/off; manage saved thresholds and views. |

### Controls you'll see on most pages

- **Sensor / device picker** — choose what to look at.
- **Time range** — quick presets: **24 h · 7 d · 30 d · All** (relative to the
  latest reading; see the note above).
- **Reset** — a button that restores the default sensor and range. It's
  *always* available, so you can never get "stuck" in a filtered state.
- **Active-filter chips** — small badges that echo back what's currently
  selected (sensor, range, and the exact date span), so you never have to
  remember what you filtered.

### Things that work on every chart
- **Drag** across a chart to **zoom in**; **double-click** to reset.
- **Click a legend entry** to hide/show that series.
- **Hover** any point for a tooltip with the value, unit, and timestamp.
- **Maps**: drag to pan, scroll to zoom.

### Colour is never the only signal
Throughout the app, colour is always paired with a **label, icon, shape, or
number** — so the meaning survives for colour-blind readers and anyone
skimming. The palette is colour-blind-safe.

---

## 3. Concepts worth knowing (they appear everywhere)

- **The measures.** PM2.5 and PM10 (particulates, in µg/m³), CO₂ (ppm),
  outdoor temperature, housing temperature, humidity, and pressure. Not
  every device records all of them — the app only ever offers the measures a
  device actually has.
- **CAQI air-quality band.** A computed European Common Air Quality Index
  category — **Very low → Low → Medium → High → Very high** — derived from
  the worse of PM2.5/PM10. The app shows it as a plain word (**Good / Fair /
  Moderate / Poor / Very poor**) plus a coloured badge and a distinct
  face icon. It is always labelled **"computed"** — it's derived, not a raw
  sensor value.
- **Hidden saturation readings (honesty).** Sensors sometimes report a
  "stuck at maximum" value (e.g. PM2.5 = 999.9). These are **hidden from
  charts and averages so they don't mislead — but always counted and
  disclosed** in a small note ("*N readings … were hidden*"). Nothing is
  silently dropped. On Time Series you can flip a **Show raw** toggle to see
  them.
- **Honest axes.** Concentration charts start at zero; nothing is truncated
  to exaggerate a trend.
- **Saving & sharing.** The Dashboard and Time Series mirror your current
  view into the page URL — **bookmark or copy the link** to return to the
  exact same view.

---

## 4. The pages in detail

### 4.1 Dashboard — the adaptive hub

This is the landing page and the place to start. It **adapts to the device
you pick**.

**Always at the top (the "primary" zone):**
1. **Device picker** — lists *every device that has data*, grouped by type
   (Stationary, Mobile, External, Specialty). Plus the time range and Reset.
2. **Plain-language status** — a sentence like **"Air quality: Good"** with
   the CAQI badge ("CAQI: Very low") and a one-line explanation ("…pollution
   is very low"). This is the headline answer; you don't need to read a chart
   to get it.
3. **One headline visual**, chosen by device type:
   - **Stationary / fixed device** → a **PM2.5 & PM10 time-series chart** for
     the selected range, plus a **small map showing where the sensor sits**.
   - **Mobile device** → a **route map**: the GPS track split into separate
     **trips**, each drawn as its own path, with the **points coloured by
     PM2.5** (Viridis scale + colour legend) so you can see pollution *along
     the route*. A caption tells you how many trips and points are shown.

**Below, in tabs (the "secondary" zone — everything else):**
- **Measures & data** — the current-value KPI tiles (PM2.5, PM10, CO₂, temp,
  humidity + the CAQI tile, each with a 24-hour trend arrow); a **measure
  picker** that charts any combination (different units are charted
  separately); a **Show raw** toggle; a **CSV download** of exactly what's on
  screen; and an **"Open this device in Time Series"** button for the full
  depth.
- **Correlation** — *verdict first*: pick two or more measures and get a
  colour-coded, plain-language verdict per pair — e.g. **"↓ Moderate
  negative · PM2.5 ↔ Temp. · r = −0.61"**. Strength bands by |r|: **under 0.3
  = no/weak · 0.3–0.7 = moderate · over 0.7 = strong**; the arrow shows
  direction. *Then* the supporting chart: a **scatter** (with a best-fit
  line) or a shape-comparison **overlay** for two measures, or a
  **correlation matrix** heat-grid for three or more. A reminder that
  *correlation is not causation*.
- **Routes** *(mobile devices only)* — adjust **how trips are split** (start a
  new trip when the gap exceeds 15 min … 6 h; default **1 hour**); a **table**
  of every trip (start, end, duration, number of points, mean PM2.5); and a
  **trip picker** that highlights one trip on the map above and charts that
  trip's **PM2.5 over time**.

> **The fixed-position "Hi-res PM sensor"** has GPS but never moved, so it's
> shown as a single **map marker** (with its coordinates corrected), not as a
> route.

---

### 4.2 Time Series — deep dive into one sensor

The most powerful page for exploring a single sensor over time.

**What you can do:**
- **Pick the sensor and time range** (top toolbar, with Reset).
- **Pick the measures** to plot (multi-select). Measures with different units
  are drawn in **separate charts** (never forced onto a misleading shared
  axis).
- **Aggregation** — choose how finely the data is averaged into buckets:
  **Auto · 1 min · 5 min · 15 min · 1 hour · 6 hours · 1 day**. A caption tells
  you the bucket size and point count.
- **Rolling average** — a slider overlays a smoothed line (the raw line stays
  visible underneath, so the smoothing is shown, not substituted).
- **Show raw (unfiltered)** — include the saturation/sentinel readings to
  inspect the device's "stuck at max" behaviour directly (with a warning that
  it can distort the axes).
- **Reference thresholds** — draw a horizontal reference line per measure;
  readings at or above it are emphasised. Defaults come from any thresholds
  you saved on the Manage page.
- **Download current view (CSV)** — exactly the points on screen.
- **Save this view** — give the current sensor/measures/range/bucket a name;
  it appears on the **Manage** page and can be re-opened later.
- The page is **bookmarkable** — the URL captures your view.

**Optional modules** (can be switched on/off on the Manage page):
- **Annotations** — mark a time range (or a single point) with a label and
  note; saved annotations appear as **shaded bands** on the charts. You can
  list and delete them.
- **Raw readings & flags** — a table of the newest 200 raw rows in range;
  **flag** an individual reading as *suspect / confirmed / ignore* with a note
  (this never changes the underlying data). Flags can be listed and deleted.
- **Particle-size distribution** — for the high-resolution Gdańsk sensor only:
  mean concentration per particle-size class.

---

### 4.3 Map — where the sensors are

A spatial view of the whole network.

**What you can see/do:**
- **Layer toggles** (pills): **Stationary & fixed** locations and/or
  **Mobile tracks**.
- **Markers** are coloured by each sensor's current **CAQI band**, and the
  **legend doubles as the key** (so colour isn't the only signal). A caption
  notes that the high-res Gdańsk sensor's coordinates were corrected on load,
  and that one mobile track reaches back to 2023.
- **Mobile tracks** are drawn as coloured paths.
- **Details on demand** — pick a sensor from the dropdown to see its **latest
  readings** as KPI tiles + CAQI tile, and an **"Explore in Time Series"**
  button that jumps to the Time Series page focused on that sensor.
- **Edit a location** — correct a station's **name, city, street, postcode,
  or coordinates**; a small **preview map updates as you type**, and
  **Save** writes the change. (Every edit is reversible and confirmed.)

---

### 4.4 Comparison — sensors against each other

Compare **one measure across several sensors** over a shared time range.

**What you can do:**
- **Pick several sensors** (multi-select) and a time range.
- **Pick the measure** — only measures that *all* selected sensors share are
  offered, so the comparison is fair.
- **Averages tab** — a bar per sensor showing the mean, with the exact value
  printed on each bar.
- **Distribution tab** — a box plot per sensor (median, quartiles, min/max),
  so spread and outliers are visible honestly.
- A note discloses how many saturation readings were excluded.
- **Download comparison (CSV)** and a **"Show the numbers"** table (n, mean,
  min, Q1, median, Q3, max, hidden count).

---

### 4.5 Devices & Data Quality — the catalogue + an honest audit

Makes the dataset's structure and its quirks transparent rather than hiding
them.

**What you can see/do:**
- **Summary tiles** — how many devices are registered, how many actually have
  data, how many are registered but never logged, and how many are
  external/specialty sources.
- **Data availability timeline** — a Gantt-style bar per sensor showing its
  first→last reading. A device with no data simply has no bar.
- **Device catalogue** — a sortable table: device name, type, data "shape",
  city, MAC, whether a data table exists, row count, and first/last reading.
- **Known data-quality issues** — a count of the saturation readings excluded
  from every chart (per sensor), plus a plain-language list of the handled
  quirks: saturation ceilings, swapped coordinates (corrected), duplicate
  rows (de-duplicated), empty/registered-only devices, the µg/m³ vs "ppm"
  unit correction, and the performance index added for time queries.
- **Edit device metadata** — update a device's **name, description, icon, and
  "data capture" flag** (descriptive fields only; measurement data is never
  editable). Saved in one transaction, with confirmation.

---

### 4.6 Manage — optional features & saved items

A small admin surface. Everything here is reversible and confirms its result.

**What you can do:**
- **Optional modules** — toggle the Time Series add-ons on/off
  (**Annotations**, **Raw readings & flags**, **Particle-size drill-down**).
  Changes take effect immediately. A separate expander lists legacy
  system flags for completeness.
- **Saved thresholds** — add a reference threshold for a measure (value +
  optional label); these become the default reference lines on Time Series.
  List and delete existing ones.
- **Saved views** — the named views you saved on Time Series. **Apply**
  re-opens Time Series with that exact sensor/measures/range/bucket; or
  **Delete** a view.

> Some features here (thresholds, saved views, annotations, flags) depend on
> an optional database setup. If it isn't present, the page tells you plainly
> and the **feature-flag toggles still work**.

---

## 5. Common tasks — "how do I…?"

| I want to… | Go here | Do this |
|------------|---------|---------|
| See if the air is OK right now at a sensor | **Dashboard** | Pick the device — read the status sentence at the top. |
| Look at a mobile sensor's trips | **Dashboard** | Pick a **Mobile** device → the route map; use the **Routes** tab to split/inspect trips. |
| Study one sensor's PM over a month | **Time Series** | Pick the sensor, set range to **30 d**, choose PM2.5/PM10; drag to zoom. |
| Compare average PM across sensors | **Comparison** | Select the sensors, pick the measure, read the **Averages** tab. |
| Check whether two measures relate | **Dashboard → Correlation tab** | Pick 2+ measures; read the colour-coded verdict, then the chart. |
| Export the data I'm looking at | **Time Series** or **Comparison** or **Dashboard → Measures** | Use the **Download … (CSV)** button. |
| Save a view to return to later | **Time Series** | **Save this view** → re-open it from **Manage → Saved views**. |
| Share my exact view | **Dashboard / Time Series** | Copy the page **URL** (it captures your selection). |
| Fix a wrong sensor address/position | **Map → Edit a location** | Update the fields/coordinates → **Save**. |
| Mark or question a reading | **Time Series → Raw readings & flags** | Flag a reading id as suspect/confirmed/ignore. |
| Understand the data's quirks | **Devices & Data Quality** | Read the **Known data-quality issues** section. |
| Turn an optional feature on/off | **Manage** | Toggle it under **Optional modules**. |

---

## 6. What the messages mean

- **"… readings … were hidden"** — saturation/"stuck at max" values were
  excluded from this view so they don't distort it; the count is shown for
  honesty.
- **"No readings in the selected range"** / **"No routes … in the selected
  range"** — widen the time range (try **All**) or use **Reset**.
- **"Pick at least two measures…"** — the correlation view needs two or more
  measures.
- **"computed"** next to CAQI — that band is derived from PM, not a measured
  value.
- **"The dashboard can't reach its database"** — a connection problem (not
  something you did); the technical detail is in an expander. The data needs
  its database running.
- **Loading spinners** ("Loading time series…", "Segmenting routes…") — the
  app is fetching/preparing data; large ranges take a moment.

---

## 7. Accessibility & tips

- **Colour-blind safe** throughout; colour is always backed by a label,
  icon, or number.
- **Keyboard**: the app is operable by keyboard; charts and maps also support
  mouse/touch.
- **Touch-friendly** targets and spacing.
- **Reset is always reachable** — you can never get trapped in a filter.
- **Dark mode** follows your system/Streamlit theme setting.
- If a view looks empty, it's almost always the **time range** — switch to
  **All** or hit **Reset**.
