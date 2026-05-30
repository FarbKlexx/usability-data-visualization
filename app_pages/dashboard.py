"""Dashboard — the adaptive central hub (adaptive-device-view plan).

One unified picker lists every data-bearing device grouped by type; the
page then **reshapes itself to the selected device** (plan §A/§B):

* **Primary zone** (consistent placement, read at a glance): the device
  picker, a plain-language air-quality status, and exactly **one headline
  visual** — the PM time-series for a stationary/fixed device, or a
  **segmented route map** for a mobile one (§B1/§B2/§B3, Sweet Spot,
  Miller).
* **Secondary zone** (progressive disclosure, Hick's Law): everything
  else lives in **tabs** — *Measures & data* (KPIs, measures, raw/clean,
  export), *Correlation* (verdict-first), and, for mobile, *Routes*
  (route list, split-gap control, per-route PM chart) — so the advanced
  controls never compete with the primary answer (§D).

Subpages stay in place; the dashboard is the hub layered on top.
"""

from __future__ import annotations

import itertools

import pandas as pd
import streamlit as st

from src.components import charts, filter_bar
from src.components.kpi import aqi_tile, metric_tile
from src.data import (
    available_metrics,
    build_comparison_frame,
    load_devices,
    load_latest,
    load_locations,
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

st.title(":material/dashboard: Dashboard")
st.caption("Pick any device — the view adapts to it. The air-quality answer is up top; details are in the tabs below.")

devices = load_devices()
pool = devices[devices["has_data"]]  # every data-bearing device (plan §A)

# Restore a shared view from the URL before any widget binds (bookmarkable).
seed_session_defaults(
    {"ov_sensors": str, "ov_range": str, "ov_measures": csv_split, "ov_corr": csv_split}
)
_valid_tables = set(pool["table_name"].dropna())
if st.session_state.get("ov_sensors") not in _valid_tables:
    st.session_state.pop("ov_sensors", None)

# === PRIMARY: unified, type-grouped device picker (consistent spot) =========
fs = filter_bar(
    devices, prefix="ov", multi=False, pool=pool, group_by_type=True,
    default_tables=["sensor_000aeb8337ac"], default_range="7 d",
)
if fs.is_empty:
    st.stop()
table = fs.tables[0]
drow = devices[devices["table_name"] == table].iloc[0]
is_mobile = bool(drow["is_mobile"])

# === PRIMARY: plain-language status (same for every device type) ============
latest_df, latest_ts = load_latest(table)
vals = {r.metric: (r.value, r.delta) for r in latest_df.itertuples()}
band = caqi_band(vals.get("pm2_5", (None,))[0], vals.get("pm10_0", (None,))[0])
with st.container(border=True):
    if band is None:
        st.subheader(":material/help: Air quality: no current reading")
        st.caption(f"{fs.labels[0]} has no usable PM2.5/PM10 reading right now.")
    else:
        st.subheader(f"{band.icon} Air quality: {band.quality}")
        st.markdown(f":{_BAND_BADGE.get(band.level, 'gray')}-badge[CAQI: {band.label}] &nbsp; {band.advice}")
        meta = f"{fs.labels[0]} · CAQI computed from PM2.5/PM10"
        if latest_ts is not None:
            meta += f" · latest reading {latest_ts:%Y-%m-%d %H:%M}"
        st.caption(meta, help=COMPUTED_NOTE)

# === PRIMARY: exactly one headline visual, chosen by device type ============
routes = pd.DataFrame()  # populated for mobile; referenced again in the Routes tab
if is_mobile:
    st.markdown("#### :material/route: Routes travelled")
    gap_seconds = int(st.session_state.get("ov_route_gap", 3600))
    routes = load_routes(table, gap_seconds=gap_seconds, start=fs.start, end=fs.end)
    if routes.empty:
        st.info(
            "No routes for this device in the selected range. Widen the time range "
            "(the **Reset** button restores it, or try **All**).",
            icon=":material/info:",
        )
    else:
        route_ids = [int(r) for r in sorted(routes["route_id"].unique())]
        sel = st.session_state.get("ov_route_sel")
        selected_route = sel if isinstance(sel, int) and sel in route_ids else None
        st.plotly_chart(charts.route_map(routes, selected_route=selected_route), **_MAP_PLOT)
        scope = "all routes" if selected_route is None else f"route {selected_route + 1}"
        st.caption(
            f":material/route: {len(route_ids)} trip(s), {len(routes):,} points (showing {scope}). "
            "Points coloured by PM2.5 (Viridis legend); each line is one trip. "
            "Drag to pan · scroll to zoom · pick a trip in the **Routes** tab."
        )
else:
    st.markdown("#### :material/timeline: Particulate matter over time")
    ts_df, ts_hidden, _ = load_timeseries(table, ("pm2_5", "pm10_0"), fs.start, fs.end)
    st.plotly_chart(charts.line_chart(ts_df, ("pm2_5", "pm10_0")), **_PLOT)
    if (notice := hidden_notice(ts_hidden)):
        st.caption(f":material/visibility_off: {notice}")
    st.caption("Drag to zoom · double-click to reset · click a legend entry to toggle a series.")

    # B1/B3: a small location map so the spatial context is present even for a
    # device that doesn't move (the fixed-point 781c sensor lands here too).
    loc_one = load_locations()
    loc_one = loc_one[
        (loc_one["table_name"] == table) & loc_one["lon"].notna() & loc_one["lat"].notna()
    ]
    st.markdown("**:material/location_on: Where this sensor sits**")
    if loc_one.empty:
        st.caption(":material/location_off: No location is recorded for this sensor.")
    else:
        st.plotly_chart(
            charts.map_figure(charts.build_location_markers(loc_one), height=240, show_text=True),
            **_MAP_PLOT,
        )

st.divider()

# === SECONDARY: tabs (progressive disclosure, plan §D) ======================
tab_titles = (
    [":material/route: Routes", ":material/insights: Measures & data", ":material/scatter_plot: Correlation"]
    if is_mobile
    else [":material/insights: Measures & data", ":material/scatter_plot: Correlation"]
)
tabs = dict(zip(["routes", "measures", "correlation"] if is_mobile else ["measures", "correlation"], st.tabs(tab_titles)))

# --- Routes tab (mobile only): list, split control, per-route PM chart ------
if is_mobile:
    with tabs["routes"]:
        st.caption("Adjust how trips are split, then inspect a single trip's pollution over time.")
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
                st.markdown(f"**PM2.5 along Route {chosen + 1}**")
                st.plotly_chart(charts.line_chart(rdf, ("pm2_5",), height=260), **_PLOT)
            else:
                st.caption("Pick a trip above to see its PM2.5 over time.")

# --- Measures & data tab (all devices): KPIs + measures + raw/clean + CSV ---
with tabs["measures"]:
    kpis = [k for k in HEADLINE_KPIS if k in vals]
    if latest_ts is not None:
        st.caption(f":material/schedule: Latest reading {latest_ts:%Y-%m-%d %H:%M} · trend vs. previous 24 h")
    if kpis:
        kcols = st.columns(len(kpis) + 1, gap="small")
        for col, key in zip(kcols, kpis):
            with col:
                metric_tile(key, *vals.get(key, (None, None)))
        with kcols[-1]:
            aqi_tile(band)

    options = [m.key for m, _ in available_metrics(table)]
    default_measures = [k for k in ("pm2_5", "pm10_0") if k in options] or options[:1]
    if "ov_measures" in st.session_state:
        kept = [m for m in st.session_state["ov_measures"] if m in options]
        st.session_state["ov_measures"] = kept or default_measures
    else:
        st.session_state["ov_measures"] = default_measures

    mc1, mc2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
    measures = mc1.multiselect(
        "Measures", options=options, key="ov_measures", format_func=lambda k: get(k).label,
        help="Different units are charted separately. Open Time Series for thresholds, rolling averages and annotations.",
    )
    show_raw = mc2.toggle("Show raw", value=False, help="Include saturation/sentinel readings instead of hiding them.")

    if measures:
        mdf, mhidden, _ = load_timeseries(table, tuple(measures), fs.start, fs.end, clean=not show_raw)
        if mdf.empty:
            st.warning("No readings in the selected range.", icon=":material/info:")
        else:
            groups: dict[str, list[str]] = {}
            for key in (k for k in options if k in measures):
                groups.setdefault(get(key).unit, []).append(key)
            for unit, keys in groups.items():
                st.markdown(f"**{', '.join(get(k).label for k in keys)}** · {unit}")
                st.plotly_chart(charts.line_chart(mdf, keys, height=300 if len(groups) > 1 else 360), **_PLOT)
            if (notice := hidden_notice(mhidden)):
                verb = "would be hidden in cleaned mode" if show_raw else "were hidden"
                st.caption(f":material/visibility_off: {notice.replace('were hidden', verb)}")
            st.download_button(
                "Download these measures (CSV)", data=mdf.to_csv(index=False).encode("utf-8"),
                file_name=f"{table}_{fs.range_key.replace(' ', '')}.csv", mime="text/csv",
                icon=":material/download:", help="Exactly the points on screen (post-aggregation, post-filter).",
            )
    else:
        st.info("Select at least one measure to plot.", icon=":material/info:")
    st.button(
        "Open this device in Time Series", icon=":material/open_in_full:",
        on_click=hand_off_to_timeseries, args=(table,),
        help="Full depth: aggregation bucket, rolling average, thresholds, annotations, flags.",
    )

# --- Correlation tab (all devices): verdict-first, replace-in-place ---------
with tabs["correlation"]:
    st.caption("Pick two or more measures from this device. The plain-language verdict comes first; the chart is the evidence.")
    options = [m.key for m, _ in available_metrics(table)]
    default_corr = [k for k in ("pm2_5", "temp1") if k in options] or options[:2]
    if "ov_corr" in st.session_state:
        kept = [m for m in st.session_state["ov_corr"] if m in options]
        st.session_state["ov_corr"] = kept or default_corr
    else:
        st.session_state["ov_corr"] = default_corr
    corr_measures = st.multiselect(
        "Measures to relate", options=options, key="ov_corr", format_func=lambda k: get(k).label,
        help="Two or more measures recorded by this device; they are paired per reading.",
    )

    if len(corr_measures) < 2:
        st.info("Pick at least two measures to see whether they relate.", icon=":material/info:")
    else:
        corr_df, corr_hidden, _ = load_timeseries(table, tuple(corr_measures), fs.start, fs.end, clean=True)
        frame = build_comparison_frame(corr_df, corr_measures)
        if len(frame) < 2:
            st.warning("Not enough paired readings in this range to compare these measures.", icon=":material/info:")
        else:
            for a, b in itertools.combinations(corr_measures, 2):
                res = compute_correlation(frame, (a, b))
                v = correlation_verdict(res.r)
                prefix = f"{v.arrow} " if v.arrow else ""
                r_text = "–" if res.r is None else f"{res.r:+.2f}"
                st.markdown(
                    f":{v.badge}-badge[{prefix}{v.label}] "
                    f"**{get(a).short_label} ↔ {get(b).short_label}** · r = {r_text} · n = {res.n:,}"
                )
            st.caption(
                "Strength by |r|: under 0.3 = no/weak · 0.3–0.7 = moderate · over 0.7 = strong. "
                "Sign (↑/↓) shows whether they rise together or move oppositely. Correlation is not causation."
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
                        charts.scatter_correlation(frame, a, b, slope=res.slope, intercept=res.intercept), **_PLOT
                    )
                    st.caption("Each point is one sample, coloured start (dark) → end (yellow); dashed line is the least-squares fit.")
                else:
                    norm, ranges = normalize_frame(frame, corr_measures)
                    st.plotly_chart(charts.normalized_overlay(norm, corr_measures, ranges), **_PLOT)
                    st.caption(
                        "Both measures min–max scaled to 0–1 so their shapes line up. "
                        + " · ".join(f"**{get(k).short_label}** {get(k).format(lo)}–{get(k).format(hi)}"
                                     for k, (lo, hi) in ranges.items())
                    )
            else:
                res = compute_correlation(frame, tuple(corr_measures))
                st.plotly_chart(charts.correlation_heatmap(res.matrix), **_PLOT)
                st.caption("Pairwise r over the paired samples; each cell prints its coefficient (−1 inverse · 0 none · +1 identical).")
            if (notice := hidden_notice(corr_hidden)):
                st.caption(f":material/visibility_off: {notice}")

# Publish the current view to the URL (shareable/bookmarkable).
publish_query_params(
    {"ov_sensors": table, "ov_range": fs.range_key, "ov_measures": st.session_state.get("ov_measures", []),
     "ov_corr": st.session_state.get("ov_corr", [])}
)
