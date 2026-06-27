"""Route detail — one mobile trip, in depth (drill-down from the Dashboard).

A hidden page (not in the nav rail): the Dashboard's mobile **Routes** list
opens it via ``st.switch_page(..., query_params=…)``, passing the sensor
table, the route id, and the segmentation gap + time window so this page
re-segments identically and isolates the one trip.

Layout mirrors the Dashboard cockpit: a verdict hero (air-quality word +
red→green meter) → a KPI strip of trip stats → the route on a map → its
PM2.5 over time. Everything reachable by URL, so a link restores the view.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import streamlit as st

from src.components import charts
from src.components.filter_bar import device_label
from src.components.meter import air_quality_meter
from src.data import available_metrics, load_devices, load_routes, load_timeseries
from src.utils.aqi import COMPUTED_NOTE, caqi_band, caqi_index
from src.utils.clean import hidden_notice
from src.utils.metrics import get

_PLOT = {"theme": "streamlit", "width": "stretch", "config": {"displaylogo": False}}
_MAP_PLOT = {"theme": "streamlit", "width": "stretch", "config": {"scrollZoom": True, "displaylogo": False}}


def _haversine_km(lat: np.ndarray, lon: np.ndarray) -> float:
    """Total great-circle length (km) along an ordered lat/lon track."""
    if len(lat) < 2:
        return 0.0
    lat1, lat2 = np.radians(lat[:-1]), np.radians(lat[1:])
    dlat = lat2 - lat1
    dlon = np.radians(lon[1:]) - np.radians(lon[:-1])
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return float((2 * 6371.0 * np.arcsin(np.sqrt(a))).sum())


st.title(":material/route: Route detail")

qp = st.query_params
table = qp.get("route_table")
rid_raw = qp.get("route_id")

# --- Resolve the selection from the URL; bail gracefully if absent/stale -----
if not table or rid_raw is None:
    st.info("Open a trip from the Dashboard's **Routes** list to see its details.", icon=":material/info:")
    st.page_link("app_pages/dashboard.py", label="Back to Dashboard", icon=":material/dashboard:")
    st.stop()

try:
    rid = int(rid_raw)
    gap = int(qp.get("route_gap", 3600))
    start = datetime.fromisoformat(qp["route_start"])
    end = datetime.fromisoformat(qp["route_end"])
except (ValueError, KeyError):
    st.error("This route link is incomplete or malformed.", icon=":material/error:")
    st.page_link("app_pages/dashboard.py", label="Back to Dashboard", icon=":material/dashboard:")
    st.stop()

devices = load_devices()
drow = devices[devices["table_name"] == table]
device_name = device_label(drow.iloc[0]) if not drow.empty else table

routes = load_routes(table, gap_seconds=gap, start=start, end=end)
one = routes[routes["route_id"] == rid] if not routes.empty else routes
if one.empty:
    st.warning(
        "That trip is no longer in the selected range (the time window or split gap may have changed).",
        icon=":material/info:",
    )
    st.page_link("app_pages/dashboard.py", label="Back to Dashboard", icon=":material/dashboard:")
    st.stop()

st.caption(f":material/sensors: {device_name} · Route {rid + 1}")

# --- Trip stats --------------------------------------------------------------
one = one.sort_values("ts")
t_start, t_end = one["ts"].min(), one["ts"].max()
duration_h = (t_end - t_start).total_seconds() / 3600
distance_km = _haversine_km(one["lat"].to_numpy(), one["lon"].to_numpy())
mean_pm = one["pm2_5"].mean()
max_pm = one["pm2_5"].max()
band = caqi_band(mean_pm if not np.isnan(mean_pm) else None)
idx = caqi_index(mean_pm if not np.isnan(mean_pm) else None)

# === ZONE 1: verdict hero (air quality on the trip, by mean PM2.5) ===========
with st.container(border=True, key="box_hero"):
    meta = f"CAQI from mean PM2.5 over the trip · {t_start:%Y-%m-%d %H:%M}–{t_end:%H:%M}"
    if band is None:
        st.subheader(":material/help: Air quality: no PM reading on this trip", help=meta)
    else:
        st.subheader(f"{band.icon} Air quality: {band.quality}", help=meta)
        if idx is not None:
            air_quality_meter(1.0 - min(idx, 100.0) / 100.0, band.color)

# === ZONE 2: KPI strip — the trip's headline numbers =========================
with st.container(horizontal=True):
    st.metric("Points", f"{len(one):,}", border=True, help="GPS readings recorded on this trip.")
    st.metric("Duration", f"{duration_h:.1f} h", border=True, help=f"{t_start:%H:%M} → {t_end:%H:%M}")
    st.metric("Distance", f"{distance_km:.1f} km", border=True, help="Great-circle length along the track.")
    st.metric(
        "Mean PM2.5", "–" if np.isnan(mean_pm) else f"{mean_pm:.1f}", border=True,
        help="Mean PM2.5 (µg/m³) across the trip; saturation sentinels excluded.",
    )
    st.metric(
        "Max PM2.5", "–" if np.isnan(max_pm) else f"{max_pm:.1f}", border=True,
        help="Highest PM2.5 (µg/m³) reading on the trip.",
    )

# === ZONE 3: the route on a map, then its PM2.5 over time ====================
with st.container(border=True, key="box_routedetailmap"):
    st.markdown(
        "**:material/route: Route travelled**",
        help="Drag to pan · scroll to zoom · points coloured by PM2.5 (Viridis).",
    )
    st.plotly_chart(charts.route_map(one, selected_route=rid, height=460), **_MAP_PLOT)

with st.container(border=True, key="box_routepm"):
    st.markdown(
        "**:material/timeline: Measures over the trip**",
        help="Drag to zoom · double-click to reset · click a legend entry to toggle a series.",
    )
    options = [m.key for m, _ in available_metrics(table)]
    default = [k for k in ("pm2_5",) if k in options] or options[:1]
    chosen = st.multiselect(
        "Measures", options=options, default=default, format_func=lambda k: get(k).label,
        help="Pick one or more measures recorded by this sensor to plot over the trip's time window.",
    )
    if not chosen:
        st.caption("Pick at least one measure to plot.")
    else:
        tdf, thidden, _ = load_timeseries(
            table, tuple(chosen), t_start.to_pydatetime(),
            (t_end + timedelta(seconds=1)).to_pydatetime(), clean=True,
        )
        # Group by unit so different units never share a (misleading) y-axis;
        # each unit gets its own chart (honest data, no deceptive dual axes).
        groups: dict[str, list[str]] = {}
        for k in chosen:
            groups.setdefault(get(k).unit, []).append(k)
        for keys in groups.values():
            st.plotly_chart(charts.line_chart(tdf, tuple(keys), height=300), **_PLOT)
        if (notice := hidden_notice(thidden)):
            st.caption(f":material/visibility_off: {notice}")

st.caption("Computed from the mobile sensor's GPS track.", help=COMPUTED_NOTE)
st.page_link("app_pages/dashboard.py", label="Back to Dashboard", icon=":material/dashboard:")
