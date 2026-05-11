"""Standalone DB connectivity test.

Run with::

    uv run python scripts/check_db.py

Exits with status 0 on success, non-zero on any failure. Prints a
small smoke summary: current user, current database, a row count from
``tbl_observedobject``, and a sample row.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text  # noqa: E402

from src.db import get_engine  # noqa: E402


def main() -> int:
    engine = get_engine()
    try:
        with engine.connect() as conn:
            user, db = conn.execute(
                text("SELECT current_user, current_database()")
            ).one()
            n_oo = conn.execute(
                text("SELECT count(*) FROM smartmonitoring.tbl_observedobject")
            ).scalar_one()
            sample = conn.execute(
                text(
                    "SELECT id, name, mac "
                    "FROM smartmonitoring.tbl_observedobject "
                    "WHERE mac IS NOT NULL "
                    "ORDER BY id LIMIT 1"
                )
            ).one()
    except Exception as exc:  # noqa: BLE001 — this *is* the catch-all
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(f"connected as {user!r} -> database {db!r}")
    print(f"smartmonitoring.tbl_observedobject: {n_oo} rows")
    print(f"first observed object: id={sample.id}, name={sample.name!r}, mac={sample.mac}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
