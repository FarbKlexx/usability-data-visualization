"""Dashboard — the adaptive monitoring cockpit (IA redesign, 2nd pass).

The hub answers "how is the air, for *this* device?" at a glance, in a
fixed top-to-bottom hierarchy that clears a laptop fold without scrolling:

* **Zone 0 — toolbar** (Fitts: screen edge): the type-grouped device
  picker + time range + Reset, echoed as chips.
* **Zone 1 — hero card** (the single focal point, Mental Models top-left):
  one ``st.subheader`` that *names the active device* and states the
  plain-language CAQI verdict, paired with the dominant-pollutant number.
* **Zone 2 — KPI strip** (Miller ≤7, lifted above the fold): the headline
  measures + the computed-CAQI tile, in source order *before* any chart.
* **Zone 3 — bento** (Split-Attention, asymmetry = hierarchy): a wide
  ``[2,1]`` row — the PM trend (or route map) leads, a near-square
  location map / trip stats sits beside it (no full-width letterbox map).
* one ``st.divider`` → **slim tabs** (Hick, progressive disclosure):
  *Compare* (folded-in multi-sensor comparison), *Correlation*, and, for
  mobile, *Routes*.

Operating hints live in tooltips, not standing prose; only honest-data
disclosures (hidden sentinels, "CAQI computed") stay on screen.
"""

from __future__ import annotations

import itertools

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from app_pages.comparison import render_compare
from src.components import charts, filter_bar, skeleton
from src.components.filter_bar import device_label
from src.components.kpi import aqi_tile, metric_tile
from src.data import (
    available_metrics,
    build_comparison_frame,
    load_devices,
    load_locations,
    load_range_summary,
    load_routes,
    load_timeseries,
)
from src.utils.aqi import COMPUTED_NOTE, caqi_band
from src.utils.clean import hidden_notice
from src.utils.correlate import compute_correlation, correlation_verdict, normalize_frame
from src.utils.metrics import HEADLINE_KPIS, get
from src.utils.state import csv_split, hand_off_to_timeseries, publish_query_params, seed_session_defaults

# CAQI level → Streamlit badge colour (icon + word carry the meaning; the
# colour only reinforces it — never colour alone).
_BAND_BADGE = {0: "green", 1: "blue", 2: "orange", 3: "red", 4: "violet"}
# Route split-gap presets (label → seconds); default 1 h (plan locked decision).
_GAP_PRESETS = {"15 min": 900, "30 min": 1800, "1 hour": 3600, "2 hours": 7200, "6 hours": 21600}
_PLOT = {"theme": "streamlit", "width": "stretch", "config": {"displaylogo": False}}
_MAP_PLOT = {"theme": "streamlit", "width": "stretch", "config": {"scrollZoom": True, "displaylogo": False}}
# Operating hints that used to be standing captions — now tooltips (no prose).
_ZOOM_HELP = "Drag to zoom · double-click to reset · click a legend entry to toggle a series."
_ROUTEMAP_HELP = "Drag to pan · scroll to zoom · points coloured by PM2.5 (Viridis) · pick a trip in the Routes tab."

st.title(":material/dashboard: Dashboard")

devices = load_devices()
pool = devices[devices["has_data"]]  # every data-bearing device (plan §A)

# Restore a shared view from the URL before any widget binds (bookmarkable).
seed_session_defaults({"ov_sensors": str, "ov_range": str, "ov_corr": csv_split})
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
device_name = device_label(drow)  # clean "name · city", no type prefix

# Snapshot for the hero, the KPI strip and the CAQI verdict. Everything here
# is the **mean over the selected range** (so the tiles change with the time
# range), with the trend measured against the previous equal-length period.
# The hero + the KPI strip share this one query, so we paint a content-shaped
# skeleton in both slots *before* it runs and swap the values in afterwards —
# the layout never jumps and the wait reads as "loading", not "broken".
avg_label = "full-record average" if fs.range_key == "All" else f"{fs.range_key} average"
prev_label = None if fs.range_key == "All" else f"previous {fs.range_key}"

# === ZONE 1: hero card — names the device + states the verdict (focal point) =
hero_ph = st.empty()
with hero_ph.container(border=True, key="box_hero_skel"):
    skeleton.hero()

# === ZONE 2: KPI strip — lifted above the fold (was hidden in a tab) =========
strip_cap = f":material/schedule: {avg_label[:1].upper()}{avg_label[1:]}"
if prev_label:
    strip_cap += f" · trend vs. {prev_label}"
st.caption(strip_cap)
strip_ph = st.empty()
with strip_ph.container():
    skeleton.tiles(len(HEADLINE_KPIS) + 1)  # headline measures + the CAQI tile

summary_df, latest_ts = load_range_summary(table, fs.start, fs.end)
vals = {r.metric: (r.value, r.delta) for r in summary_df.itertuples()}
band = caqi_band(vals.get("pm2_5", (None,))[0], vals.get("pm10_0", (None,))[0])

with hero_ph.container(border=True, key="box_hero"):
    hL, hR = st.columns([0.62, 0.38], gap="medium", vertical_alignment="center")
    with hL:
        if band is None:
            st.subheader(f":material/help: {device_name} — air quality: no reading in range")
            st.caption("No usable PM2.5/PM10 reading in the selected range.")
        else:
            st.subheader(f"{band.icon} {device_name} — air quality: {band.quality}")
            st.markdown(f":{_BAND_BADGE.get(band.level, 'gray')}-badge[CAQI: {band.label}] &nbsp; {band.advice}")
            meta = f"CAQI from PM2.5/PM10 · {avg_label}"
            if latest_ts is not None:
                meta += f" · through {latest_ts:%Y-%m-%d %H:%M}"
            st.caption(meta, help=COMPUTED_NOTE)
    with hR:
        # Dominant-pollutant headline number paired with the verdict (IQAir pattern).
        dom_key = "pm2_5" if vals.get("pm2_5", (None,))[0] is not None else "pm10_0"
        if vals.get(dom_key, (None,))[0] is not None:
            metric_tile(
                dom_key, *vals.get(dom_key, (None, None)),
                value_desc=avg_label, baseline_label=prev_label or "previous period",
            )

with strip_ph.container(horizontal=True):
    for key in (k for k in HEADLINE_KPIS if k in vals):
        metric_tile(
            key, *vals.get(key, (None, None)),
            value_desc=avg_label, baseline_label=prev_label or "previous period",
        )
    aqi_tile(band)

# === ZONE 3: bento — primary visual beside its spatial/trip context ==========
# Each cell shows a chart/map/stat-shaped skeleton while its loader runs. Both
# cells of the row are skeletoned *before* either query runs, so the whole
# bento reads as "loading" at once rather than one cell at a time, then each
# swaps to real content as its data arrives. Static chrome (the box + its
# title + the hand-off button) renders immediately — only the data area waits.
routes = pd.DataFrame()  # populated for mobile; referenced again in the Routes tab
cL, cR = st.columns([2, 1], gap="medium", vertical_alignment="top")
if is_mobile:
    gap_seconds = int(st.session_state.get("ov_route_gap", 3600))
    with cL:
        with st.container(border=True, key="box_routemap"):
            st.markdown("**:material/route: Routes travelled**", help=_ROUTEMAP_HELP)
            routemap_ph = st.empty()
            with routemap_ph.container():
                skeleton.block(420)
            st.button(
                "Open in Time Series", icon=":material/open_in_full:",
                on_click=hand_off_to_timeseries, args=(table,),
                help="Full depth: aggregation bucket, rolling average, thresholds, annotations, flags.",
            )
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
            sel = st.session_state.get("ov_route_sel")
            selected_route = sel if isinstance(sel, int) and sel in route_ids else None
            st.plotly_chart(charts.route_map(routes, selected_route=selected_route, height=420), **_MAP_PLOT)
            scope = "all routes" if selected_route is None else f"route {selected_route + 1}"
            st.caption(f":material/route: {len(route_ids)} trip(s), {len(routes):,} points (showing {scope}).")
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
else:
    with cL:
        with st.container(border=True, key="box_pmtrend"):
            st.markdown("**:material/timeline: Particulate matter over time**", help=_ZOOM_HELP)
            pmtrend_ph = st.empty()
            with pmtrend_ph.container():
                skeleton.block(320)
            st.button(
                "Open in Time Series", icon=":material/open_in_full:",
                on_click=hand_off_to_timeseries, args=(table,),
                help="Full depth: aggregation bucket, rolling average, thresholds, annotations, flags.",
            )
    with cR:
        with st.container(border=True, key="box_locmap"):
            st.markdown("**:material/location_on: Location**")
            locmap_ph = st.empty()
            with locmap_ph.container():
                skeleton.block(320)
            st.page_link("app_pages/map.py", label="Full map", icon=":material/open_in_full:")
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

st.divider()

# === SECONDARY: tabs (progressive disclosure, Hick) =========================
tab_keys = (["routes", "compare", "correlation"] if is_mobile else ["compare", "correlation"])
tab_titles = (
    [":material/route: Routes", ":material/compare_arrows: Compare", ":material/scatter_plot: Correlation"]
    if is_mobile
    else [":material/compare_arrows: Compare", ":material/scatter_plot: Correlation"]
)
tabs = dict(zip(tab_keys, st.tabs(tab_titles)))

# --- Routes tab (mobile only): split control, trip list, per-route PM chart --
if is_mobile:
    with tabs["routes"]:
        st.select_slider(
            "Start a new trip when the gap exceeds", options=list(_GAP_PRESETS.values()),
            value=3600, key="ov_route_gap", format_func=lambda s: {v: k for k, v in _GAP_PRESETS.items()}[s],
            help="Larger gaps merge stops into one trip; smaller gaps split more aggressively.",
        )
        if routes.empty:
            st.info("No routes in the selected range — widen the time range above.", icon=":material/info:")
        else:
            route_ids = [int(r) for r in sorted(routes["route_id"].unique())]
            if st.session_state.get("ov_route_sel") not in route_ids:
                st.session_state.pop("ov_route_sel", None)
            st.selectbox(
                "Inspect a trip", options=[None] + route_ids, key="ov_route_sel",
                format_func=lambda v: "All routes (map only)" if v is None else f"Route {v + 1}",
                help="Highlights the trip on the map above and charts its PM2.5 over time.",
            )
            summary = (
                routes.groupby("route_id")
                .agg(points=("ts", "size"), start=("ts", "min"), end=("ts", "max"), mean_pm=("pm2_5", "mean"))
                .reset_index()
            )
            summary["duration"] = (summary["end"] - summary["start"]).dt.total_seconds() / 3600
            summary["Route"] = summary["route_id"] + 1
            st.dataframe(
                summary[["Route", "points", "start", "end", "duration", "mean_pm"]],
                hide_index=True, width="stretch",
                column_config={
                    "points": st.column_config.NumberColumn("Points", format="%d"),
                    "start": st.column_config.DatetimeColumn("Start", format="YYYY-MM-DD HH:mm"),
                    "end": st.column_config.DatetimeColumn("End", format="YYYY-MM-DD HH:mm"),
                    "duration": st.column_config.NumberColumn("Hours", format="%.1f"),
                    "mean_pm": st.column_config.NumberColumn("Mean PM2.5", format="%.1f"),
                },
            )
            chosen = st.session_state.get("ov_route_sel")
            if isinstance(chosen, int) and chosen in route_ids:
                rdf = routes[routes["route_id"] == chosen][["ts", "pm2_5"]]
                st.markdown(f"**PM2.5 along Route {chosen + 1}**", help=_ZOOM_HELP)
                st.plotly_chart(charts.line_chart(rdf, ("pm2_5",), height=260), **_PLOT)
            else:
                st.caption("Pick a trip above to see its PM2.5 over time.")

# --- Compare tab (all devices): folded-in multi-sensor comparison -----------
with tabs["compare"]:
    render_compare()

# --- Correlation tab (all devices): verdict-first, replace-in-place ---------
with tabs["correlation"]:
    options = [m.key for m, _ in available_metrics(table)]
    default_corr = [k for k in ("pm2_5", "temp1") if k in options] or options[:2]
    if "ov_corr" in st.session_state:
        kept = [m for m in st.session_state["ov_corr"] if m in options]
        st.session_state["ov_corr"] = kept or default_corr
    else:
        st.session_state["ov_corr"] = default_corr
    corr_measures = st.multiselect(
        "Measures to relate", options=options, key="ov_corr", format_func=lambda k: get(k).label,
        help="Two or more measures recorded by this device; paired per reading. "
             "The plain-language verdict comes first; the chart is the evidence.",
    )

    if len(corr_measures) < 2:
        st.info("Pick at least two measures to see whether they relate.", icon=":material/info:")
    else:
        # Skeleton the verdict + chart while the paired-readings query runs.
        corr_ph = st.empty()
        with corr_ph.container():
            skeleton.lines(widths=("55%", "45%"), height="1.1rem")
            skeleton.block(360)
        corr_df, corr_hidden, _ = load_timeseries(table, tuple(corr_measures), fs.start, fs.end, clean=True)
        with corr_ph.container():
            frame = build_comparison_frame(corr_df, corr_measures)
            if len(frame) < 2:
                st.warning(
                    "Not enough paired readings in this range to compare these measures.",
                    icon=":material/info:",
                )
            else:
                for a, b in itertools.combinations(corr_measures, 2):
                    res = compute_correlation(frame, (a, b))
                    v = correlation_verdict(res.r)
                    prefix = f"{v.arrow} " if v.arrow else ""
                    r_text = "–" if res.r is None else f"{res.r:+.2f}"
                    st.markdown(
                        f":{v.badge}-badge[{prefix}{v.label}] "
                        f"**{get(a).short_label} ↔ {get(b).short_label}** · r = {r_text} · n = {res.n:,}",
                        help="Strength by |r|: <0.3 none/weak · 0.3–0.7 moderate · >0.7 strong. "
                             "Sign (↑/↓) = rise together vs. move oppositely. Correlation is not causation.",
                    )
                if len(corr_measures) == 2:
                    a, b = corr_measures
                    view = st.segmented_control(
                        "Chart", options=["Scatter", "Overlay"], key="ov_corr_view", default="Scatter",
                        help="Scatter shows the relationship itself; Overlay compares the curve shapes over time.",
                    ) or "Scatter"
                    if view == "Scatter":
                        res = compute_correlation(frame, (a, b))
                        st.plotly_chart(
                            charts.scatter_correlation(frame, a, b, slope=res.slope, intercept=res.intercept),
                            **_PLOT,
                        )
                    else:
                        norm, ranges = normalize_frame(frame, corr_measures)
                        st.plotly_chart(charts.normalized_overlay(norm, corr_measures, ranges), **_PLOT)
                else:
                    res = compute_correlation(frame, tuple(corr_measures))
                    st.plotly_chart(charts.correlation_heatmap(res.matrix), **_PLOT)
                if (notice := hidden_notice(corr_hidden)):
                    st.caption(f":material/visibility_off: {notice}")

# Publish the current view to the URL (shareable/bookmarkable).
publish_query_params(
    {"ov_sensors": table, "ov_range": fs.range_key, "ov_corr": st.session_state.get("ov_corr", [])}
)

# Sticky filter bar: toggle `.ov-stuck` on the bar once it reaches the top so
# the CSS in app.py morphs it into a full-width top bar (and reverts on the way
# back up). Done in JS — not a CSS scroll-timeline — so it works in Safari and
# Firefox too. Runs in a 0-height same-origin iframe, reaches the parent DOM.
#
# This iframe is *destroyed and recreated* when you leave the Dashboard and come
# back. Its scroll listener / observers live in the iframe's JS context, so they
# die with it — yet `stMain` persists across that navigation. So the watcher
# must NOT gate re-binding on flags stored on the persistent DOM (an earlier
# `stMain.__ovBound` / `window.parent.__ovStickyInit` did, which left the
# returning page with a dead listener and a non-full-width bar). Instead every
# iframe run re-binds fresh in its own live context, first tearing down the
# previous run's listener/observers (refs parked on the persistent nodes).
components.html(
    """
    <script>
    (function () {
      const W = window.parent;
      const doc = W.document;
      const STICK_TOP = 58;  /* matches the CSS sticky offset (top: 3.5rem) */
      function sync() {
        const bar = doc.querySelector('.st-key-ov_bar');
        const main = doc.querySelector('[data-testid="stMain"]');
        if (!bar || !main) return;
        const stuck = bar.getBoundingClientRect().top <= STICK_TOP;
        bar.classList.toggle('ov-stuck', stuck);
        if (stuck) {
          /* span the main content column (NOT the viewport), so the bar never
             slides under an open sidebar; clientWidth excludes the scrollbar. */
          const wrap = bar.parentElement;
          const leftGutter = wrap.getBoundingClientRect().left - main.getBoundingClientRect().left;
          const w = main.clientWidth;
          bar.style.width = w + 'px';
          bar.style.maxWidth = w + 'px';
          bar.style.marginLeft = (-leftGutter) + 'px';
        } else {
          bar.style.width = '';
          bar.style.maxWidth = '';
          bar.style.marginLeft = '';
        }
      }
      function bind() {
        const sc = doc.querySelector('[data-testid="stMain"]');
        /* `__ovSync` holds the live sync fn of whichever iframe bound this node.
           A different value (or none) means this is a fresh iframe / new node —
           swap in our listener and re-arm the ResizeObserver. Same value means
           we already bound it this run, so don't stack listeners. */
        if (sc && sc.__ovSync !== sync) {
          if (sc.__ovSync) sc.removeEventListener('scroll', sc.__ovSync);
          sc.addEventListener('scroll', sync, { passive: true });
          sc.__ovSync = sync;
          if (sc.__ovRO) { try { sc.__ovRO.disconnect(); } catch (e) {} }
          sc.__ovRO = new ResizeObserver(sync);  /* fires on sidebar open/close + resize */
          sc.__ovRO.observe(sc);
        }
        sync();
      }
      /* One live MutationObserver per iframe run; drop the previous (now-dead)
         one so they don't pile up across navigations. */
      if (W.__ovMO) { try { W.__ovMO.disconnect(); } catch (e) {} }
      W.__ovMO = new MutationObserver(bind);
      W.__ovMO.observe(doc.documentElement, { childList: true, subtree: true });
      bind();
    })();
    </script>
    """,
    height=0,
)
