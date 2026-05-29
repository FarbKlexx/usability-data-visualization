"""Data access layer.

Wraps every source of truth (Postgres dump in ``pgsql/``, CSV/Parquet
in ``assets/``, remote APIs) behind cached loader functions so pages
never touch I/O directly.
"""

from src.data.loaders import (
    available_metrics,
    choose_bucket_seconds,
    load_comparison,
    load_devices,
    load_latest,
    load_locations,
    load_particle_sizes,
    load_timeseries,
    load_tracks,
    sensors_with_data,
    shape_of,
)

__all__ = [
    "load_devices",
    "sensors_with_data",
    "load_latest",
    "load_timeseries",
    "load_comparison",
    "load_locations",
    "load_tracks",
    "load_particle_sizes",
    "available_metrics",
    "choose_bucket_seconds",
    "shape_of",
]
