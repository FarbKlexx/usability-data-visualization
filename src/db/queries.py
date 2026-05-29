"""Reusable SQL primitives and the sensor-table security allowlist.

Sensor measurements live in one table per device, named after its MAC
(``sensor_<mac>``). Because the table name varies at runtime it cannot
be passed as a bind parameter, so a naive f-string would be an SQL
injection hole. Instead we load the set of **real, existing** sensor
tables once from the catalog and validate every requested name against
it (plan §6.1). This both blocks injection and cleanly rejects the 8
registered-but-tableless ``m13``–``m20`` devices.

Everything here returns plain Python / pandas; the engine comes from
``src.db.get_engine``. Pages never import this directly — they go
through ``src.data`` loaders, which add the ``@st.cache_data`` layer.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy import text

from src.db.connection import get_engine

SCHEMA = "smartmonitoring"


@st.cache_data(show_spinner=False)
def sensor_table_allowlist() -> frozenset[str]:
    """All real ``sensor_*`` / ``ext_sensor_*`` tables that actually exist.

    Read once from ``pg_class`` and cached (the DB is frozen, so there is
    no TTL). This is the trust boundary for dynamic table names.
    """
    sql = text(
        """
        SELECT c.relname
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = :schema
          AND c.relkind = 'r'
          AND (c.relname LIKE 'sensor\\_%' OR c.relname LIKE 'ext\\_sensor%')
        """
    )
    with get_engine().connect() as conn:
        rows = conn.execute(sql, {"schema": SCHEMA}).scalars().all()
    return frozenset(rows)


def is_sensor_table(name: str) -> bool:
    """True if ``name`` is a known, existing sensor table."""
    return name in sensor_table_allowlist()


def safe_sensor_table(name: str) -> str:
    """Validate a sensor-table name and return it quoted+qualified.

    Raises ``ValueError`` for anything not in the allowlist, so callers
    can safely interpolate the result into SQL.
    """
    if not is_sensor_table(name):
        raise ValueError(
            f"Unknown or non-existent sensor table {name!r}. "
            "It must be one of the catalog-verified sensor tables."
        )
    return f'{SCHEMA}."{name}"'


def read_sql(sql: str, params: dict | None = None) -> pd.DataFrame:
    """Run a query and return a tidy DataFrame.

    ``sql`` may contain ``:name`` bind parameters (passed via ``params``).
    Any dynamic table name must already have been vetted with
    :func:`safe_sensor_table`.
    """
    with get_engine().connect() as conn:
        return pd.read_sql_query(text(sql), conn, params=params or {})
