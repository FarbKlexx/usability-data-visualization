"""Time Series page — deep, interactive exploration of one sensor.

Baseline (plan m1 §5.2): sensor + measures + range selectors, direct
manipulation on the charts, measures grouped by unit (no deceptive dual
axes), honest hidden-sentinel / downsampling notices.

Interactivity layer (plan §A/§B), added here:

* **A2** adjustable aggregation bucket + a rolling-average overlay.
* **A3** a raw/cleaned toggle that bypasses the sentinel filter so the
  saturation behaviour can be inspected directly.
* **A4** interactive reference thresholds (line + emphasised exceedances),
  defaulting from any persisted thresholds (§B6).
* **A6** CSV export of exactly the view on screen.
* **A7** the view (sensor, measures, range, bucket) is mirrored into the
  URL query params, so a link restores it.
* **B4** time-range annotations: saved notes drawn as shaded bands.
* **B5** a raw-reading inspector that flags individual points without
  altering the source row.

The annotation, raw-inspector and particle-drill-down modules are
*optional*, gated by feature flags (§B3) that the Manage page can toggle.
"""

from __future__ import annotations

from datetime import datetime, time

import pandas as pd
import streamlit as st

from src.components import charts, filter_bar
from src.data import (
    available_metrics,
    dashboard_tables_ready,
    load_annotations,
    load_devices,
    load_particle_sizes,
    load_raw_readings,
    load_reading_flags,
    load_thresholds,
    load_timeseries,
    shape_of,
)
from src.db import (
    add_annotation,
    add_reading_flag,
    delete_annotation,
    delete_reading_flag,
    save_view,
)
from src.utils.clean import hidden_notice
from src.utils.metrics import METRICS, get
from src.utils.state import csv_split, publish_query_params, seed_session_defaults
from src.utils.text import escape_md

_ZOOM_HELP = "Drag to zoom · double-click to reset · click a legend entry to toggle a series."

st.title(":material/timeline: Time Series")

devices = load_devices()
pool = devices[devices["has_data"]]

# --- A7: restore a shared view from the URL before any widget is built ------
seed_session_defaults(
    {
        "ts_sensors": str,
        "ts_range": str,
        "ts_measures": csv_split,
        "ts_bucket": str,
    }
)
# Guard against a stale/invalid sensor in the URL or session (selectbox would
# otherwise raise) — fall back to the bar's own default.
_valid_tables = set(pool["table_name"].dropna())
if st.session_state.get("ts_sensors") not in _valid_tables:
    st.session_state.pop("ts_sensors", None)

fs = filter_bar(
    devices, prefix="ts", multi=False, pool=pool,
    default_tables=["sensor_000aeb8337ac"], default_range="30 d",
)
if fs.is_empty:
    st.stop()
table = fs.tables[0]

# Annotations / flags / saved views need the dashboard_* tables.
dash_ready = dashboard_tables_ready()

# Measures available on *this* sensor's shape. Persist the selection (for the
# URL/back-navigation) but sanitise it against the current sensor's options so
# a measure absent on the new shape never lingers.
options = [m.key for m, _ in available_metrics(table)]
default_measures = [k for k in ("pm2_5", "pm10_0") if k in options] or options[:1]
if "ts_measures" in st.session_state:
    kept = [m for m in st.session_state["ts_measures"] if m in options]
    st.session_state["ts_measures"] = kept or default_measures
else:
    st.session_state["ts_measures"] = default_measures

measures = st.multiselect(
    "Measures", options=options, key="ts_measures",
    format_func=lambda k: get(k).label,
    help="Add or remove measures. Different units are charted separately.",
)
if not measures:
    st.info("Select at least one measure to plot.", icon=":material/info:")
    st.stop()

# --- A2/A3: display controls -----------------------------------------------
_BUCKETS: dict[str, int | None] = {
    "Auto": None, "1 min": 60, "5 min": 300, "15 min": 900,
    "1 hour": 3600, "6 hours": 21600, "1 day": 86400,
}
# Guard a stale/invalid bucket from the URL (the selectbox raises if its
# session value is not among the options) — same pattern as ts_sensors.
if st.session_state.get("ts_bucket") not in _BUCKETS:
    st.session_state.pop("ts_bucket", None)
with st.container(border=True):
    c_bucket, c_smooth, c_raw = st.columns([0.34, 0.4, 0.26], vertical_alignment="center")
    with c_bucket:
        bucket_label = st.selectbox(
            "Aggregation", options=list(_BUCKETS), key="ts_bucket",
            help="How finely to average the series. 'Auto' keeps the view responsive.",
        )
    with c_smooth:
        smooth_window = st.slider(
            "Rolling average (samples)", min_value=0, max_value=60, value=0, step=1,
            help="Overlay a moving average. 0 turns it off; the raw line stays visible.",
        )
    with c_raw:
        show_raw = st.toggle(
            "Show raw (unfiltered)", value=False,
            help="Include saturation/sentinel readings instead of hiding them.",
        )

bucket_seconds = _BUCKETS[bucket_label]
df, hidden, bucket_s = load_timeseries(
    table, tuple(measures), fs.start, fs.end, bucket_seconds=bucket_seconds, clean=not show_raw
)
if df.empty:
    st.warning("No readings in the selected range.", icon=":material/info:")
    st.stop()


def _humanize(seconds: int) -> str:
    for limit, div, unit in ((90, 1, "s"), (5400, 60, "min"), (129600, 3600, "h")):
        if seconds < limit:
            return f"{round(seconds / div)} {unit}"
    return f"{round(seconds / 86400)} d"


st.caption(f":material/compress: Averaged into {_humanize(bucket_s)} buckets ({len(df):,} points).")
notice = hidden_notice(hidden)
if notice:
    verb = "would be hidden in cleaned mode" if show_raw else "were hidden"
    st.caption(f":material/visibility_off: {notice.replace('were hidden', verb)}")
if show_raw:
    st.caption(":material/warning: Raw mode — saturation ceilings (e.g. 999.9) are included and can distort axes.")

# --- A4: reference thresholds (default from persisted thresholds, §B6) ------
saved_thr = load_thresholds()
saved_by_metric = (
    saved_thr.groupby("metric")["value"].last().to_dict() if not saved_thr.empty else {}
)
thresholds: dict[str, float] = {}
with st.expander(":material/horizontal_rule: Reference thresholds", expanded=bool(saved_by_metric)):
    st.caption("Draw a reference line for a measure; readings at/above it are emphasised.")
    st.page_link(
        "app_pages/settings.py", label="Manage saved defaults in Settings", icon=":material/tune:"
    )
    for key in measures:
        m = get(key)
        default_val = float(saved_by_metric.get(key, round(m.vmax * 0.2, 1)))
        cc_on, cc_val = st.columns([0.45, 0.55], vertical_alignment="center")
        on = cc_on.checkbox(
            f"{m.label} ({m.unit})", value=key in saved_by_metric, key=f"thr_on_{key}",
        )
        val = cc_val.number_input(
            f"{m.short_label} threshold", value=default_val, step=1.0,
            key=f"thr_val_{key}", label_visibility="collapsed",
        )
        if on:
            thresholds[key] = val

# --- B4: annotations (optional module) -------------------------------------
annotations_on = dash_ready
ann_overlay: list[dict] = []
if annotations_on:
    ann_df = load_annotations(table)
    if not ann_df.empty:
        in_range = ann_df[
            (pd.to_datetime(ann_df["ts_from"]) <= fs.end)
            & (pd.to_datetime(ann_df["ts_to"].fillna(ann_df["ts_from"])) >= fs.start)
        ]
        ann_overlay = in_range.to_dict("records")

# Smoothing overlay frame (plan §A2): rolling mean on the bucketed series.
smooth_df = None
if smooth_window > 0:
    smooth_df = df.copy()
    for key in measures:
        if key in smooth_df.columns:
            smooth_df[key] = smooth_df[key].rolling(smooth_window, min_periods=1).mean()

# --- Charts: one per unit (registry order preserved) ------------------------
groups: dict[str, list[str]] = {}
for key in (k for k in METRICS if k in measures):
    groups.setdefault(get(key).unit, []).append(key)

for unit, keys in groups.items():
    names = ", ".join(get(k).label for k in keys)
    st.markdown(f"**{names}** · {unit}", help=_ZOOM_HELP)
    st.plotly_chart(
        charts.line_chart(
            df, keys, height=300 if len(groups) > 1 else 420,
            smooth=smooth_df, thresholds={k: v for k, v in thresholds.items() if k in keys},
            annotations=ann_overlay,
        ),
        theme="streamlit", width="stretch", config={"displaylogo": False},
    )

# --- A6: export + A7/B6: save this view ------------------------------------
csv = df.to_csv(index=False).encode("utf-8")
ex_col, save_col = st.columns([0.4, 0.6], vertical_alignment="center")
with ex_col:
    st.download_button(
        "Download current view (CSV)", data=csv,
        file_name=f"{table}_{fs.range_key.replace(' ', '')}_{_humanize(bucket_s).replace(' ', '')}.csv",
        mime="text/csv", icon=":material/download:", width="stretch",
        help="Exactly the points on screen (post-aggregation, post-filter).",
    )
with save_col:
    if dash_ready:
        with st.popover("Save this view", icon=":material/bookmark_add:", width="stretch"):
            st.caption("Persist the sensor, measures, range and bucket as a named view (Manage page lists them).")
            view_name = st.text_input("View name", key="save_view_name", placeholder="e.g. s01 PM last 30 d")
            if st.button("Save view", icon=":material/save:", type="primary", key="save_view_btn"):
                if not view_name.strip():
                    st.error("Give the view a name.", icon=":material/error:")
                else:
                    try:
                        save_view(
                            view_name.strip(),
                            {"table": table, "range": fs.range_key,
                             "measures": list(measures), "bucket": bucket_label},
                        )
                        st.success("View saved — find it on the Manage page.", icon=":material/check_circle:")
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"Could not save: {exc}", icon=":material/error:")
    else:
        st.caption(
            ":material/info: Run `uv run python scripts/add_dashboard_tables.py` to enable "
            "annotations, flags and saved views."
        )

# --- B4: annotation management ---------------------------------------------
if annotations_on:
    with st.expander(":material/edit_note: Annotations", expanded=False):
        st.caption("Mark a time range with a note. Saved annotations appear as shaded bands above.")
        ac1, ac2, ac3 = st.columns([0.3, 0.3, 0.4])
        d_from = ac1.date_input(
            "From", value=fs.start.date(),
            min_value=fs.start.date(), max_value=fs.end.date(), key="ann_from",
        )
        is_point = ac2.checkbox("Single point", value=False, key="ann_point")
        d_to = ac3.date_input(
            "To", value=fs.end.date(), min_value=fs.start.date(), max_value=fs.end.date(),
            key="ann_to", disabled=is_point,
        )
        label = st.text_input("Label", key="ann_label", max_chars=80, placeholder="e.g. heating spike")
        note = st.text_area("Note", key="ann_note", height=68, placeholder="Optional detail…")
        if st.button("Add annotation", icon=":material/add:", type="primary", key="ann_add"):
            if not label.strip():
                st.error("A label is required.", icon=":material/error:")
            else:
                ts_from = datetime.combine(d_from, time.min)
                ts_to = None if is_point else datetime.combine(d_to, time.max)
                try:
                    add_annotation(table, ts_from, ts_to, label.strip(), note.strip())
                    st.success("Annotation added.", icon=":material/check_circle:")
                    st.rerun()
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Could not save: {exc}", icon=":material/error:")

        existing = load_annotations(table)
        if not existing.empty:
            st.markdown("**Saved annotations**")
            for _, a in existing.iterrows():
                span = f"{pd.to_datetime(a['ts_from']):%Y-%m-%d}"
                if pd.notna(a["ts_to"]):
                    span += f" → {pd.to_datetime(a['ts_to']):%Y-%m-%d}"
                lc, dc = st.columns([0.85, 0.15], vertical_alignment="center")
                lc.markdown(
                    f":blue-badge[{span}] **{escape_md(a['label'])}** "
                    f"{('· ' + escape_md(a['note'])) if a['note'] else ''}"
                )
                if dc.button("Delete", icon=":material/delete:", key=f"del_ann_{a['id']}"):
                    delete_annotation(int(a["id"]))
                    st.rerun()

# --- B5: raw-reading inspector + flags (optional module) -------------------
if dash_ready:
    with st.expander(":material/flag: Raw readings & flags", expanded=False):
        st.caption(
            "Flag individual readings (e.g. a 999.9 sentinel) as suspect without "
            "changing the source row. Newest 200 rows in range."
        )
        raw = load_raw_readings(table, fs.start, fs.end, limit=200)
        flags = load_reading_flags(table)
        if not raw.empty:
            shown = raw.copy()
            if not flags.empty:
                flag_by_id = flags.groupby("reading_id")["flag"].first().to_dict()
                shown["flag"] = shown["id"].map(flag_by_id)
            st.dataframe(shown, hide_index=True, width="stretch", height=240)

        fc1, fc2, fc3 = st.columns([0.3, 0.3, 0.4])
        rid = fc1.number_input("Reading id", min_value=0, step=1, key="flag_rid")
        flag_kind = fc2.selectbox("Flag", options=["suspect", "confirmed", "ignore"], key="flag_kind")
        fnote = fc3.text_input("Note", key="flag_note", placeholder="Optional…")
        if st.button("Flag reading", icon=":material/flag:", key="flag_add"):
            try:
                add_reading_flag(table, int(rid), flag_kind, fnote.strip())
                st.success(f"Flagged reading {int(rid)} as '{flag_kind}'.", icon=":material/check_circle:")
                st.rerun()
            except Exception as exc:  # noqa: BLE001
                st.error(f"Could not flag: {exc}", icon=":material/error:")

        if not flags.empty:
            st.markdown("**Existing flags**")
            for _, f in flags.iterrows():
                lc, dc = st.columns([0.85, 0.15], vertical_alignment="center")
                lc.markdown(
                    f":orange-badge[{f['flag']}] reading **{int(f['reading_id'])}**"
                    f"{(' · ' + escape_md(f['note'])) if f['note'] else ''}"
                )
                if dc.button("Delete", icon=":material/delete:", key=f"del_flag_{f['id']}"):
                    delete_reading_flag(int(f["id"]))
                    st.rerun()

# --- Hi-res sensor drill-down: particle-size distribution (optional, §B3) ---
if shape_of(table) == "B":
    st.divider()
    st.subheader(":material/scatter_plot: Particle size distribution")
    part_df = load_particle_sizes(table, fs.start, fs.end)
    st.plotly_chart(
        charts.particle_size_bars(part_df),
        theme="streamlit", width="stretch", config={"displaylogo": False},
    )
    st.caption(
        "Mean concentration per size class over the selected range. "
        "Mass (µg/m³) and particle count (#/cm³) are shown on separate axes — different units."
    )

# --- A7: publish the current view to the URL (shareable/bookmarkable) ------
publish_query_params(
    {
        "ts_sensors": table,
        "ts_range": fs.range_key,
        "ts_measures": measures,
        "ts_bucket": bucket_label,
    }
)
