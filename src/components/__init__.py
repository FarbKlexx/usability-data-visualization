"""Reusable UI building blocks (KPI tiles, filter bars, empty-states).

A consistent component library is rule #1 in CONTEXT.md's practical
checklist — every screen should reuse the same primitives.
"""

from src.components import charts
from src.components.filter_bar import FilterState, device_label, filter_bar
from src.components.kpi import aqi_tile, metric_tile

__all__ = [
    "charts",
    "filter_bar",
    "FilterState",
    "device_label",
    "metric_tile",
    "aqi_tile",
]
