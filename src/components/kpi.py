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


def metric_tile(
    metric_key: str,
    value: float | None,
    delta: float | None,
    value_desc: str = "latest reading",
    baseline_label: str = "previous 24 h",
) -> None:
    """Render one measure as a bordered ``st.metric`` tile.

    ``value_desc`` says what ``value`` is ("latest reading", or e.g.
    "7 d average"); ``baseline_label`` names the window the trend delta is
    measured against. Both track the caller's range so the tooltip never
    claims the wrong period.
    """
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

    help_text = f"{metric.label} · {value_desc}"
    if delta_str is not None:
        help_text += f" · trend vs. mean over {baseline_label}"
    st.metric(
        label=label,
        value=value_str,
        delta=delta_str,
        delta_color=delta_color,
        help=help_text + ".",
        border=True,
    )


def aqi_tile(band: CAQIBand | None) -> None:
    """Render the computed CAQI air-quality band as a metric tile.

    Rendered as a plain ``st.metric`` so the band word ("Very low") matches the
    measurement tiles beside it — no badge colour or sentiment icon. The
    colour/position encoding of the band lives on the hero meter instead.
    """
    st.metric(
        ":material/speed: Air quality",
        band.label if band is not None else "No data",
        help=f"CAQI · computed — {COMPUTED_NOTE}",
        border=True,
    )
