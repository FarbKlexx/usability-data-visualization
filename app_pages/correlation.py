"""Correlation page — do two measures on one sensor move together?

Verdict-first |r| (a plain-language strength/direction badge) with the
chart as the *evidence*, not the headline. Two measures → a scatter (with
fit line) or a normalised overlay; three or more → a correlation heatmap.
Saturation sentinels are cleaned out before pairing and disclosed.

This was the Dashboard's *Correlation* tab; it is now its own destination
with a single-sensor toolbar (``corr`` prefix) and bookmarkable URL state.
"""

from __future__ import annotations

import itertools

import streamlit as st

from src.components import charts, filter_bar, skeleton
from src.data import available_metrics, build_comparison_frame, load_devices, load_timeseries
from src.utils.clean import hidden_notice
from src.utils.correlate import compute_correlation, correlation_verdict, normalize_frame
from src.utils.metrics import get
from src.utils.state import csv_split, publish_query_params, seed_session_defaults

_PLOT = {"theme": "streamlit", "width": "stretch", "config": {"displaylogo": False}}

st.title(":material/scatter_plot: Correlation")
st.caption(
    "Do two measures on one sensor move together? The plain-language verdict "
    "comes first; the chart is the evidence."
)

devices = load_devices()
pool = devices[devices["has_data"]]

# Restore a shared view from the URL before any widget binds (bookmarkable).
seed_session_defaults({"corr_sensors": str, "corr_range": str, "corr_measures": csv_split})
_valid_tables = set(pool["table_name"].dropna())
if st.session_state.get("corr_sensors") not in _valid_tables:
    st.session_state.pop("corr_sensors", None)

fs = filter_bar(
    devices, prefix="corr", multi=False, pool=pool, group_by_type=True,
    default_tables=["sensor_000aeb8337ac"], default_range="7 d",
)
if fs.is_empty:
    st.stop()
table = fs.tables[0]

options = [m.key for m, _ in available_metrics(table)]
default_corr = [k for k in ("pm2_5", "temp1") if k in options] or options[:2]
if "corr_measures" in st.session_state:
    kept = [m for m in st.session_state["corr_measures"] if m in options]
    st.session_state["corr_measures"] = kept or default_corr
else:
    st.session_state["corr_measures"] = default_corr
corr_measures = st.multiselect(
    "Measures to relate", options=options, key="corr_measures", format_func=lambda k: get(k).label,
    help="Two or more measures recorded by this device; paired per reading. "
         "The plain-language verdict comes first; the chart is the evidence.",
)

if len(corr_measures) < 2:
    st.info("Pick at least two measures to see whether they relate.", icon=":material/info:")
else:
    # Skeleton the verdict + chart while the paired-readings query runs.
    corr_ph = st.empty()
    with corr_ph.container():
        skeleton.lines(widths=("55%", "45%"), height="1.1rem")
        skeleton.block(360)
    corr_df, corr_hidden, _ = load_timeseries(table, tuple(corr_measures), fs.start, fs.end, clean=True)
    with corr_ph.container():
        frame = build_comparison_frame(corr_df, corr_measures)
        if len(frame) < 2:
            st.warning(
                "Not enough paired readings in this range to compare these measures.",
                icon=":material/info:",
            )
        else:
            for a, b in itertools.combinations(corr_measures, 2):
                res = compute_correlation(frame, (a, b))
                v = correlation_verdict(res.r)
                prefix = f"{v.arrow} " if v.arrow else ""
                r_text = "–" if res.r is None else f"{res.r:+.2f}"
                st.markdown(
                    f":{v.badge}-badge[{prefix}{v.label}] "
                    f"**{get(a).short_label} ↔ {get(b).short_label}** · r = {r_text} · n = {res.n:,}",
                    help="Strength by |r|: <0.3 none/weak · 0.3–0.7 moderate · >0.7 strong. "
                         "Sign (↑/↓) = rise together vs. move oppositely. Correlation is not causation.",
                )
            if len(corr_measures) == 2:
                a, b = corr_measures
                view = st.segmented_control(
                    "Chart", options=["Scatter", "Overlay"], key="corr_view", default="Scatter",
                    help="Scatter shows the relationship itself; Overlay compares the curve shapes over time.",
                ) or "Scatter"
                if view == "Scatter":
                    res = compute_correlation(frame, (a, b))
                    st.plotly_chart(
                        charts.scatter_correlation(frame, a, b, slope=res.slope, intercept=res.intercept),
                        **_PLOT,
                    )
                else:
                    norm, ranges = normalize_frame(frame, corr_measures)
                    st.plotly_chart(charts.normalized_overlay(norm, corr_measures, ranges), **_PLOT)
            else:
                res = compute_correlation(frame, tuple(corr_measures))
                st.plotly_chart(charts.correlation_heatmap(res.matrix), **_PLOT)
            if (notice := hidden_notice(corr_hidden)):
                st.caption(f":material/visibility_off: {notice}")

# Publish the current view to the URL (shareable/bookmarkable).
publish_query_params(
    {"corr_sensors": table, "corr_range": fs.range_key, "corr_measures": st.session_state.get("corr_measures", [])}
)
