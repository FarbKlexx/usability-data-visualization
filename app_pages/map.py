"""Map page — spatial view of locations and mobile tracks (plan §5.3).

* Layer toggles (stationary locations / mobile tracks) — progressive
  disclosure, user in control.
* Markers are colored by their computed CAQI band **and** grouped into a
  legend, so the color always has a textual key (never color alone).
* Pan/zoom is direct manipulation; "details on demand" is a selector
  below the map that shows a sensor's latest readings.
* Honesty: the hi-res sensor's swapped coordinates are corrected in the
  loader; the mobile track that reaches back to 2023 is flagged.
"""

from __future__ import annotations

import streamlit as st

from src.components import charts
from src.components.kpi import aqi_tile, metric_tile
from src.data import load_devices, load_latest, load_locations, load_tracks
from src.utils.aqi import caqi_band
from src.utils.metrics import HEADLINE_KPIS

st.title(":material/map: Map")
st.caption("Where the sensors sit, and where the mobile units travelled.")

devices = load_devices()
loc = load_locations()

layers = st.pills(
    "Layers", options=["Stationary & fixed", "Mobile tracks"],
    selection_mode="multi", default=["Stationary & fixed", "Mobile tracks"],
    help="Toggle map layers on and off.",
)

# Latest CAQI band per located sensor that has data → marker color + legend.
band_lookup: dict[str, object] = {}
for _, r in loc.iterrows():
    tn = r.get("table_name")
    if not (isinstance(tn, str) and bool(r.get("has_data"))):
        continue
    latest_df, _ = load_latest(tn)
    vals = {row.metric: row.value for row in latest_df.itertuples()}
    band = caqi_band(vals.get("pm2_5"), vals.get("pm10_0"))
    if band is not None:
        band_lookup[tn] = band

markers = charts.build_location_markers(loc, band_lookup) if "Stationary & fixed" in layers else None

tracks = []
if "Mobile tracks" in layers:
    mobile = devices[devices["is_mobile"] & devices["has_data"]]
    for i, (_, r) in enumerate(mobile.iterrows()):
        trk = load_tracks(r["table_name"])
        if not trk.empty:
            tracks.append(
                {"label": r["name"], "lat": trk["lat"], "lon": trk["lon"], "color": charts.track_palette(i)}
            )

st.plotly_chart(
    charts.map_figure(markers, tracks, height=560, show_text=False),
    theme="streamlit", width="stretch",
    config={"scrollZoom": True, "displaylogo": False},
)
st.caption(
    ":material/info: Marker color = computed CAQI band (see legend). "
    "The hi-res Gdańsk sensor's stored lat/lon were de-swapped on load; "
    "one mobile track extends back to 2023."
)

st.divider()

# --- Details on demand -----------------------------------------------------
st.subheader(":material/readiness_score: Sensor details")
detail_pool = loc[loc["table_name"].notna() & loc["has_data"]]
detail_options = list(detail_pool["table_name"])
if not detail_options:
    st.info("No located sensor has live readings.", icon=":material/info:")
    st.stop()

labels = {r["table_name"]: r["name"] for _, r in detail_pool.iterrows()}
chosen = st.selectbox(
    "Show latest readings for", options=detail_options,
    format_func=lambda t: labels.get(t, t),
)
latest_df, latest_ts = load_latest(chosen)
vals = {r.metric: (r.value, r.delta) for r in latest_df.itertuples()}
if latest_ts is not None:
    st.caption(f":material/schedule: Latest reading {latest_ts:%Y-%m-%d %H:%M}")

keys = [k for k in HEADLINE_KPIS if k in vals]
cols = st.columns(len(keys) + 1, gap="small")
for col, key in zip(cols, keys):
    with col:
        value, delta = vals[key]
        metric_tile(key, value, delta)
with cols[-1]:
    aqi_tile(caqi_band(vals.get("pm2_5", (None,))[0], vals.get("pm10_0", (None,))[0]))
