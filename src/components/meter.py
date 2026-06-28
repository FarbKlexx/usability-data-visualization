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


def air_quality_meter(
    position: float,
    dot_color: str,
    ticks: tuple[float, ...] = (0.25, 0.5, 0.75),
    zone_labels: tuple[tuple[float, str], ...] = (),
) -> None:
    """Render the meter. ``position`` is 0 (worst, red/left) .. 1 (best, green/right).

    ``dot_color`` fills the marker (the CAQI band colour) inside a white ring so
    it stays legible at any point along the gradient. ``ticks`` are fractional
    positions (0..1) for subtle, neutral band-boundary marks — by default the
    three interior CAQI band boundaries (the bar's quarter points), so the scale
    shows *where the air-quality thresholds sit*, not just where this reading is.
    ``zone_labels`` are ``(centre 0..1, word)`` pairs printed in small grey above
    the bar to name each zone (e.g. Good … Poor), so the scale reads without a
    legend. Pass ``ticks=()`` / ``zone_labels=()`` to omit either.
    """
    pct = max(0.0, min(1.0, position)) * 100.0
    marks = "".join(
        f"<div class='aq-meter-tick' style='left:{max(0.0, min(1.0, t)) * 100:.1f}%'></div>"
        for t in ticks
    )
    labels = ""
    if zone_labels:
        spans = "".join(
            f"<span class='aq-meter-zone' style='left:{max(0.0, min(1.0, c)) * 100:.1f}%'>{txt}</span>"
            for c, txt in zone_labels
        )
        labels = f"<div class='aq-meter-labels'>{spans}</div>"
    st.html(
        "<div class='aq-meter-wrap'>"
        + labels
        + "<div class='aq-meter'>"
        + marks
        + f"<div class='aq-meter-dot' style='left:{pct:.1f}%;background:{dot_color}'></div>"
        + "</div>"
        + "</div>"
    )
