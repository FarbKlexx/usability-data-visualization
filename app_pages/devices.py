"""Devices & Data Quality page — the catalog and an honest data audit (plan §5.5).

Makes the dataset's structure and its quirks transparent rather than
hiding them (CONTEXT ethics): which of the 40 registered objects map to
a real table, how many rows each holds, when each has coverage, and the
known anomalies (saturation sentinels, swapped coordinates, duplicate
rows, empty devices).
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from src.components import charts
from src.data import load_comparison, load_devices

st.title(":material/sensors: Devices & Data Quality")
st.caption("The full device catalog and an honest account of the data's quirks.")

devices = load_devices()

# --- Summary ----------------------------------------------------------------
registered = devices["oo_id"].notna()
n_registered = int(registered.sum())
n_with_data = int(devices["has_data"].sum())
n_registered_no_table = int((registered & ~devices["table_exists"]).sum())
n_external = int((~registered).sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Registered objects", n_registered, help="Rows in tbl_observedobject.", border=True)
c2.metric("Sensors with data", n_with_data, help="Tables that actually hold readings.", border=True)
c3.metric("Registered, no table", n_registered_no_table, help="Mobile m13–m20: registered but never logged.", border=True)
c4.metric("External / specialty", n_external, help="Sources outside the device registry.", border=True)

st.divider()

# --- Coverage timeline ------------------------------------------------------
st.subheader(":material/timeline: Data availability")
cov = devices[devices["has_data"]][["name", "first_ts", "last_ts", "n_rows"]].rename(
    columns={"name": "label"}
)
st.plotly_chart(
    charts.coverage_timeline(cov),
    theme="streamlit", width="stretch", config={"displaylogo": False},
)
st.caption("Each bar is a sensor's first→last reading. A device with no bar logged nothing.")

st.divider()

# --- Catalog table ----------------------------------------------------------
st.subheader(":material/table: Device catalog")
disp = devices.copy()
disp = disp[
    ["name", "ootype", "table_shape", "city", "mac", "table_exists", "n_rows", "first_ts", "last_ts"]
]
st.dataframe(
    disp,
    hide_index=True,
    width="stretch",
    column_config={
        "name": "Device",
        "ootype": "Type",
        "table_shape": st.column_config.TextColumn("Shape", help="A/B/C/Ext column shape."),
        "city": "City",
        "mac": "MAC",
        "table_exists": st.column_config.CheckboxColumn("Table?", help="A sensor_<mac> table exists."),
        "n_rows": st.column_config.NumberColumn("Rows", format="%d"),
        "first_ts": st.column_config.DatetimeColumn("First reading", format="YYYY-MM-DD"),
        "last_ts": st.column_config.DatetimeColumn("Last reading", format="YYYY-MM-DD"),
    },
)

st.divider()

# --- Data-quality audit -----------------------------------------------------
st.subheader(":material/rule: Known data-quality issues")

with st.spinner("Counting saturation sentinels…"):
    wide_start = datetime(2023, 1, 1)
    wide_end = datetime(2026, 1, 1)
    stationary = devices[
        devices["has_data"] & (devices["ootype"] == "Stationary") & (devices["table_shape"] == "A")
    ]
    tables = tuple(stationary["table_name"])
    name_map = {r["table_name"]: r["name"] for _, r in stationary.iterrows()}
    pm25 = load_comparison(tables, "pm2_5", wide_start, wide_end).set_index("table_name")["n_hidden"]
    pm10 = load_comparison(tables, "pm10_0", wide_start, wide_end).set_index("table_name")["n_hidden"]

sentinel_rows = [
    {
        "Sensor": name_map.get(t, t),
        "PM2.5 ≥ 999.9": int(pm25.get(t, 0) or 0),
        "PM10 ≥ 1999.9": int(pm10.get(t, 0) or 0),
    }
    for t in tables
]
if sentinel_rows:
    st.markdown("**Saturation sentinels excluded from every chart** (counted, never silently dropped):")
    st.dataframe(sentinel_rows, hide_index=True, width="stretch")

st.markdown(
    """
Handled centrally in the data layer so every view tells the same story:

- **Saturation ceilings** — PM2.5 caps at 999.9 µg/m³, PM10 at 1999.9, temp1 at 85 °C.
  These are nulled before any average and disclosed wherever they occur.
- **Swapped coordinates** — the hi-res Gdańsk sensor stores lat/lon reversed;
  corrected on load so it maps to the right place.
- **Duplicate rows** — one mobile track has identical repeated rows (a migration
  artefact); de-duplicated before drawing the track.
- **Empty devices** — mobile units *m13–m20* are registered but never logged data,
  so they carry no table and appear here with zero rows.
- **Units** — particulate matter is shown as **µg/m³**, correcting the registry's
  mislabelled "ppm".
- **No native `ts` index** — a reversible migration adds one per populated table so
  time-range queries stay responsive.
"""
)
