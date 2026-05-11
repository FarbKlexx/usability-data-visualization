"""Colorblind-safe palette tokens.

CONTEXT.md §Perception: ~8% of men have a color vision deficiency, so
color must never be the sole carrier of information. These palettes
are designed to be distinguishable under deuteranopia / protanopia.

Source: Okabe & Ito, 2008 — https://jfly.uni-koeln.de/color/
"""

from __future__ import annotations

OKABE_ITO: tuple[str, ...] = (
    "#000000",  # black
    "#E69F00",  # orange
    "#56B4E9",  # sky blue
    "#009E73",  # bluish green
    "#F0E442",  # yellow
    "#0072B2",  # blue
    "#D55E00",  # vermillion
    "#CC79A7",  # reddish purple
)

VIRIDIS_DISCRETE: tuple[str, ...] = (
    "#440154",
    "#3B528B",
    "#21908C",
    "#5DC863",
    "#FDE725",
)
