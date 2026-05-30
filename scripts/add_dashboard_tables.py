"""Idempotent migration for the user-content tables (interactivity plan §B7).

The interactivity layer lets users write back to the database. To keep
the measurement data untouched, all user-generated content lives in four
new ``dashboard_*`` tables in the ``smartmonitoring`` schema:

* ``dashboard_annotations``   — notes on time ranges (plan §B4)
* ``dashboard_reading_flags`` — per-reading flags, e.g. 'suspect' (§B5)
* ``dashboard_thresholds``    — persisted metric thresholds (§B6)
* ``dashboard_saved_views``   — named filter states as JSONB (§A7 → B6)

Usage::

    uv run python scripts/add_dashboard_tables.py            # create
    uv run python scripts/add_dashboard_tables.py --drop     # reverse
    uv run python scripts/add_dashboard_tables.py --dry-run  # show plan

All statements use ``IF [NOT] EXISTS`` so re-runs after ``git clone`` are
safe no-ops. ``--drop`` is provided for a clean reset; it removes only
these four tables and never any measurement table.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text  # noqa: E402

from src.db import SCHEMA, get_engine  # noqa: E402

# Order matters only for drop readability; there are no FKs between them.
TABLES: tuple[str, ...] = (
    "dashboard_annotations",
    "dashboard_reading_flags",
    "dashboard_thresholds",
    "dashboard_saved_views",
)

CREATE_STATEMENTS: dict[str, str] = {
    "dashboard_annotations": f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA}.dashboard_annotations (
            id          bigserial PRIMARY KEY,
            mac         varchar      NOT NULL,   -- sensor table_name (canonical key)
            ts_from     timestamp    NOT NULL,
            ts_to       timestamp,               -- NULL = point annotation
            label       varchar      NOT NULL,
            note        text,
            created_at  timestamp    NOT NULL DEFAULT now()
        )
    """,
    "dashboard_reading_flags": f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA}.dashboard_reading_flags (
            id          bigserial PRIMARY KEY,
            table_name  varchar      NOT NULL,   -- validated against the read allowlist
            reading_id  bigint       NOT NULL,   -- id within that sensor table
            flag        varchar      NOT NULL
                CONSTRAINT dashboard_reading_flags_flag_chk
                CHECK (flag IN ('suspect', 'confirmed', 'ignore')),
            note        text,
            created_at  timestamp    NOT NULL DEFAULT now()
        )
    """,
    "dashboard_thresholds": f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA}.dashboard_thresholds (
            id          bigserial PRIMARY KEY,
            metric      varchar      NOT NULL,
            value       float8       NOT NULL,
            label       varchar,
            created_at  timestamp    NOT NULL DEFAULT now()
        )
    """,
    "dashboard_saved_views": f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA}.dashboard_saved_views (
            id           bigserial PRIMARY KEY,
            name         varchar     NOT NULL,
            params_json  jsonb       NOT NULL,
            created_at   timestamp   NOT NULL DEFAULT now()
        )
    """,
}

# Helpful secondary indexes for the read paths (annotations by sensor,
# flags by table). Idempotent.
INDEX_STATEMENTS: tuple[str, ...] = (
    f'CREATE INDEX IF NOT EXISTS ix_dashboard_annotations_mac '
    f"ON {SCHEMA}.dashboard_annotations (mac)",
    f'CREATE INDEX IF NOT EXISTS ix_dashboard_reading_flags_table '
    f"ON {SCHEMA}.dashboard_reading_flags (table_name, reading_id)",
)

# Idempotently add the flag CHECK to tables created before the constraint
# existed (Postgres has no ADD CONSTRAINT IF NOT EXISTS, so guard on catalog).
CONSTRAINT_STATEMENTS: tuple[str, ...] = (
    f"""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint
            WHERE conname = 'dashboard_reading_flags_flag_chk'
        ) THEN
            ALTER TABLE {SCHEMA}.dashboard_reading_flags
                ADD CONSTRAINT dashboard_reading_flags_flag_chk
                CHECK (flag IN ('suspect', 'confirmed', 'ignore'));
        END IF;
    END $$;
    """,
)

# Dashboard-owned feature flags seeded into tbl_systemconfiguration (plan §B3).
# These let the Manage page toggle optional dashboard modules on/off as a live
# configuration surface. Seeded idempotently (the table has no unique key on
# ckey, so we guard with NOT EXISTS) and removed again on --drop.
FEATURE_FLAGS: tuple[tuple[str, str], ...] = (
    ("func_dashboard_particle_drilldown", "Particle-size drill-down (Time Series, hi-res sensor)"),
    ("func_dashboard_annotations", "Annotation panel on the Time Series page"),
    ("func_dashboard_raw_inspector", "Raw-reading inspector + flagging (Time Series)"),
)


def _seed_feature_flags(conn) -> int:
    seeded = 0
    for ckey, label in FEATURE_FLAGS:
        n = conn.execute(
            text(
                f"""
                INSERT INTO {SCHEMA}.tbl_systemconfiguration (ckey, ctype, cvalue, active)
                SELECT CAST(:ckey AS varchar), 'feature', CAST(:label AS varchar), true
                WHERE NOT EXISTS (
                    SELECT 1 FROM {SCHEMA}.tbl_systemconfiguration WHERE ckey = CAST(:ckey AS varchar)
                )
                """
            ),
            {"ckey": ckey, "label": label},
        ).rowcount
        seeded += n or 0
    return seeded


def _remove_feature_flags(conn) -> int:
    keys = [ckey for ckey, _ in FEATURE_FLAGS]
    return (
        conn.execute(
            text(f"DELETE FROM {SCHEMA}.tbl_systemconfiguration WHERE ckey = ANY(:keys)"),
            {"keys": keys},
        ).rowcount
        or 0
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--drop", action="store_true", help="drop the tables instead of creating them")
    parser.add_argument("--dry-run", action="store_true", help="print statements without executing")
    args = parser.parse_args()

    engine = get_engine()
    try:
        with engine.begin() as conn:
            if args.drop:
                print(f"DROP {len(TABLES)} dashboard table(s) + {len(FEATURE_FLAGS)} feature flag(s):")
                for tbl in reversed(TABLES):
                    stmt = f"DROP TABLE IF EXISTS {SCHEMA}.{tbl} CASCADE"
                    print(f"  {tbl:<26} {stmt}")
                    if not args.dry_run:
                        conn.execute(text(stmt))
                if not args.dry_run:
                    removed = _remove_feature_flags(conn)
                    print(f"  removed {removed} dashboard feature flag(s)")
            else:
                print(f"CREATE {len(TABLES)} dashboard table(s) + indexes + feature flags:")
                for tbl in TABLES:
                    print(f"  {tbl}")
                    if not args.dry_run:
                        conn.execute(text(CREATE_STATEMENTS[tbl]))
                for stmt in INDEX_STATEMENTS:
                    print(f"  idx: {stmt.split('ix_', 1)[1].split(' ', 1)[0]}")
                    if not args.dry_run:
                        conn.execute(text(stmt))
                for stmt in CONSTRAINT_STATEMENTS:
                    print("  constraint: dashboard_reading_flags_flag_chk")
                    if not args.dry_run:
                        conn.execute(text(stmt))
                if not args.dry_run:
                    seeded = _seed_feature_flags(conn)
                    print(f"  seeded {seeded} new dashboard feature flag(s) "
                          f"({len(FEATURE_FLAGS)} total, idempotent)")
    except Exception as exc:  # noqa: BLE001 - report and fail clearly
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print("dry-run: nothing executed." if args.dry_run else "done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
