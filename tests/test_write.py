"""Tests for the interactivity write layer (plan §B).

Mirrors ``test_smoke.py``: **pure** tests for the editable-target
allowlist (the write-side trust boundary — these need no DB and must
always hold) plus a **DB-gated** round-trip that inserts → reads →
deletes user content, skipping cleanly when Postgres is unreachable.
"""

from __future__ import annotations

from datetime import datetime

import pytest


# --- Pure: editable-target allowlist (security boundary) --------------------


def test_editable_targets_are_explicit() -> None:
    from src.db.write import EDITABLE_TARGETS

    # Only metadata tables are editable — never a measurement table.
    assert set(EDITABLE_TARGETS) == {
        "tbl_observedobject",
        "tbl_location",
        "tbl_systemconfiguration",
    }
    assert "name" in EDITABLE_TARGETS["tbl_observedobject"]
    # coordinates is intentionally NOT a plain editable column (geometry
    # goes through the ST_MakePoint path).
    assert "coordinates" not in EDITABLE_TARGETS["tbl_location"]


def test_update_row_rejects_unknown_table() -> None:
    from src.db.write import update_row

    with pytest.raises(ValueError):
        update_row("sensor_000aeb8337ac", 1, {"ts": "now"})  # measurement table


def test_update_row_rejects_unknown_column() -> None:
    from src.db.write import update_row

    with pytest.raises(ValueError):
        update_row("tbl_observedobject", 1, {"mac": "de:ad"})  # mac is not editable


def test_update_row_empty_fields_is_noop() -> None:
    from src.db.write import update_row

    assert update_row("tbl_observedobject", 1, {}) == 0


def test_annotation_rejects_non_sensor_target(db_or_skip) -> None:
    from src.db.write import add_annotation

    with pytest.raises(ValueError):
        add_annotation("not_a_sensor", datetime(2025, 1, 1), None, "x")


# --- DB-gated: full user-content round-trip ---------------------------------


@pytest.fixture(scope="session")
def db_or_skip():
    from sqlalchemy import text

    from src.db import get_engine

    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Postgres not reachable: {exc}")


def test_dashboard_tables_present(db_or_skip) -> None:
    from src.data import dashboard_tables_ready

    if not dashboard_tables_ready():
        pytest.skip("dashboard_* tables not migrated; run scripts/add_dashboard_tables.py")


def test_annotation_roundtrip(db_or_skip) -> None:
    from src.data import dashboard_tables_ready, load_annotations
    from src.db import add_annotation, delete_annotation

    if not dashboard_tables_ready():
        pytest.skip("dashboard_* tables not migrated")

    table = "sensor_000aeb8337ac"
    before = len(load_annotations(table))
    add_annotation(table, datetime(2025, 8, 1), datetime(2025, 8, 2), "pytest", "tmp")
    load_annotations.clear()
    df = load_annotations(table)
    assert len(df) == before + 1
    new_id = int(df.iloc[-1]["id"])
    delete_annotation(new_id)
    load_annotations.clear()
    assert len(load_annotations(table)) == before


def test_saved_view_jsonb_roundtrip(db_or_skip) -> None:
    from src.data import dashboard_tables_ready, load_saved_views
    from src.db import delete_view, save_view

    if not dashboard_tables_ready():
        pytest.skip("dashboard_* tables not migrated")

    params = {"table": "sensor_000aeb8337ac", "measures": ["pm2_5", "pm10_0"], "range": "7 d"}
    save_view("pytest view", params)
    load_saved_views.clear()
    views = load_saved_views()
    row = views.iloc[0]
    # JSONB comes back as a dict, structure intact.
    assert isinstance(row["params_json"], dict)
    assert row["params_json"]["measures"] == ["pm2_5", "pm10_0"]
    delete_view(int(row["id"]))
    load_saved_views.clear()
