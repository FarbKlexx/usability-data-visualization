"""Data access layer.

Wraps every source of truth (Postgres dump in ``pgsql/``, CSV/Parquet
in ``assets/``, remote APIs) behind cached loader functions so pages
never touch I/O directly.
"""

from src.data.loaders import (
    available_metrics,
    build_comparison_frame,
    choose_bucket_seconds,
    dashboard_tables_ready,
    feature_enabled,
    load_annotations,
    load_comparison,
    load_devices,
    load_feature_flags,
    load_latest,
    load_locations,
    load_particle_sizes,
    load_raw_readings,
    load_reading_flags,
    load_routes,
    load_saved_views,
    load_thresholds,
    load_timeseries,
    load_tracks,
    segment_routes,
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
    "load_routes",
    "segment_routes",
    "load_particle_sizes",
    "available_metrics",
    "build_comparison_frame",
    "choose_bucket_seconds",
    "shape_of",
    # interactivity / user-content loaders (plan §B)
    "dashboard_tables_ready",
    "load_annotations",
    "load_reading_flags",
    "load_raw_readings",
    "load_thresholds",
    "load_saved_views",
    "load_feature_flags",
    "feature_enabled",
]
