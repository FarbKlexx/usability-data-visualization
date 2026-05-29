"""KPI tile component (implementation plan §3 candidate 1).

A KPI tile shows a measure's latest value + unit + label + a 24 h trend
arrow, and there is a sibling tile for the computed CAQI air-quality
band. Design rationale:

* **Overview-first / mental models** — the most important numbers, top
  row, read left→right.
* **Trend by shape + sign, not color alone** — ``st.metric`` renders a
  ▲/▼ arrow with the signed delta; for pollutants we use ``inverse``
  coloring (a rise is *bad*), for neutral climate measures we turn
  delta color *off* so hue never misleads. The arrow + number carry the
  meaning regardless of color vision.
* **CAQI band is triple-encoded** — icon (distinct glyph) + text label +
  a colored badge, rendered through the Streamlit design system (no raw
  HTML, per CLAUDE.md).
* **Fitts' law** — bordered tiles give large, well-padded targets.

These render into the *current* container, so callers place them inside
``st.columns(...)``.
"""

from __future__ import annotations

import streamlit as st

from src.utils.aqi import COMPUTED_NOTE, CAQIBand
from src.utils.metrics import get

# A rise in a pollutant is bad; climate/index measures are neutral.
_INVERSE_DELTA = {"pm2_5", "pm10_0", "co2"}

# CAQI level -> Streamlit badge color (reinforces the icon + label).
_BAND_BADGE = {0: "green", 1: "blue", 2: "orange", 3: "red", 4: "violet"}


def metric_tile(metric_key: str, value: float | None, delta: float | None) -> None:
    """Render one measure as a bordered ``st.metric`` tile."""
    metric = get(metric_key)
    label = f"{metric.icon} {metric.short_label}"
    value_str = metric.format(value)

    delta_str = None
    if delta is not None and value is not None:
        # Keep sign + unit so the change is self-describing; st.metric
        # derives the arrow direction from the leading sign.
        delta_str = f"{delta:+.{metric.decimals}f} {metric.unit}"

    if metric_key in _INVERSE_DELTA:
        delta_color = "inverse"  # up = worse = red
    else:
        delta_color = "off"  # neutral: arrow only, grey

    st.metric(
        label=label,
        value=value_str,
        delta=delta_str,
        delta_color=delta_color,
        help=f"{metric.label} · latest reading vs. mean of the previous 24 h.",
        border=True,
    )


def aqi_tile(band: CAQIBand | None) -> None:
    """Render the computed CAQI air-quality band as a tile."""
    with st.container(border=True):
        st.markdown(":material/speed: **Air quality**")
        if band is None:
            st.markdown(":gray-badge[:material/help: No data]")
            st.caption("No PM reading available.")
            return
        color = _BAND_BADGE.get(band.level, "gray")
        st.markdown(f":{color}-badge[{band.icon} {band.label}]")
        st.caption("CAQI · computed", help=COMPUTED_NOTE)
