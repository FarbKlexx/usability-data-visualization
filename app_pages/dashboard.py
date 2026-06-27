"""Dashboard — the adaptive monitoring cockpit (IA redesign, 2nd pass).

The hub answers "how is the air, for *this* device?" at a glance, in a
fixed top-to-bottom hierarchy that clears a laptop fold without scrolling:

* **Zone 0 — toolbar** (Fitts: screen edge): the type-grouped device
  picker + time range + Reset, echoed as chips.
* **Zone 1 — hero card** (the single focal point, Mental Models top-left):
  one ``st.subheader`` stating the plain-language CAQI verdict, above a
  red→green air-quality meter.
* **Zone 2 — KPI strip** (Miller ≤7, lifted above the fold): the headline
  measures, in source order *before* any chart.
* **Zone 3 — bento** (Split-Attention, asymmetry = hierarchy): a wide
  ``[2,1]`` row — the PM trend (or route map) leads, a near-square
  location map / trip stats sits beside it (no full-width letterbox map).
* for **mobile** devices only, a **Routes** section (trip split control,
  trip list, per-route PM). *Compare* and *Correlation* are now their own
  top-level pages, not tabs here.

Operating hints live in tooltips, not standing prose; only honest-data
disclosures (hidden sentinels, "CAQI computed") stay on screen.
"""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src.components import charts, filter_bar, skeleton
from src.components.kpi import metric_tile
from src.components.meter import air_quality_meter
from src.data import (
    load_devices,
    load_locations,
    load_range_summary,
    load_raw_readings,
    load_routes,
    load_timeseries,
)
from src.utils.aqi import caqi_band, caqi_index
from src.utils.clean import clean_frame, hidden_notice
from src.utils.metrics import HEADLINE_KPIS, get
from src.utils.state import publish_query_params, seed_session_defaults

_PLOT = {"theme": "streamlit", "width": "stretch", "config": {"displaylogo": False}}
_MAP_PLOT = {"theme": "streamlit", "width": "stretch", "config": {"scrollZoom": True, "displaylogo": False}}
# Operating hints that used to be standing captions — now tooltips (no prose).
_ZOOM_HELP = "Drag to zoom · double-click to reset · click a legend entry to toggle a series."
_ROUTEMAP_HELP = "Drag to pan · scroll to zoom · points coloured by PM2.5 (Viridis) · pick a trip in the Routes section below."


# "Full map" opens a larger map in a modal overlay (there is no separate Map
# page anymore): the stationary device's location point, or the mobile device's
# routes, drawn into a big interactive map.
@st.dialog("Location", width="large")
def _location_overlay(loc_df: pd.DataFrame) -> None:
    st.plotly_chart(
        charts.map_figure(charts.build_location_markers(loc_df), height=600, show_text=True),
        key="ov_locmap_overlay", **_MAP_PLOT,
    )


@st.dialog("Routes travelled", width="large")
def _routes_overlay(routes_df: pd.DataFrame) -> None:
    st.plotly_chart(
        charts.route_map(routes_df, height=600, show_points=False),
        key="ov_routemap_overlay", **_MAP_PLOT,
    )

st.title(":material/dashboard: Dashboard")

devices = load_devices()
pool = devices[devices["has_data"]]  # every data-bearing device (plan §A)

# Restore a shared view from the URL before any widget binds (bookmarkable).
seed_session_defaults({"ov_sensors": str, "ov_range": str})
_valid_tables = set(pool["table_name"].dropna())
if st.session_state.get("ov_sensors") not in _valid_tables:
    st.session_state.pop("ov_sensors", None)

# === ZONE 0: unified, type-grouped device picker (toolbar at the edge) =======
fs = filter_bar(
    devices, prefix="ov", multi=False, pool=pool, group_by_type=True,
    default_tables=["sensor_000aeb8337ac"], default_range="7 d",
)
if fs.is_empty:
    st.stop()
table = fs.tables[0]
drow = devices[devices["table_name"] == table].iloc[0]
is_mobile = bool(drow["is_mobile"])

# Snapshot for the hero, the KPI strip and the CAQI verdict. Everything here
# is the **mean over the selected range** (so the tiles change with the time
# range), with the trend measured against the previous equal-length period.
# The hero + the KPI strip share this one query, so we paint a content-shaped
# skeleton in both slots *before* it runs and swap the values in afterwards —
# the layout never jumps and the wait reads as "loading", not "broken".
avg_label = "full-record average" if fs.range_key == "All" else f"{fs.range_key} average"

# === ZONE 1: hero card — names the device + states the verdict (focal point) =
hero_ph = st.empty()
with hero_ph.container(border=True, key="box_hero_skel"):
    skeleton.hero()

# === ZONE 2: KPI strip — lifted above the fold (was hidden in a tab) =========
# The trend-baseline label can only be written *after* the query: if the
# immediately-preceding window was a gap, the delta falls back to the most
# recent window that had data, and the caption must say so — hence its own
# placeholder rather than a caption rendered up front.
cap_ph = st.empty()
strip_ph = st.empty()
with strip_ph.container():
    skeleton.tiles(len(HEADLINE_KPIS))  # one per headline measure

summary_df, latest_ts, baseline_end = load_range_summary(table, fs.start, fs.end)
vals = {r.metric: (r.value, r.delta) for r in summary_df.itertuples()}
band = caqi_band(vals.get("pm2_5", (None,))[0], vals.get("pm10_0", (None,))[0])

# Name the trend baseline honestly: normally "previous 7 d"; when the immediate
# prior window held no data, "previous 7 d with data (to <date>)".
if fs.range_key == "All":
    prev_label = None
elif baseline_end is not None:
    prev_label = f"previous {fs.range_key} with data (to {baseline_end:%b %d})"
else:
    prev_label = f"previous {fs.range_key}"
strip_cap = f":material/schedule: {avg_label[:1].upper()}{avg_label[1:]}"
if prev_label:
    strip_cap += f" · trend vs. {prev_label}"
# Render as a grey badge (not a plain caption) to match the time-window badge
# under the filter bar.
cap_ph.markdown(f":gray-badge[{strip_cap}]")

with hero_ph.container(border=True, key="box_hero"):
    # The hero is just the verdict word + a red→green meter now: the device name
    # is already in the picker above, the dominant-PM number duplicated the KPI
    # strip below, and the CAQI badge + advice line restated the verdict. The
    # provenance/window line (formerly a caption) is folded into the heading's
    # tooltip. The meter's marker position carries the value spatially, so the
    # word + position + hue triple-encode it (colour never the only channel).
    if band is None:
        st.subheader(":material/help: Air quality: no reading in range")
        st.caption("No usable PM2.5/PM10 reading in the selected range.")
    else:
        meta = f"CAQI from PM2.5/PM10 · {avg_label}"
        if latest_ts is not None:
            meta += f" · through {latest_ts:%Y-%m-%d %H:%M}"
        st.subheader(f"{band.icon} Air quality: {band.quality}", help=meta)
        idx = caqi_index(vals.get("pm2_5", (None,))[0], vals.get("pm10_0", (None,))[0])
        if idx is not None:
            # idx: 0 cleanest .. 100 worst → marker position 1 (green/right) .. 0 (red/left).
            air_quality_meter(1.0 - min(idx, 100.0) / 100.0, band.color)

# Equal-width tiles: st.columns splits the row evenly, so every KPI card is the
# same width (a horizontal container would size each to its own content).
strip_keys = [k for k in HEADLINE_KPIS if k in vals]
with strip_ph.container():
    for col, key in zip(st.columns(len(strip_keys) or 1), strip_keys):
        with col:
            metric_tile(
                key, *vals.get(key, (None, None)),
                value_desc=avg_label, baseline_label=prev_label or "previous period",
            )

# === ZONE 3: bento — primary visual beside its spatial/trip context ==========
# Each cell shows a chart/map/stat-shaped skeleton while its loader runs. Both
# cells of the row are skeletoned *before* either query runs, so the whole
# bento reads as "loading" at once rather than one cell at a time, then each
# swaps to real content as its data arrives. Static chrome (the box + its
# title) renders immediately — only the data area waits.
routes = pd.DataFrame()  # populated for mobile; referenced again in the Routes tab
cL, cR = st.columns([2, 1], gap="small", vertical_alignment="top")
if is_mobile:
    gap_seconds = 3600  # hardcoded: start a new trip after a 1 h gap
    with cL:
        with st.container(border=True, key="box_routemap"):
            rt_title, rt_action = st.columns([1, 1], vertical_alignment="center")
            rt_title.markdown("**:material/route: Routes travelled**", help=_ROUTEMAP_HELP)
            with rt_action.container(horizontal=True, horizontal_alignment="right"):
                open_routemap = st.button("Full map", icon=":material/open_in_full:", key="ov_fullmap_route")
            routemap_ph = st.empty()
            with routemap_ph.container():
                skeleton.block(420)
    with cR:
        with st.container(border=True, key="box_tripstats"):
            st.markdown("**:material/insights: This window**")
            tripstats_ph = st.empty()
            with tripstats_ph.container():
                skeleton.tiles_stack(3)
    # Both skeletons painted; run the (shared) query and swap both cells in.
    routes = load_routes(table, gap_seconds=gap_seconds, start=fs.start, end=fs.end)
    with routemap_ph.container():
        if routes.empty:
            st.info(
                "No routes in the selected range — widen the time range (Reset, or try All).",
                icon=":material/info:",
            )
        else:
            route_ids = [int(r) for r in sorted(routes["route_id"].unique())]
            # Clicking opens the trip's detail page. We use Streamlit's plotly
            # selection (server-side → st.switch_page) because the alternative —
            # navigating from the hover iframe — is blocked (the components iframe
            # is sandboxed without top-navigation). Selection only fires for
            # marker/point clicks, which is why the route line carries markers.
            map_event = st.plotly_chart(
                charts.route_map(routes, height=420, clickable=True, show_points=False),
                on_select="rerun", selection_mode="points", key="ov_routemap_sel", **_MAP_PLOT,
            )
            st.caption(
                f":material/route: {len(route_ids)} trip(s) · click a route to open it."
            )
            route_id_set = set(route_ids)
            picked = (map_event.selection or {}).get("points", []) if map_event else []
            if picked:
                p0 = picked[0]
                cd = p0.get("customdata")
                if isinstance(cd, dict):  # some builds key customdata by index
                    cd = [cd[k] for k in sorted(cd, key=lambda x: int(x))]
                if isinstance(cd, (list, tuple)) and cd:
                    last = cd[-1]
                elif isinstance(cd, (int, float)):
                    last = cd
                else:
                    last = None
                rid: int | None = None
                try:
                    rid = int(last) if last is not None else None
                except (TypeError, ValueError):
                    rid = None
                # Guard with a signature so navigating back (which restores the
                # selection) doesn't immediately re-fire the page switch.
                sig = (rid, p0.get("point_number"), p0.get("curve_number"))
                if rid in route_id_set and st.session_state.get("ov_routemap_nav") != sig:
                    st.session_state["ov_routemap_nav"] = sig
                    st.switch_page(
                        "app_pages/route.py",
                        query_params={
                            "route_table": table,
                            "route_id": str(rid),
                            "route_gap": str(gap_seconds),
                            "route_start": fs.start.isoformat(),
                            "route_end": fs.end.isoformat(),
                        },
                    )
    with tripstats_ph.container():
        if routes.empty:
            st.caption("No trips in range.")
        else:
            mean_pm = routes["pm2_5"].mean()
            st.metric("Trips", int(routes["route_id"].nunique()), border=True)
            st.metric("GPS points", f"{len(routes):,}", border=True)
            st.metric(
                "Mean PM2.5", "–" if pd.isna(mean_pm) else f"{mean_pm:.1f} µg/m³",
                border=True, help="Mean PM2.5 across all points in the selected range.",
            )
    if open_routemap and not routes.empty:
        _routes_overlay(routes)
else:
    with cL:
        with st.container(border=True, key="box_pmtrend"):
            st.markdown("**:material/timeline: Particulate matter over time**", help=_ZOOM_HELP)
            pmtrend_ph = st.empty()
            with pmtrend_ph.container():
                skeleton.block(320)
    with cR:
        with st.container(border=True, key="box_locmap"):
            loc_title, loc_action = st.columns([1, 1], vertical_alignment="center")
            loc_title.markdown("**:material/location_on: Location**")
            with loc_action.container(horizontal=True, horizontal_alignment="right"):
                open_locmap = st.button("Full map", icon=":material/open_in_full:", key="ov_fullmap_loc")
            locmap_ph = st.empty()
            with locmap_ph.container():
                skeleton.block(320)
    # Both skeletons painted; load each cell and swap it in.
    ts_df, ts_hidden, _ = load_timeseries(table, ("pm2_5", "pm10_0"), fs.start, fs.end)
    with pmtrend_ph.container():
        st.plotly_chart(charts.line_chart(ts_df, ("pm2_5", "pm10_0"), height=320), **_PLOT)
        if (notice := hidden_notice(ts_hidden)):
            st.caption(f":material/visibility_off: {notice}")
    loc_one = load_locations()
    loc_one = loc_one[
        (loc_one["table_name"] == table) & loc_one["lon"].notna() & loc_one["lat"].notna()
    ]
    with locmap_ph.container():
        if loc_one.empty:
            st.caption(":material/location_off: No location recorded for this sensor.")
        else:
            st.plotly_chart(
                charts.map_figure(charts.build_location_markers(loc_one), height=320, show_text=True),
                **_MAP_PLOT,
            )
    if open_locmap and not loc_one.empty:
        _location_overlay(loc_one)

# === SECONDARY: the device's spatial/temporal entries ========================
# Mobile → the trips it made (clickable → the Route detail page). Stationary →
# the individual readings it logged in range (most-recent-first, load-more).
if is_mobile:
    st.subheader(":material/route: Routes")
    gap_seconds = 3600  # hardcoded: start a new trip after a 1 h gap
    if routes.empty:
        st.info("No routes in the selected range — widen the time range above.", icon=":material/info:")
    else:
        summary = (
            routes.groupby("route_id")
            .agg(points=("ts", "size"), start=("ts", "min"), end=("ts", "max"), mean_pm=("pm2_5", "mean"))
            .reset_index()
            .sort_values("start")
        )
        st.caption("Pick a trip to open its details.")
        # One card per trip: the trip's facts on the left, a small "Open" button
        # on the right (a list of cards, not a stack of full-width buttons; and
        # not a selectable dataframe, whose selection would persist in
        # session_state and re-fire the page switch on every navigate-back).
        for r in summary.itertuples():
            rid = int(r.route_id)
            dur_h = (r.end - r.start).total_seconds() / 3600
            pm = "no PM" if pd.isna(r.mean_pm) else f"mean PM2.5 {r.mean_pm:.1f}"
            with st.container(border=True, key=f"box_route_{rid}"):
                info_c, open_c = st.columns([0.8, 0.2], vertical_alignment="center")
                info_c.markdown(
                    f"**:material/route: Route {rid + 1}** · {r.start:%b %d, %H:%M}–{r.end:%H:%M}  \n"
                    f":gray-badge[{r.points:,} points] :gray-badge[{dur_h:.1f} h] :gray-badge[{pm}]"
                )
                if open_c.button("Open", icon=":material/open_in_new:", key=f"ov_route_btn_{rid}", width="stretch"):
                    st.switch_page(
                        "app_pages/route.py",
                        query_params={
                            "route_table": table,
                            "route_id": str(rid),
                            "route_gap": str(gap_seconds),
                            "route_start": fs.start.isoformat(),
                            "route_end": fs.end.isoformat(),
                        },
                    )
else:
    with st.container(border=True, key="box_points"):
        st.markdown(
            "**:material/list_alt: Recent readings**",
            help="The sensor's individual readings in the selected range, newest first. "
                 "Saturation sentinels are blanked (shown as empty cells), never silently kept.",
        )
        n_show = int(st.session_state.get("ov_points_n", 25))
        raw = load_raw_readings(table, fs.start, fs.end, limit=n_show)
        if raw.empty:
            st.caption("No readings for this sensor in the selected range.")
        else:
            cleaned, _ = clean_frame(raw)
            measures = [k for k in HEADLINE_KPIS if k in cleaned.columns]
            disp = cleaned[["ts", *measures]].copy()
            pm25 = cleaned["pm2_5"] if "pm2_5" in cleaned.columns else None
            pm10 = cleaned["pm10_0"] if "pm10_0" in cleaned.columns else None
            if pm25 is not None or pm10 is not None:
                p25 = pm25.tolist() if pm25 is not None else [None] * len(disp)
                p10 = pm10.tolist() if pm10 is not None else [None] * len(disp)
                disp["air_quality"] = [
                    (caqi_band(a, b).quality if caqi_band(a, b) else "—") for a, b in zip(p25, p10)
                ]
            col_cfg: dict = {"ts": st.column_config.DatetimeColumn("Time", format="YYYY-MM-DD HH:mm")}
            for k in measures:
                m = get(k)
                col_cfg[k] = st.column_config.NumberColumn(
                    m.short_label, format=f"%.{m.decimals}f", help=f"{m.label} ({m.unit})"
                )
            if "air_quality" in disp.columns:
                col_cfg["air_quality"] = st.column_config.TextColumn("Air quality", help="Computed CAQI band.")
            st.dataframe(disp, hide_index=True, width="stretch", column_config=col_cfg)
            st.caption(f":material/list_alt: Showing the {len(raw):,} most recent readings.")
            if len(raw) == n_show:  # a full page came back → there are probably more
                if st.button("Load more", icon=":material/expand_more:", key="ov_points_more"):
                    st.session_state["ov_points_n"] = n_show + 25
                    st.rerun()

# Route-map hover affordance (mobile only). Hovering a trip tints its convex-hull
# polygon (the "area that encapsulates the route") and shows a centre label, and
# the cursor turns to a pointer. Performance: a *single* reusable polygon + label
# trace (`activehull`/`activelabel`) is repointed to the hovered trip from the
# precomputed `HULLS` data — far lighter than one trace per trip — and only on a
# *route change*, so moving along one trip never re-renders. (MapLibre/Scattermap
# can't make a polygon interior a hover target, so the route line is the trigger.)
# Streamlit exposes no Plotly-hover hook, so a 0-height same-origin iframe binds
# the events on the graph div (same escape hatch as the sticky-bar watcher); the
# restyle needs the page's global Plotly and degrades silently if absent.
if is_mobile and not routes.empty:
    _hull_js = """
        <script>
        (function () {
          const HULLS = __HULLS__;
          const doc = window.parent.document;
          function P() { return window.parent.Plotly; }
          let boundGd = null;
          function bind() {
            const box = doc.querySelector('.st-key-box_routemap');
            if (!box) return;
            const gd = box.querySelector('.js-plotly-plot');
            if (!gd || gd === boundGd) return;   // this gd already bound by THIS run
            boundGd = gd;
            // Streamlit may reuse the same graph div across reruns (e.g. changing
            // the time range), so a previous run's hover listeners — closing over
            // STALE hull data — can linger. Drop them and rebind with fresh HULLS.
            // (Streamlit drives selection via plotly_click, not hover, so removing
            // hover listeners is safe.)
            if (gd.removeAllListeners) {
              gd.removeAllListeners('plotly_hover');
              gd.removeAllListeners('plotly_unhover');
            }
            const canvasC = box.querySelector('.maplibregl-canvas-container');
            const data = gd.data || [];
            let hullI = -1; const lineIdx = [];
            data.forEach(function (t, i) {
              if (t.meta === 'activehull') hullI = i;
              else if (t.mode && String(t.mode).indexOf('lines') >= 0) lineIdx.push(i);
            });
            // A real (styled) tooltip: an HTML div over the map, positioned at the
            // trip centroid via MapLibre's projection (fallback: map centre).
            const mapEl = box.querySelector('.maplibregl-map') || canvasC;
            let tip = box.querySelector('.aq-route-tip');
            if (!tip) {
              tip = doc.createElement('div');
              tip.className = 'aq-route-tip';
              tip.style.cssText = 'position:absolute;z-index:6;pointer-events:none;'
                + 'transform:translate(-50%,-130%);background:rgba(28,33,40,0.94);color:#fff;'
                + 'padding:5px 9px;border-radius:7px;font-size:12px;line-height:1.3;font-weight:600;'
                + 'white-space:nowrap;box-shadow:0 2px 8px rgba(16,24,40,0.35);opacity:0;'
                + 'transition:opacity .12s ease;';
              if (mapEl) { mapEl.appendChild(tip); }
            }
            function mlMap() {
              try { return gd._fullLayout.map._subplot.map; } catch (e) { return null; }
            }
            function placeTip(h) {
              const m = mlMap();
              let x, y;
              if (m && m.project) { const pt = m.project([h.clon, h.clat]); x = pt.x; y = pt.y; }
              else if (mapEl) { x = mapEl.clientWidth / 2; y = mapEl.clientHeight / 2; }
              if (x != null) { tip.style.left = x + 'px'; tip.style.top = y + 'px'; }
              tip.innerHTML = h.text
                + "<br><span style='opacity:.75;font-weight:400'>Click to open</span>";
              tip.style.opacity = '1';
            }
            function routeOf(p) {
              const cd = p.customdata;
              if (cd != null) {
                let v = Array.isArray(cd) ? cd[cd.length - 1] : null;
                if (v == null && typeof cd === 'object') { const ks = Object.keys(cd); v = cd[ks[ks.length - 1]]; }
                if (v != null) return parseInt(v);
              }
              if (lineIdx.indexOf(p.curveNumber) >= 0) return lineIdx.indexOf(p.curveNumber);
              return null;
            }
            let lastRid = null, clearTimer = null;
            function emphasize(rid) {
              const Plotly = P(); const h = HULLS[rid];
              if (!Plotly || !h || rid === lastRid) return;   // same trip → no re-render
              if (hullI >= 0) Plotly.restyle(gd, {lat: [h.lat], lon: [h.lon], fillcolor: ['rgba(213,94,0,0.22)']}, [hullI]);
              placeTip(h);
              lastRid = rid;
            }
            function clearEmph() {
              const Plotly = P();
              if (tip) tip.style.opacity = '0';
              if (!Plotly || lastRid === null) return;
              if (hullI >= 0) Plotly.restyle(gd, {fillcolor: ['rgba(213,94,0,0)']}, [hullI]);
              lastRid = null;
            }
            gd.on('plotly_hover', function (e) {
              const p = e.points && e.points[0];
              if (!p) return;
              if (clearTimer) { clearTimeout(clearTimer); clearTimer = null; }
              const rid = routeOf(p);
              if (rid == null) return;
              if (canvasC) canvasC.style.cursor = 'pointer';
              emphasize(rid);
            });
            gd.on('plotly_unhover', function () {
              if (canvasC) canvasC.style.cursor = '';
              if (clearTimer) clearTimeout(clearTimer);
              clearTimer = setTimeout(clearEmph, 150);   // debounce: ignore brief gaps
            });
            // (Click → navigation is handled server-side via st.plotly_chart's
            // selection; the iframe can't navigate the parent — it's sandboxed.)
          }
          bind();
          // Re-bind across Streamlit reruns (a new graph div replaces the old).
          new MutationObserver(bind).observe(doc.body, {childList: true, subtree: true});
        })();
        </script>
    """
    components.html(_hull_js.replace("__HULLS__", json.dumps(charts.route_hulls(routes))), height=0)

# Publish the current view to the URL (shareable/bookmarkable).
publish_query_params({"ov_sensors": table, "ov_range": fs.range_key})

# NOTE: the sticky-filter-bar watcher (and the scroll-condense header title) now
# lives GLOBALLY in app.py, not here — it has to run on every page so it can
# hide the header title when this bar is absent. See app.py's trailing
# components.html block.
