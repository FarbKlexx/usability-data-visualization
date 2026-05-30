"""Dashboard — the central hub (consolidation plan §B).

Rebuilt from the old read-only "Overview" to be the place that answers the
app's core question first and pulls the key signals up from the subpages:

* **B1 — plain-language status** leads: a worded air-quality verdict +
  EU-CAQI category (via ``aqi.py``), so a non-expert understands the
  situation before reading an axis (CONTEXT: match-the-real-world,
  most-important-top-left).
* **B2 — pulled-up values**: the latest KPIs and the headline PM trend,
  each linking through to the Time Series page for the full detail (the
  hub summarizes; the subpage expands).
* **B3/B4 — correlation, verdict-first**: pick 2+ measures, get a
  colour-coded ``|r|`` strength verdict (word + arrow + neutral badge,
  never colour alone) *above* a single supporting chart that swaps in
  place (scatter for two measures, matrix for three or more).

The subpages stay in place (moderate consolidation); the dashboard is the
hub layered on top.
"""

from __future__ import annotations

import itertools

import streamlit as st

from src.components import charts, filter_bar
from src.components.kpi import aqi_tile, metric_tile
from src.data import (
    available_metrics,
    build_comparison_frame,
    load_devices,
    load_latest,
    load_locations,
    load_timeseries,
)
from src.utils.aqi import COMPUTED_NOTE, caqi_band
from src.utils.clean import hidden_notice
from src.utils.correlate import compute_correlation, correlation_verdict, normalize_frame
from src.utils.metrics import HEADLINE_KPIS, get
from src.utils.state import (
    csv_split,
    hand_off_to_timeseries,
    publish_query_params,
    seed_session_defaults,
)

# CAQI level → Streamlit badge colour (mirrors the aqi_tile mapping; the
# icon + word carry the meaning, the colour only reinforces it).
_BAND_BADGE = {0: "green", 1: "blue", 2: "orange", 3: "red", 4: "violet"}

st.title(":material/dashboard: Dashboard")
st.caption("Your air-quality answer at a glance — open any card for the full detail.")

devices = load_devices()
# Stationary Shape-A units carry the full measure set; the sparse external
# feeds would distort the headline numbers (kept on Map / Devices).
pool = devices[
    devices["has_data"] & (devices["ootype"] == "Stationary") & (devices["table_shape"] == "A")
]

# Restore a shared view from the URL before any widget binds (bookmarkable).
seed_session_defaults({"ov_sensors": str, "ov_range": str, "ov_corr": csv_split})
_valid_tables = set(pool["table_name"].dropna())
if st.session_state.get("ov_sensors") not in _valid_tables:
    st.session_state.pop("ov_sensors", None)

fs = filter_bar(
    devices, prefix="ov", multi=False, pool=pool,
    default_tables=["sensor_000aeb8337ac"], default_range="7 d",
)
if fs.is_empty:
    st.stop()
table = fs.tables[0]
sensor_label = fs.labels[0]

# Latest snapshot — shared by the status band (B1) and the KPI row (B2).
latest_df, latest_ts = load_latest(table)
vals = {r.metric: (r.value, r.delta) for r in latest_df.itertuples()}
band = caqi_band(vals.get("pm2_5", (None,))[0], vals.get("pm10_0", (None,))[0])

# === B1: plain-language status (leads, top-left) ===========================
with st.container(border=True):
    if band is None:
        st.subheader(":material/help: Air quality: no current reading")
        st.caption(f"{sensor_label} has no usable PM2.5/PM10 reading right now.")
    else:
        badge = _BAND_BADGE.get(band.level, "gray")
        st.subheader(f"{band.icon} Air quality: {band.quality}")
        st.markdown(f":{badge}-badge[CAQI: {band.label}] &nbsp; {band.advice}")
        meta = f"{sensor_label} · CAQI computed from PM2.5/PM10"
        if latest_ts is not None:
            meta += f" · latest {latest_ts:%Y-%m-%d %H:%M}"
        st.caption(meta, help=COMPUTED_NOTE)

# === B2: latest KPIs, pulled up from the subpages ==========================
st.markdown("#### :material/insights: Latest readings")
if latest_ts is not None:
    st.caption(f":material/schedule: {latest_ts:%Y-%m-%d %H:%M} · trend vs. previous 24 h")
cols = st.columns(len(HEADLINE_KPIS) + 1, gap="small")
for col, key in zip(cols, HEADLINE_KPIS):
    with col:
        value, delta = vals.get(key, (None, None))
        metric_tile(key, value, delta)
with cols[-1]:
    aqi_tile(band)

st.divider()

# === B2: headline trend, pulled up (links through to Time Series) ==========
h_left, h_right = st.columns([0.68, 0.32], vertical_alignment="center")
h_left.markdown("#### :material/timeline: Particulate matter over time")
with h_right:
    st.button(
        "Open this sensor in Time Series", icon=":material/open_in_full:",
        on_click=hand_off_to_timeseries, args=(table,), width="stretch",
        help="Open the Time Series page focused on this sensor for the full detail.",
    )
ts_df, ts_hidden, _ = load_timeseries(table, ("pm2_5", "pm10_0"), fs.start, fs.end)
st.plotly_chart(
    charts.line_chart(ts_df, ("pm2_5", "pm10_0")),
    theme="streamlit", width="stretch", config={"displaylogo": False},
)
if (notice := hidden_notice(ts_hidden)):
    st.caption(f":material/visibility_off: {notice}")
st.caption("Drag to zoom · double-click to reset · click a legend entry to toggle a series.")

st.divider()

# === B3/B4: correlation, verdict-first, replace-in-place ===================
st.markdown("#### :material/scatter_plot: Do these measures move together?")
st.caption("Pick two or more measures from this sensor. The plain-language verdict comes first; the chart below is the evidence.")

options = [m.key for m, _ in available_metrics(table)]
default_corr = [k for k in ("pm2_5", "temp1") if k in options] or options[:2]
if "ov_corr" in st.session_state:
    kept = [m for m in st.session_state["ov_corr"] if m in options]
    st.session_state["ov_corr"] = kept or default_corr
else:
    st.session_state["ov_corr"] = default_corr

corr_measures = st.multiselect(
    "Measures to relate", options=options, key="ov_corr",
    format_func=lambda k: get(k).label,
    help="Two or more measures recorded by this sensor; they are paired per reading.",
)

if len(corr_measures) < 2:
    st.info("Pick at least two measures to see whether they relate.", icon=":material/info:")
else:
    corr_df, corr_hidden, _ = load_timeseries(table, tuple(corr_measures), fs.start, fs.end, clean=True)
    frame = build_comparison_frame(corr_df, corr_measures)
    if len(frame) < 2:
        st.warning(
            "Not enough paired readings in this range to compare these measures. "
            "Try a wider time range or different measures.",
            icon=":material/info:",
        )
    else:
        # B3 — the verdict leads: one color-coded line per measure pair.
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

        # B4 — one chart slot that swaps content with the selection.
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
                    theme="streamlit", width="stretch", config={"displaylogo": False},
                )
                st.caption(
                    "Each point is one sample, colored from the start (dark) to the end (yellow) of the range; "
                    "the dashed line is the least-squares fit."
                )
            else:
                norm, ranges = normalize_frame(frame, corr_measures)
                st.plotly_chart(
                    charts.normalized_overlay(norm, corr_measures, ranges),
                    theme="streamlit", width="stretch", config={"displaylogo": False},
                )
                st.caption(
                    "Both measures min–max scaled to 0–1 so their *shapes* line up; hover shows the real value. "
                    + " · ".join(f"**{get(k).short_label}** {get(k).format(lo)}–{get(k).format(hi)}"
                                 for k, (lo, hi) in ranges.items())
                )
        else:
            res = compute_correlation(frame, tuple(corr_measures))
            st.plotly_chart(
                charts.correlation_heatmap(res.matrix),
                theme="streamlit", width="stretch", config={"displaylogo": False},
            )
            st.caption("Pairwise r over the paired samples; each cell prints its coefficient (−1 inverse · 0 none · +1 identical).")

        if (notice := hidden_notice(corr_hidden)):
            st.caption(f":material/visibility_off: {notice}")

st.divider()

# === Mini-map — spatial teaser, links to the full Map ======================
m_left, m_right = st.columns([0.7, 0.3], vertical_alignment="center")
m_left.markdown("#### :material/map: Where the sensors are")
m_right.page_link("app_pages/map.py", label="Open full map", icon=":material/open_in_full:")
loc = load_locations()
st.plotly_chart(
    charts.map_figure(charts.build_location_markers(loc), height=300, show_text=False),
    theme="streamlit", width="stretch", config={"scrollZoom": True, "displaylogo": False},
)

# Publish the current view to the URL (shareable/bookmarkable).
publish_query_params({"ov_sensors": table, "ov_range": fs.range_key, "ov_corr": corr_measures})
