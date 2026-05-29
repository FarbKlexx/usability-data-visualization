"""Time Series page — deep exploration of one sensor (plan §5.2).

* Selectors: sensor (1) + measures (multi) + time range.
* Each chart supports direct manipulation: drag-to-zoom, double-click to
  reset, click-legend to toggle a series — no separate filter panel.
* Measures are grouped **by unit** into separate charts, so different
  units are never forced onto one deceptive axis (CONTEXT ethics). PM
  (µg/m³) shares one chart; CO₂, temperature, humidity, pressure each
  get their own — the "small multiples" of plan §5.2.
* Honesty: every axis is unit-labelled; hidden-sentinel and
  downsampling notices are shown explicitly.
"""

from __future__ import annotations

import streamlit as st

from src.components import charts, filter_bar
from src.data import available_metrics, load_devices, load_particle_sizes, load_timeseries, shape_of
from src.utils.clean import hidden_notice
from src.utils.metrics import METRICS, get

st.title(":material/timeline: Time Series")
st.caption("Pick a sensor and measures, then zoom and brush directly on the charts.")

devices = load_devices()
pool = devices[devices["has_data"]]

fs = filter_bar(
    devices, prefix="ts", multi=False, pool=pool,
    default_tables=["sensor_000aeb8337ac"], default_range="30 d",
)
if fs.is_empty:
    st.stop()
table = fs.tables[0]

# Measures available on *this* sensor's shape (resets when the sensor changes,
# since the option set changes — no stale selections).
options = [m.key for m, _ in available_metrics(table)]
default = [k for k in ("pm2_5", "pm10_0") if k in options] or options[:1]
measures = st.multiselect(
    "Measures", options=options, default=default,
    format_func=lambda k: get(k).label,
    help="Add or remove measures. Different units are charted separately.",
)
if not measures:
    st.info("Select at least one measure to plot.", icon=":material/info:")
    st.stop()

df, hidden, bucket_s = load_timeseries(table, tuple(measures), fs.start, fs.end)
if df.empty:
    st.warning("No readings in the selected range.", icon=":material/info:")
    st.stop()


def _humanize(seconds: int) -> str:
    for limit, div, unit in ((90, 1, "s"), (5400, 60, "min"), (129600, 3600, "h")):
        if seconds < limit:
            return f"{round(seconds / div)} {unit}"
    return f"{round(seconds / 86400)} d"


st.caption(
    f":material/compress: Averaged into {_humanize(bucket_s)} buckets to keep the view responsive."
)
notice = hidden_notice(hidden)
if notice:
    st.caption(f":material/visibility_off: {notice}")

# One chart per unit (registry order preserved).
groups: dict[str, list[str]] = {}
for key in (k for k in METRICS if k in measures):
    groups.setdefault(get(key).unit, []).append(key)

for unit, keys in groups.items():
    names = ", ".join(get(k).label for k in keys)
    st.markdown(f"**{names}** &nbsp;·&nbsp; {unit}".replace("&nbsp;", " "))
    st.plotly_chart(
        charts.line_chart(df, keys, height=300 if len(groups) > 1 else 420),
        theme="streamlit", width="stretch", config={"displaylogo": False},
    )

st.caption("Drag to zoom · double-click to reset · click a legend entry to toggle a series.")

# Hi-res sensor drill-down: particle-size distribution (plan §3 candidate 8).
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
