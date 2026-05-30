"""Database access layer.

Exposes a cached SQLAlchemy engine for the air-quality Postgres
instance. Pages should not import psycopg or SQLAlchemy directly;
instead call ``get_engine()`` and pass the result to pandas or
queries defined in ``queries.py``.
"""

from src.db.connection import get_engine
from src.db.queries import (
    SCHEMA,
    is_sensor_table,
    read_sql,
    safe_sensor_table,
    sensor_table_allowlist,
)
from src.db.write import (
    DASHBOARD_TABLES,
    EDITABLE_TARGETS,
    add_annotation,
    add_reading_flag,
    delete_annotation,
    delete_reading_flag,
    delete_threshold,
    delete_view,
    execute,
    save_threshold,
    save_view,
    set_feature_flag,
    update_location,
    update_object,
    update_row,
)

__all__ = [
    "get_engine",
    "SCHEMA",
    "sensor_table_allowlist",
    "is_sensor_table",
    "safe_sensor_table",
    "read_sql",
    # write layer
    "execute",
    "update_row",
    "update_object",
    "update_location",
    "set_feature_flag",
    "add_annotation",
    "delete_annotation",
    "add_reading_flag",
    "delete_reading_flag",
    "save_threshold",
    "delete_threshold",
    "save_view",
    "delete_view",
    "EDITABLE_TARGETS",
    "DASHBOARD_TABLES",
]
