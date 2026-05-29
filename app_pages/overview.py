"""Overview page — overview-first KPIs and a current air-quality snapshot.

Layout (plan §5.1), top→bottom, ≈4 logical blocks (Miller 7±2):

1. Global filter toolbar (sensor + time range, with Reset + chips).
2. KPI row: 5 headline measures + the computed CAQI band (≤7 tiles).
3. One headline time series (PM2.5 + PM10) for the selected range.
4. A mini map of the stationary locations, linking to the full Map page.

Per plan §8 the sparse external feeds are kept off the Overview (they
would distort the headline numbers); they remain on Map / Devices.
"""

from __future__ import annotations

import streamlit as st

from src.components import charts, filter_bar
from src.components.kpi import aqi_tile, metric_tile
from src.data import load_devices, load_latest, load_locations, load_timeseries
from src.utils.aqi import caqi_band
from src.utils.clean import hidden_notice
from src.utils.metrics import HEADLINE_KPIS

st.title(":material/dashboard: Overview")
st.caption("Latest air-quality snapshot. Overview first — drill down on the other pages.")

devices = load_devices()
pool = devices[
    devices["has_data"] & (devices["ootype"] == "Stationary") & (devices["table_shape"] == "A")
]

fs = filter_bar(
    devices, prefix="ov", multi=False, pool=pool,
    default_tables=["sensor_000aeb8337ac"], default_range="7 d",
)
if fs.is_empty:
    st.stop()
table = fs.tables[0]

# --- KPI row ---------------------------------------------------------------
latest_df, latest_ts = load_latest(table)
vals = {r.metric: (r.value, r.delta) for r in latest_df.itertuples()}

if latest_ts is not None:
    st.caption(f":material/schedule: Latest reading {latest_ts:%Y-%m-%d %H:%M} · trend vs. previous 24 h")

cols = st.columns(len(HEADLINE_KPIS) + 1, gap="small")
for col, key in zip(cols, HEADLINE_KPIS):
    with col:
        value, delta = vals.get(key, (None, None))
        metric_tile(key, value, delta)
with cols[-1]:
    band = caqi_band(vals.get("pm2_5", (None,))[0], vals.get("pm10_0", (None,))[0])
    aqi_tile(band)

st.divider()

# --- Headline time series --------------------------------------------------
st.subheader(":material/timeline: Particulate matter over time")
ts_df, hidden, _ = load_timeseries(table, ("pm2_5", "pm10_0"), fs.start, fs.end)
st.plotly_chart(
    charts.line_chart(ts_df, ("pm2_5", "pm10_0")),
    theme="streamlit", width="stretch",
    config={"displaylogo": False},
)
notice = hidden_notice(hidden)
if notice:
    st.caption(f":material/visibility_off: {notice}")
st.caption("Drag to zoom · double-click to reset · click a legend entry to toggle a series.")

st.divider()

# --- Mini map --------------------------------------------------------------
left, right = st.columns([0.75, 0.25], vertical_alignment="center")
with left:
    st.subheader(":material/map: Where the sensors are")
with right:
    st.page_link("app_pages/map.py", label="Open full map", icon=":material/open_in_full:")

loc = load_locations()
markers = charts.build_location_markers(loc)
st.plotly_chart(
    charts.map_figure(markers, height=320, show_text=False),
    theme="streamlit", width="stretch",
    config={"scrollZoom": True, "displaylogo": False},
)
