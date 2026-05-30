"""Transactional write layer (interactivity plan §B0).

The read side treats the dump as frozen; this module is the *only* place
that writes back. It mirrors the read-side trust boundary
(:func:`src.db.safe_sensor_table`) with three rules:

* **Atomicity** — every write runs inside ``engine.begin()`` so it either
  fully commits or fully rolls back.
* **Editable-target allowlist** — :data:`EDITABLE_TARGETS` is the explicit
  map of ``{table: {editable columns}}``. Column names are never taken
  from user input verbatim; they are validated against this map and only
  then interpolated, while *values* always travel as bind parameters.
  Anything off the list raises before touching the database.
* **Cache invalidation** — after a successful write the relevant
  ``@st.cache_data`` loaders are cleared (scoped, via lazy import to
  avoid a circular dependency on ``src.data``), so the next rerun reads
  the new state.

Writes fall into two groups: edits to a few existing metadata tables and
inserts into the new ``dashboard_*`` user-content tables created by
``scripts/add_dashboard_tables.py``.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import streamlit as st
from sqlalchemy import text

from src.db.connection import get_engine
from src.db.queries import SCHEMA, is_sensor_table

# --- Editable-target allowlist ---------------------------------------------
# {table: editable columns}. `tbl_location.coordinates` is intentionally
# absent — geometry is written through a dedicated, parameterised path
# (ST_SetSRID/ST_MakePoint), never as a raw value.
EDITABLE_TARGETS: dict[str, frozenset[str]] = {
    "tbl_observedobject": frozenset({"name", "description", "icon", "datacapture"}),
    "tbl_location": frozenset({"name", "city", "street", "postcode"}),
    "tbl_systemconfiguration": frozenset({"active"}),
}

# The user-content tables this module may insert into / delete from. Created
# by the migration; we never write measurement tables.
DASHBOARD_TABLES: frozenset[str] = frozenset(
    {
        "dashboard_annotations",
        "dashboard_reading_flags",
        "dashboard_thresholds",
        "dashboard_saved_views",
    }
)

# Allowed values for a reading flag — validated at the write boundary, not
# only by the UI selectbox (mirrors the DDL's CHECK constraint).
READING_FLAGS: frozenset[str] = frozenset({"suspect", "confirmed", "ignore"})


# --- Low-level primitives ---------------------------------------------------


def execute(stmt: str, params: dict[str, Any] | None = None) -> int:
    """Run one statement in its own transaction; return affected rowcount.

    ``stmt`` may use ``:name`` bind parameters. Any table/column name it
    interpolates must already have been validated by the helpers below —
    only literals from :data:`EDITABLE_TARGETS` / the allowlists are ever
    interpolated, never raw user input.
    """
    with get_engine().begin() as conn:
        result = conn.execute(text(stmt), params or {})
        return result.rowcount if result.rowcount is not None else 0


def _validate_columns(table: str, columns: set[str] | frozenset[str]) -> frozenset[str]:
    """Validate a metadata edit target; return the allowed column set."""
    allowed = EDITABLE_TARGETS.get(table)
    if allowed is None:
        raise ValueError(
            f"Table {table!r} is not an editable target. "
            f"Allowed: {sorted(EDITABLE_TARGETS)}."
        )
    bad = set(columns) - allowed
    if bad:
        raise ValueError(
            f"Columns {sorted(bad)} are not editable on {table!r}. "
            f"Allowed: {sorted(allowed)}."
        )
    return allowed


def _clear_caches(*loader_names: str) -> None:
    """Clear specific ``@st.cache_data`` loaders by name (lazy import).

    Imported lazily so ``src.db`` never imports ``src.data`` at module
    load (that would be circular). Unknown names are ignored, so callers
    can be liberal.
    """
    try:
        from src.data import loaders
    except Exception:  # pragma: no cover - defensive
        st.cache_data.clear()
        return
    for name in loader_names:
        fn = getattr(loaders, name, None)
        clear = getattr(fn, "clear", None)
        if callable(clear):
            clear()


# --- Metadata edits (B1, B2, B3) -------------------------------------------


def update_row(table: str, row_id: int, fields: dict[str, Any]) -> int:
    """Validated ``UPDATE <table> SET ... WHERE id = :id`` (one row).

    ``fields`` keys are validated against :data:`EDITABLE_TARGETS`; empty
    ``fields`` is a no-op. Returns the affected rowcount.
    """
    if not fields:
        return 0
    _validate_columns(table, set(fields))
    assignments = ", ".join(f'"{col}" = :{col}' for col in fields)
    params = dict(fields)
    params["__id"] = row_id
    return execute(
        f"UPDATE {SCHEMA}.{table} SET {assignments} WHERE id = :__id", params
    )


def update_object(oo_id: int, fields: dict[str, Any]) -> int:
    """Edit device/place metadata on ``tbl_observedobject`` (plan §B1)."""
    n = update_row("tbl_observedobject", oo_id, fields)
    _clear_caches("load_devices", "_coverage")
    return n


def update_location(
    loc_id: int,
    fields: dict[str, Any] | None = None,
    *,
    lon: float | None = None,
    lat: float | None = None,
) -> int:
    """Edit address fields and/or the PostGIS point on ``tbl_location`` (§B2).

    Text fields go through the validated :func:`update_row`; coordinates
    are written via ``ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)`` so the
    geometry is always well-formed and SRID-tagged.
    """
    affected = 0
    if fields:
        affected += update_row("tbl_location", loc_id, fields)
    if lon is not None and lat is not None:
        affected += execute(
            f"""
            UPDATE {SCHEMA}.tbl_location
            SET coordinates = ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
            WHERE id = :loc_id
            """,
            {"lon": float(lon), "lat": float(lat), "loc_id": loc_id},
        )
    _clear_caches("load_devices", "load_locations")
    return affected


def set_feature_flag(ckey: str, active: bool) -> int:
    """Toggle a ``tbl_systemconfiguration`` feature flag by its key (§B3)."""
    n = execute(
        f"UPDATE {SCHEMA}.tbl_systemconfiguration SET active = :active WHERE ckey = :ckey",
        {"active": bool(active), "ckey": ckey},
    )
    _clear_caches("load_feature_flags")
    return n


# --- User content: annotations & reading flags (B4, B5) --------------------


def _require_sensor_table(table_name: str) -> None:
    """Reject anything not in the read-side sensor allowlist."""
    if not is_sensor_table(table_name):
        raise ValueError(
            f"{table_name!r} is not a known sensor table; refusing to attach "
            "user content to it."
        )


def add_annotation(
    table_name: str,
    ts_from: datetime,
    ts_to: datetime | None,
    label: str,
    note: str = "",
) -> int:
    """Insert a time-range annotation for a sensor (plan §B4).

    ``ts_to`` may be ``None`` for a point annotation. The measurement
    tables are never touched — annotations live in their own table.
    """
    _require_sensor_table(table_name)
    n = execute(
        f"""
        INSERT INTO {SCHEMA}.dashboard_annotations (mac, ts_from, ts_to, label, note)
        VALUES (:mac, :ts_from, :ts_to, :label, :note)
        """,
        {"mac": table_name, "ts_from": ts_from, "ts_to": ts_to, "label": label, "note": note},
    )
    _clear_caches("load_annotations")
    return n


def delete_annotation(annotation_id: int) -> int:
    """Remove an annotation (reversibility, Shneiderman #6)."""
    n = execute(
        f"DELETE FROM {SCHEMA}.dashboard_annotations WHERE id = :id",
        {"id": annotation_id},
    )
    _clear_caches("load_annotations")
    return n


def add_reading_flag(table_name: str, reading_id: int, flag: str, note: str = "") -> int:
    """Flag a single reading without altering the source row (plan §B5)."""
    _require_sensor_table(table_name)
    if flag not in READING_FLAGS:
        raise ValueError(f"Flag {flag!r} must be one of {sorted(READING_FLAGS)}.")
    n = execute(
        f"""
        INSERT INTO {SCHEMA}.dashboard_reading_flags (table_name, reading_id, flag, note)
        VALUES (:table_name, :reading_id, :flag, :note)
        """,
        {"table_name": table_name, "reading_id": int(reading_id), "flag": flag, "note": note},
    )
    _clear_caches("load_reading_flags")
    return n


def delete_reading_flag(flag_id: int) -> int:
    """Remove a reading flag."""
    n = execute(
        f"DELETE FROM {SCHEMA}.dashboard_reading_flags WHERE id = :id",
        {"id": flag_id},
    )
    _clear_caches("load_reading_flags")
    return n


# --- Persisted UI state: thresholds & saved views (B6) ---------------------


def save_threshold(metric: str, value: float, label: str = "") -> int:
    """Persist a metric threshold so it survives sessions (plan §B6)."""
    n = execute(
        f"""
        INSERT INTO {SCHEMA}.dashboard_thresholds (metric, value, label)
        VALUES (:metric, :value, :label)
        """,
        {"metric": metric, "value": float(value), "label": label},
    )
    _clear_caches("load_thresholds")
    return n


def delete_threshold(threshold_id: int) -> int:
    """Remove a persisted threshold."""
    n = execute(
        f"DELETE FROM {SCHEMA}.dashboard_thresholds WHERE id = :id",
        {"id": threshold_id},
    )
    _clear_caches("load_thresholds")
    return n


def save_view(name: str, params: dict[str, Any]) -> int:
    """Persist a named saved view (A7 → B6); ``params`` stored as JSONB.

    The ``table`` entry (if present) is validated against the sensor
    allowlist so a view can only ever point at a real sensor — the same
    trust boundary the read path enforces, applied here at write time.
    """
    table = params.get("table")
    if table is not None and not is_sensor_table(str(table)):
        raise ValueError(f"Saved view references unknown sensor table {table!r}.")
    n = execute(
        f"""
        INSERT INTO {SCHEMA}.dashboard_saved_views (name, params_json)
        VALUES (:name, CAST(:params AS jsonb))
        """,
        {"name": name, "params": json.dumps(params)},
    )
    _clear_caches("load_saved_views")
    return n


def delete_view(view_id: int) -> int:
    """Remove a saved view."""
    n = execute(
        f"DELETE FROM {SCHEMA}.dashboard_saved_views WHERE id = :id",
        {"id": view_id},
    )
    _clear_caches("load_saved_views")
    return n
