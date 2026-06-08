"""Comparison surface — sensors against each other (plan §5.4).

Several sensors, one measure → grouped average bars (with on-bar value
labels, so color is not the sole channel) and a distribution box plot
that surfaces spread and outliers honestly. Saturation sentinels are
excluded from the statistics but **counted and disclosed**.

Consolidation note: this is no longer a top-level page. Its body is
exposed as :func:`render_compare`, which the Dashboard hub mounts inside
a **Compare** tab (one fewer top-level destination — Hick's law at the
menu level). It keeps its own ``cmp``-prefixed multi-sensor toolbar
because multi-sensor scoping is intentionally a different task from the
hub's single-device picker; only the *destination* is folded in.
"""

from __future__ import annotations

import streamlit as st

from src.components import charts, filter_bar
from src.components.filter_bar import device_label
from src.data import available_metrics, load_comparison, load_devices
from src.utils.metrics import get

_DEFAULTS = [
    "sensor_000aeb8337ac", "sensor_74da38543e94",
    "sensor_74da38543e8d", "sensor_801f02b31e0d",
]


def render_compare() -> None:
    """Render the multi-sensor comparison surface (mounted in a hub tab)."""
    devices = load_devices()
    pool = devices[devices["has_data"]]

    fs = filter_bar(
        devices, prefix="cmp", multi=True, pool=pool,
        default_tables=_DEFAULTS, default_range="30 d",
    )
    if fs.is_empty:
        return

    # Only measures present on *every* selected sensor can be compared fairly.
    common: set[str] | None = None
    for table in fs.tables:
        keys = {m.key for m, _ in available_metrics(table)}
        common = keys if common is None else (common & keys)
    common = common or set()
    metric_options = [k for k in ("pm2_5", "pm10_0", "co2", "temp1", "inn_hum", "inn_pres") if k in common]

    if not metric_options:
        st.warning(
            "The selected sensors share no comparable measure. "
            "Pick sensors of the same kind (e.g. the stationary units).",
            icon=":material/info:",
        )
        return

    metric_key = st.selectbox(
        "Measure", options=metric_options, format_func=lambda k: get(k).label,
        help="Only measures available on every selected sensor are offered.",
    )

    stats = load_comparison(tuple(fs.tables), metric_key, fs.start, fs.end)
    if stats.empty or stats["n"].fillna(0).sum() == 0:
        st.warning("No readings for these sensors in the selected range.", icon=":material/info:")
        return

    label_map = {r["table_name"]: device_label(r) for _, r in devices.iterrows()}

    hidden_total = int(stats["n_hidden"].fillna(0).sum())
    if hidden_total:
        st.caption(
            f":material/visibility_off: {hidden_total} reading(s) at/above the measuring range "
            f"were excluded from the statistics."
        )

    tab_avg, tab_dist = st.tabs([":material/bar_chart: Averages", ":material/box: Distribution"])
    with tab_avg:
        st.plotly_chart(
            charts.grouped_bar(stats, metric_key, label_map),
            theme="streamlit", width="stretch", config={"displaylogo": False},
        )
        st.caption("Bars show the mean over the selected range; labels give the exact value.")
    with tab_dist:
        st.plotly_chart(
            charts.box_from_stats(stats, metric_key, label_map),
            theme="streamlit", width="stretch", config={"displaylogo": False},
        )
        st.caption("Box = inter-quartile range with median; whiskers reach the min/max.")

    show = stats.assign(sensor=stats["table_name"].map(lambda t: label_map.get(t, t)))

    # A6: export the current comparison (post-filter) as CSV.
    st.download_button(
        "Download comparison (CSV)",
        data=show[["sensor", "n", "avg", "min", "q1", "median", "q3", "max", "n_hidden"]]
        .to_csv(index=False)
        .encode("utf-8"),
        file_name=f"comparison_{get(metric_key).key}_{fs.range_key.replace(' ', '')}.csv",
        mime="text/csv", icon=":material/download:",
        help="The per-sensor summary statistics currently shown.",
    )

    with st.expander("Show the numbers"):
        st.dataframe(
            show[["sensor", "n", "avg", "min", "q1", "median", "q3", "max", "n_hidden"]],
            hide_index=True, width="stretch",
            column_config={
                "sensor": "Sensor",
                "n": st.column_config.NumberColumn("n", format="%d"),
                "avg": st.column_config.NumberColumn("mean", format="%.1f"),
                "q1": st.column_config.NumberColumn("Q1", format="%.1f"),
                "median": st.column_config.NumberColumn("median", format="%.1f"),
                "q3": st.column_config.NumberColumn("Q3", format="%.1f"),
                "min": st.column_config.NumberColumn("min", format="%.1f"),
                "max": st.column_config.NumberColumn("max", format="%.1f"),
                "n_hidden": st.column_config.NumberColumn("hidden", format="%d"),
            },
        )
