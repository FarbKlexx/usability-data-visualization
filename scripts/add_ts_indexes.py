"""Idempotent, reversible ``ts`` index migration (implementation plan §6.4).

No sensor table ships a usable ``ts`` index, so every time-range query
(KPI "latest", time-series, comparison) is a full scan over up to ~248k
rows. Since the working copy (``pgdata/``) is mutable, we add a btree
index on ``ts`` for each populated sensor table. This brings
time-range queries and ``ORDER BY ts DESC LIMIT 1`` under the
<100 ms feedback budget (CONTEXT). Server-side downsampling + the
``@st.cache_data`` TTL stay active as a second layer regardless.

Usage::

    uv run python scripts/add_ts_indexes.py          # create indexes
    uv run python scripts/add_ts_indexes.py --drop    # reverse (idempotent)
    uv run python scripts/add_ts_indexes.py --dry-run  # show plan only

Both directions use ``IF [NOT] EXISTS`` so re-runs are no-ops. Indexes
are named ``ix_<table>_ts`` so they are easy to spot and drop.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text  # noqa: E402

from src.db import SCHEMA, get_engine, sensor_table_allowlist  # noqa: E402


def _index_name(table: str) -> str:
    return f"ix_{table}_ts"


def _populated_sensor_tables(conn) -> list[str]:
    """Sensor tables that have a ``ts`` column and at least one row."""
    tables = sorted(sensor_table_allowlist())
    has_ts = set(
        conn.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.columns
                WHERE table_schema = :schema AND column_name = 'ts'
                """
            ),
            {"schema": SCHEMA},
        ).scalars()
    )
    populated: list[str] = []
    for tbl in tables:
        if tbl not in has_ts:
            continue
        # EXISTS is cheap even without an index — stops at the first row.
        exists = conn.execute(
            text(f'SELECT EXISTS (SELECT 1 FROM {SCHEMA}."{tbl}")')
        ).scalar_one()
        if exists:
            populated.append(tbl)
    return populated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--drop", action="store_true", help="drop the indexes instead of creating them")
    parser.add_argument("--dry-run", action="store_true", help="print statements without executing")
    args = parser.parse_args()

    engine = get_engine()
    try:
        with engine.begin() as conn:
            tables = _populated_sensor_tables(conn)
            verb = "DROP" if args.drop else "CREATE"
            print(f"{verb} ts index for {len(tables)} populated sensor table(s):")
            for tbl in tables:
                idx = _index_name(tbl)
                if args.drop:
                    stmt = f'DROP INDEX IF EXISTS {SCHEMA}."{idx}"'
                else:
                    stmt = f'CREATE INDEX IF NOT EXISTS "{idx}" ON {SCHEMA}."{tbl}" (ts)'
                print(f"  {tbl:<28} {stmt}")
                if not args.dry_run:
                    conn.execute(text(stmt))
    except Exception as exc:  # noqa: BLE001 - report and fail clearly
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print("dry-run: nothing executed.")
    else:
        print("done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
