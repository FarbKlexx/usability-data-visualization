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

import pandas as pd

from src.components import charts
from src.components.kpi import aqi_tile, metric_tile
from src.data import load_devices, load_latest, load_locations, load_tracks
from src.db import update_location
from src.utils.aqi import caqi_band
from src.utils.metrics import HEADLINE_KPIS
from src.utils.state import hand_off_to_timeseries

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

# Cross-filter hand-off: jump to the Time Series page for this sensor (plan §A1).
st.button(
    "Explore in Time Series",
    icon=":material/timeline:",
    help="Open the Time Series page focused on this sensor.",
    on_click=hand_off_to_timeseries,
    args=(chosen,),
)

st.divider()

# --- Edit a location (interactivity plan §B2) -------------------------------
st.subheader(":material/edit_location: Edit a location")
st.caption(
    "Correct a station's address or move its map point. Coordinates are "
    "stored as a PostGIS point (SRID 4326); the preview updates as you type."
)

loc_pool = devices[devices["loc_id"].notna()].copy()
if loc_pool.empty:
    st.info("No editable locations are linked to a device.", icon=":material/info:")
else:
    loc_ids = [int(v) for v in loc_pool["loc_id"].unique()]
    loc_name = {
        int(r["loc_id"]): f"{r['name']}" + (f" · {r['city']}" if isinstance(r.get("city"), str) and r["city"] else "")
        for _, r in loc_pool.iterrows()
    }
    # Drop a stale selection before the widget binds (else selectbox raises).
    if st.session_state.get("editloc_id") not in loc_ids:
        st.session_state.pop("editloc_id", None)
    edit_loc_id = st.selectbox(
        "Location", options=loc_ids, format_func=lambda i: loc_name.get(i, str(i)),
        key="editloc_id", help="Pick the location to edit.",
    )
    lrow = loc_pool[loc_pool["loc_id"] == edit_loc_id].iloc[0]

    def _txt(v: object) -> str:
        return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)

    def _coord(v: object, fallback: float) -> float:
        return fallback if v is None or (isinstance(v, float) and pd.isna(v)) else float(v)

    fields_col, map_col = st.columns([0.5, 0.5], vertical_alignment="top")
    with fields_col:
        new_name = st.text_input("Name", value=_txt(lrow.get("name")), key="editloc_name")
        new_city = st.text_input("City", value=_txt(lrow.get("city")), key="editloc_city")
        new_street = st.text_input("Street", value=_txt(lrow.get("street")), key="editloc_street")
        new_postcode = st.text_input("Postcode", value=_txt(lrow.get("postcode")), key="editloc_postcode")
        cc1, cc2 = st.columns(2)
        new_lon = cc1.number_input(
            "Longitude", value=_coord(lrow.get("lon"), 8.9), format="%.6f", step=0.0001, key="editloc_lon"
        )
        new_lat = cc2.number_input(
            "Latitude", value=_coord(lrow.get("lat"), 52.3), format="%.6f", step=0.0001, key="editloc_lat"
        )
    with map_col:
        preview = pd.DataFrame(
            [{"lat": new_lat, "lon": new_lon, "label": new_name or "new position",
              "group": "Edited point", "color": charts.OKABE_ITO[1]}]
        )
        st.plotly_chart(
            charts.map_figure(preview, height=260, show_text=True),
            theme="streamlit", width="stretch",
            config={"scrollZoom": True, "displaylogo": False},
        )

    if st.button("Save location", icon=":material/save:", type="primary", key="editloc_save"):
        if not new_name.strip():
            st.error("Name cannot be empty.", icon=":material/error:")
        else:
            try:
                n = update_location(
                    int(edit_loc_id),
                    {
                        "name": new_name.strip(),
                        "city": new_city.strip() or None,
                        "street": new_street.strip() or None,
                        "postcode": new_postcode.strip() or None,
                    },
                    lon=new_lon,
                    lat=new_lat,
                )
                st.success(f"Location saved — {n} write(s) applied.", icon=":material/check_circle:")
                st.rerun()
            except Exception as exc:  # noqa: BLE001 — surface write failures
                st.error(f"Could not save: {exc}", icon=":material/error:")
