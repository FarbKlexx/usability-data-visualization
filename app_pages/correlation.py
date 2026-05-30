"""Correlation page — do a sensor's measures move together?
(implementation plan ``implementation_plan_correlation_graph.md``).

On a Shape-A sensor every measure of a moment lives in the *same row with
the same timestamp*, so two measures are already paired per row — no time
alignment needed. This page lets the user pick 2+ measures from one
sensor and inspect their relationship three ways (plan §B):

* **Scatter / correlation** (§B3) — measure A vs B, colored by time, with
  a least-squares fit and the Pearson/Spearman ``r`` + sample size ``n``.
  This is the mode that actually quantifies correlation.
* **Normalized overlay** (§B1) — every measure min–max-scaled to 0–1 on
  one axis, so the *shapes* of the curves are directly comparable despite
  different units. Real min/max are disclosed so the scale is recoverable.
* **Dual axis** (§B2, two measures) — A on the left axis, B on the right,
  each in its true unit.

For three or more measures the scatter becomes a **correlation matrix**
heatmap (§B3). A lag control (§D) shifts the second measure so the user
can probe whether one measure *leads* another.

Sentinel cleaning stays applied by default (the 999.9 PM ceiling and the
85 °C ``temp1`` fault would otherwise dominate any correlation); the
raw/cleaned toggle remains so the saturation behaviour is inspectable.
"""

from __future__ import annotations

import streamlit as st

from src.components import charts, filter_bar
from src.data import available_metrics, build_comparison_frame, load_devices, load_timeseries
from src.utils.clean import hidden_notice
from src.utils.correlate import compute_correlation, interpret_r, normalize_frame
from src.utils.metrics import get, label_with_unit
from src.utils.state import csv_split, publish_query_params, seed_session_defaults

st.title(":material/scatter_plot: Correlation")
st.caption("Pick one sensor and two or more measures, then see whether they move together.")

devices = load_devices()
pool = devices[devices["has_data"]]

# Restore a shared view from the URL before any widget is built (mirrors the
# Time Series page's bookmarkable state, plan §A7).
seed_session_defaults(
    {
        "corr_sensors": str,
        "corr_range": str,
        "corr_measures": csv_split,
        "corr_bucket": str,
        "corr_mode": str,
        "corr_method": str,
    }
)
_valid_tables = set(pool["table_name"].dropna())
if st.session_state.get("corr_sensors") not in _valid_tables:
    st.session_state.pop("corr_sensors", None)

fs = filter_bar(
    devices, prefix="corr", multi=False, pool=pool,
    default_tables=["sensor_000aeb8337ac"], default_range="30 d",
)
if fs.is_empty:
    st.stop()
table = fs.tables[0]

# Measures available on this sensor's shape; persist + sanitise the selection
# against the current sensor (a measure absent on a new shape never lingers).
options = [m.key for m, _ in available_metrics(table)]
default_measures = [k for k in ("pm2_5", "temp1") if k in options] or options[:2]
if "corr_measures" in st.session_state:
    kept = [m for m in st.session_state["corr_measures"] if m in options]
    st.session_state["corr_measures"] = kept or default_measures
else:
    st.session_state["corr_measures"] = default_measures

measures = st.multiselect(
    "Measures", options=options, key="corr_measures",
    format_func=lambda k: get(k).label,
    help="Two or more measures recorded by this sensor. They are paired per reading.",
)
if len(measures) < 2:
    st.info("Pick at least two measures to compare.", icon=":material/info:")
    st.stop()

# --- Display controls -------------------------------------------------------
_BUCKETS: dict[str, int | None] = {
    "Auto": None, "1 min": 60, "5 min": 300, "15 min": 900,
    "1 hour": 3600, "6 hours": 21600, "1 day": 86400,
}
_METHODS = {"pearson": "Pearson (linear)", "spearman": "Spearman (monotonic)"}
if st.session_state.get("corr_bucket") not in _BUCKETS:
    st.session_state.pop("corr_bucket", None)
if st.session_state.get("corr_method") not in _METHODS:
    st.session_state.pop("corr_method", None)

with st.container(border=True):
    c_bucket, c_method, c_raw = st.columns([0.36, 0.38, 0.26], vertical_alignment="center")
    with c_bucket:
        bucket_label = st.selectbox(
            "Aggregation", options=list(_BUCKETS), key="corr_bucket",
            help="How finely to average each measure before pairing. 'Auto' keeps the view responsive.",
        )
    with c_method:
        method = st.selectbox(
            "Correlation method", options=list(_METHODS), key="corr_method",
            format_func=lambda k: _METHODS[k],
            help="Pearson measures a straight-line relationship; Spearman measures a monotonic (rank) one.",
        )
    with c_raw:
        show_raw = st.toggle(
            "Show raw (unfiltered)", value=False,
            help="Include saturation/sentinel readings instead of hiding them — they can dominate a correlation.",
        )

# Mode choice depends on how many measures are selected (plan §B).
two = len(measures) == 2
mode_options = (
    ["Scatter", "Normalized overlay", "Dual axis"] if two
    else ["Correlation matrix", "Normalized overlay"]
)
if st.session_state.get("corr_mode") not in mode_options:
    st.session_state.pop("corr_mode", None)
mode = st.segmented_control(
    "View", options=mode_options, key="corr_mode", default=mode_options[0],
    help="How to render the selected measures.",
) or mode_options[0]

# --- Load + align -----------------------------------------------------------
bucket_seconds = _BUCKETS[bucket_label]
df, hidden, bucket_s = load_timeseries(
    table, tuple(measures), fs.start, fs.end, bucket_seconds=bucket_seconds, clean=not show_raw
)
if df.empty:
    st.warning("No readings in the selected range.", icon=":material/info:")
    st.stop()

frame = build_comparison_frame(df, measures)
n_paired = len(frame)
n_dropped = len(df) - n_paired
if n_paired < 2:
    st.warning(
        "Not enough rows where every selected measure is present to correlate. "
        "Try a wider range, a coarser aggregation, or fewer measures.",
        icon=":material/info:",
    )
    st.stop()


def _humanize(seconds: int) -> str:
    for limit, div, unit in ((90, 1, "s"), (5400, 60, "min"), (129600, 3600, "h")):
        if seconds < limit:
            return f"{round(seconds / div)} {unit}"
    return f"{round(seconds / 86400)} d"


st.caption(
    f":material/compress: Averaged into {_humanize(bucket_s)} buckets · "
    f"{n_paired:,} paired samples"
    + (f" ({n_dropped:,} buckets dropped — a measure was missing)" if n_dropped else "")
    + "."
)
notice = hidden_notice(hidden)
if notice:
    verb = "would be hidden in cleaned mode" if show_raw else "were hidden"
    st.caption(f":material/visibility_off: {notice.replace('were hidden', verb)}")
if show_raw:
    st.caption(
        ":material/warning: Raw mode — saturation ceilings (e.g. 999.9) are included "
        "and can dominate the correlation."
    )

_PLOT = {"theme": "streamlit", "width": "stretch", "config": {"displaylogo": False}}


def _show_stats(result, *, method_label: str) -> None:
    """Pearson/Spearman r + n + plain-words strength for two measures."""
    c_r, c_n, c_rel = st.columns(3)
    r_text = "–" if result.r is None else f"{result.r:+.2f}"
    c_r.metric(f"{method_label} r", r_text, help="−1 = perfect inverse, 0 = none, +1 = perfect.")
    c_n.metric("Paired samples (n)", f"{result.n:,}")
    c_rel.metric("Relationship", interpret_r(result.r).capitalize())
    if result.lag:
        a, b = (get(k).short_label for k in result.keys)
        st.caption(
            f":material/schedule: {b} shifted by {result.lag:+d} bucket(s) "
            f"({_humanize(bucket_s)} each) relative to {a}."
        )


# --- Render per mode --------------------------------------------------------
if mode == "Scatter":
    a, b = measures
    lag = st.slider(
        "Lag (buckets)", min_value=-24, max_value=24, value=0, step=1, key="corr_lag",
        help=f"Shift {get(b).short_label} relative to {get(a).short_label} to probe whether one leads the other.",
    )
    result = compute_correlation(frame, (a, b), method=method, lag=lag)
    st.plotly_chart(
        charts.scatter_correlation(
            # re-pair after the lag shift so the plotted points match the stat
            build_comparison_frame(frame.assign(**{b: frame[b].shift(lag)}), (a, b)),
            a, b, slope=result.slope, intercept=result.intercept,
        ),
        **_PLOT,
    )
    st.caption(
        f"Each point is one {_humanize(bucket_s)} sample · color runs from the start "
        f"(dark) to the end (yellow) of the range."
        + ("" if method == "pearson" else " Spearman is rank-based, so no straight-line fit is drawn.")
    )
    _show_stats(result, method_label=_METHODS[method].split(" ")[0])

elif mode == "Correlation matrix":
    result = compute_correlation(frame, measures, method=method)
    st.plotly_chart(charts.correlation_heatmap(result.matrix), **_PLOT)
    st.caption(
        f"Pairwise {_METHODS[method].split(' ')[0]} r over {result.n:,} paired samples. "
        "Each cell prints its coefficient (−1 inverse · 0 none · +1 identical)."
    )

elif mode == "Normalized overlay":
    norm, ranges = normalize_frame(frame, measures)
    st.plotly_chart(charts.normalized_overlay(norm, measures, ranges), **_PLOT)
    st.caption("Each measure is min–max scaled to 0–1 so the *shapes* line up. Real ranges:")
    st.markdown(
        " · ".join(
            f"**{get(k).short_label}** {get(k).format(lo)} – {get(k).format(hi)}"
            for k, (lo, hi) in ranges.items()
        )
    )
    if two:
        result = compute_correlation(frame, tuple(measures), method=method)
        _show_stats(result, method_label=_METHODS[method].split(" ")[0])
    else:
        st.caption("Switch to **Correlation matrix** for the pairwise coefficients.")

else:  # Dual axis (two measures, real units)
    a, b = measures
    st.plotly_chart(charts.dual_axis_lines(frame, a, b), **_PLOT)
    st.caption(
        f"**{label_with_unit(a)}** on the left axis · **{label_with_unit(b)}** on the right. "
        "Independent scales — use the **Scatter** view to actually quantify the relationship."
    )
    result = compute_correlation(frame, (a, b), method=method)
    _show_stats(result, method_label=_METHODS[method].split(" ")[0])

st.caption("Drag to zoom · double-click to reset · click a legend entry to toggle a series.")

# --- Export the aligned, on-screen frame as CSV -----------------------------
st.download_button(
    "Download paired samples (CSV)",
    data=frame.to_csv(index=False).encode("utf-8"),
    file_name=f"{table}_correlation_{fs.range_key.replace(' ', '')}.csv",
    mime="text/csv", icon=":material/download:",
    help="Exactly the aligned, paired samples behind this view (post-aggregation, post-filter).",
)

# Publish the current view to the URL (shareable/bookmarkable, plan §A7).
publish_query_params(
    {
        "corr_sensors": table,
        "corr_range": fs.range_key,
        "corr_measures": measures,
        "corr_bucket": bucket_label,
        "corr_mode": mode,
        "corr_method": method,
    }
)
