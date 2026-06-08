"""Devices & Data Quality page — the catalog and an honest data audit (plan §5.5).

Makes the dataset's structure and its quirks transparent rather than
hiding them (CONTEXT ethics): which of the 40 registered objects map to
a real table, how many rows each holds, when each has coverage, and the
known anomalies (saturation sentinels, swapped coordinates, duplicate
rows, empty devices).
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from src.components import charts
from src.data import load_comparison, load_devices
from src.db import update_object

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

st.caption("Handled centrally in the data layer so every view tells the same story — details on demand:")

_ISSUES = (
    ("Saturation ceilings",
     "PM2.5 caps at 999.9 µg/m³, PM10 at 1999.9, temp1 at 85 °C. These are nulled "
     "before any average and disclosed wherever they occur."),
    ("Swapped coordinates",
     "The hi-res Gdańsk sensor stores lat/lon reversed; corrected on load so it "
     "maps to the right place."),
    ("Duplicate rows",
     "One mobile track has identical repeated rows (a migration artefact); "
     "de-duplicated before drawing the track."),
    ("Empty devices",
     "Mobile units *m13–m20* are registered but never logged data, so they carry "
     "no table and appear here with zero rows."),
    ("Units",
     "Particulate matter is shown as **µg/m³**, correcting the registry's "
     "mislabelled \"ppm\"."),
    ("No native `ts` index",
     "A reversible migration adds one per populated table so time-range queries "
     "stay responsive."),
)
for _title, _detail in _ISSUES:
    with st.expander(_title):
        st.markdown(_detail)

st.divider()

# --- Edit device metadata (interactivity plan §B1) --------------------------
st.subheader(":material/edit: Edit device metadata")
st.caption(
    "Update the catalog entry for a registered device. Only descriptive "
    "fields are editable — measurement data is never touched."
)

editable = devices[devices["oo_id"].notna()].copy()
if editable.empty:
    st.info("No registered devices to edit.", icon=":material/info:")
else:
    options = [int(v) for v in editable["oo_id"]]
    name_by_id = {int(r["oo_id"]): str(r["name"]) for _, r in editable.iterrows()}
    # Drop a stale selection before the widget binds (else selectbox raises).
    if st.session_state.get("edit_device_id") not in options:
        st.session_state.pop("edit_device_id", None)
    chosen_id = st.selectbox(
        "Device", options=options, format_func=lambda i: name_by_id.get(i, str(i)),
        key="edit_device_id", help="Pick the device whose metadata you want to edit.",
    )
    row = editable[editable["oo_id"] == chosen_id].iloc[0]

    def _clean(v: object) -> str:
        return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)

    with st.form("edit_device", border=True):
        name = st.text_input("Name", value=_clean(row.get("name")), max_chars=255)
        description = st.text_area("Description", value=_clean(row.get("description")), height=80)
        icon = st.text_input(
            "Icon", value=_clean(row.get("icon")),
            help="A Material icon name, e.g. sensors or place.",
        )
        datacapture = st.checkbox(
            "Data capture enabled",
            value=bool(row.get("datacapture")) if pd.notna(row.get("datacapture")) else False,
            help="Whether this device is actively collecting (metadata flag only).",
        )
        c_save, c_hint = st.columns([0.25, 0.75], vertical_alignment="center")
        submitted = c_save.form_submit_button(
            "Save changes", icon=":material/save:", type="primary", width="stretch"
        )
        c_hint.caption("Changes are written in one transaction; the catalog reloads on save.")

    if submitted:
        if not name.strip():
            st.error("Name cannot be empty.", icon=":material/error:")
        else:
            try:
                n = update_object(
                    int(chosen_id),
                    {
                        "name": name.strip(),
                        "description": description.strip() or None,
                        "icon": icon.strip() or None,
                        "datacapture": bool(datacapture),
                    },
                )
                st.success(f"Saved — {n} row updated.", icon=":material/check_circle:")
                st.rerun()
            except Exception as exc:  # noqa: BLE001 — surface write failures to the user
                st.error(f"Could not save: {exc}", icon=":material/error:")
