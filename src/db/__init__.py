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

__all__ = [
    "get_engine",
    "SCHEMA",
    "sensor_table_allowlist",
    "is_sensor_table",
    "safe_sensor_table",
    "read_sql",
]
