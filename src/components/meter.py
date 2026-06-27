"""Air-quality meter — a slim red→green bar with a marker for the current value.

Usability rationale (CONTEXT.md §Perception / §Color): the verdict word ("Good",
"Poor") tells you *what* the air quality is; this meter shows *where on the scale*
it sits, so a value reads as "just into the good zone" vs. "almost the best
possible" rather than collapsing to one label. Colour is **never** the only
channel — the marker's horizontal **position** carries the same information as the
red→green hue, and the heading word states it in text, so a colour-blind reader
loses nothing (the bar's left=worst / right=best ordering is the real signal).

Mechanics: same documented ``st.html`` escape hatch as ``skeleton.py`` — the
static look (slim height, pill rounding, the fixed red→amber→green gradient,
marker size + white ring) lives in the global CSS in ``app.py`` (the ``.aq-meter*``
classes, theme-safe); only the two per-value bits — the marker's ``left`` offset
and its fill colour — travel inline, exactly like the skeleton blocks' inline
dimensions. Streamlit ships no such widget and the config exposes no token for it.
"""

from __future__ import annotations

import streamlit as st


def air_quality_meter(position: float, dot_color: str) -> None:
    """Render the meter. ``position`` is 0 (worst, red/left) .. 1 (best, green/right).

    ``dot_color`` fills the marker (the CAQI band colour) inside a white ring so
    it stays legible at any point along the gradient.
    """
    pct = max(0.0, min(1.0, position)) * 100.0
    st.html(
        "<div class='aq-meter'>"
        f"<div class='aq-meter-dot' style='left:{pct:.1f}%;background:{dot_color}'></div>"
        "</div>"
    )
