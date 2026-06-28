"""Devices & Data Quality page — the device catalog + coverage timeline.

Makes the dataset's structure transparent (CONTEXT ethics): which of the
registered objects map to a real table, how many rows each holds, and when
each has coverage — honest about gaps (a device with no bar logged nothing).

The layout **mirrors the Dashboard cockpit** so the two pages read as one
product: a verdict **hero card** (the dataset at a glance — the single
focal point) over a **KPI strip**, then bordered ``box_*`` tile cards
(coverage · catalog). Each card carries an icon+title header whose
operating hints live in tooltips, and a skeleton-swap load so the layout
never jumps — exactly the hub's treatment.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.components import charts, skeleton
from src.data import load_devices

st.title(":material/sensors: Devices & Data Quality")
st.caption("The full device catalog and when each sensor has coverage.")

# === ZONES 1+2: hero + KPI strip — skeletoned before the catalog query ========
# Both are whole-swapped (their content *is* the data), so they get a content-
# shaped skeleton in a reserved slot and swap once load_devices() resolves.
hero_ph = st.empty()
with hero_ph.container(border=True, key="box_dev_hero_skel"):
    skeleton.lines(widths=("30%", "75%", "55%"))

strip_ph = st.empty()
with strip_ph.container():
    skeleton.tiles(4)

# === ZONE 3: content cards. The box + its title render immediately; only the
# data area (an inner st.empty) shows a skeleton until the catalog resolves. ===
with st.container(border=True, key="box_coverage"):
    st.markdown(
        "**:material/timeline: Data availability**",
        help="Each bar spans a sensor's first→last reading; hover for its row "
             "count. A device with no bar logged nothing — honest about gaps.",
    )
    cov_ph = st.empty()
    with cov_ph.container():
        skeleton.block(420)

with st.container(border=True, key="box_catalog"):
    st.markdown(
        "**:material/table: Device catalog**",
        help="Every registered object and external source: type, column shape "
             "(A/B/C/Ext), location, MAC and row count. Click a header to sort.",
    )
    cat_ph = st.empty()
    with cat_ph.container():
        skeleton.block(320)

# The one blocking catalog query — every skeleton above is visible while it runs.
devices = load_devices()

# --- Summary counts (drive the hero + the KPI strip) ------------------------
registered = devices["oo_id"].notna()
n_registered = int(registered.sum())
n_with_data = int(devices["has_data"].sum())
n_registered_with_data = int((registered & devices["has_data"]).sum())
n_registered_no_table = int((registered & ~devices["table_exists"]).sum())
n_external = int((~registered).sum())
total_rows = int(devices["n_rows"].fillna(0).sum())
span_lo = devices["first_ts"].min()
span_hi = devices["last_ts"].max()

# === ZONE 1: hero — the dataset at a glance (the focal point) =================
with hero_ph.container(border=True, key="box_dev_hero"):
    st.markdown(
        "**:material/insights: Dataset overview**",
        help="The full record at a glance: how many readings, over what span, "
             "and across how many of the registered devices.",
    )
    st.subheader(f":material/database: {total_rows:,} readings from {n_with_data} active sensors")
    # Badges carry what the KPI strip below does *not*: the record's time span
    # and a coverage framing of the registry, not the raw per-category counts.
    badges = ""
    if pd.notna(span_lo) and pd.notna(span_hi):
        badges += f":gray-badge[{span_lo:%b %Y} – {span_hi:%b %Y}] "
    badges += f":gray-badge[{n_registered_with_data} of {n_registered} registered logging]"
    st.markdown(badges)

# === ZONE 2: KPI strip — the registry broken into ≤7 tiles (Miller) ===========
with strip_ph.container():
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registered objects", n_registered, help="Rows in tbl_observedobject.", border=True)
    c2.metric("Sensors with data", n_with_data, help="Tables that actually hold readings.", border=True)
    c3.metric("Registered, no table", n_registered_no_table, help="Mobile m13–m20: registered but never logged.", border=True)
    c4.metric("External / specialty", n_external, help="Sources outside the device registry.", border=True)

# === Coverage timeline — swap the real chart into the reserved slot ===========
with cov_ph.container():
    cov = devices[devices["has_data"]][["name", "first_ts", "last_ts", "n_rows"]].rename(
        columns={"name": "label"}
    )
    st.plotly_chart(
        charts.coverage_timeline(cov),
        theme="streamlit", width="stretch", config={"displaylogo": False},
    )

# === Device catalog — swap the real table into the reserved slot ==============
with cat_ph.container():
    disp = devices.copy()[
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
