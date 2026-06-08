"""Cached data loaders for the air-quality dashboard (implementation plan §6.2).

Pages never touch the DB directly — they call these loaders, which:

* validate every dynamic table name against the catalog allowlist
  (``src.db.safe_sensor_table``), so table names are injection-safe;
* clean saturation sentinels **server-side** (so a 999.9 ceiling can
  never poison a downsampled average), and report how many were hidden
  so the UI can disclose it honestly (CONTEXT ethics);
* downsample large time ranges in SQL (the DB has no native ``ts`` index
  beyond the one we add in ``scripts/add_ts_indexes.py``, and even with
  it we never ship 248k raw points to the browser);
* return tidy ``pandas.DataFrame`` objects with documented columns.

Each loader is wrapped in ``@st.cache_data``; the dataset is frozen, so
TTLs are generous and exist mainly to bound memory.

Shapes (see ``docs/data_schema_full.md`` §E):
    A   — SENSORpi (pm2_5, pm10_0, co2, temp1, inn_*)        canonical
    B   — hi-res PM (mass_pm*/number_pm*), pos axis-swapped   sensor_781c3ce6ad3c
    C   — Polish external (caqi, pm*, climate)                sensor_pollish_external
    Ext — sensor.community import (pm only, sparse)           ext_sensor_47589
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from src.db import SCHEMA, is_sensor_table, read_sql, safe_sensor_table, sensor_table_allowlist
from src.utils.metrics import METRICS, Metric, get

# --- Shape / column resolution ---------------------------------------------

_SHAPE_B = "sensor_781c3ce6ad3c"
_SHAPE_C = "sensor_pollish_external"

# Specialty / external tables that own no tbl_observedobject row (plan §1,
# schema §D.1). Hand-curated display metadata + their fixed coordinates
# (lon, lat) — the DB is frozen, so these are stable. 781c3ce6ad3c is
# axis-swapped in storage; the coords below are already corrected.
SPECIALTY_TABLES: dict[str, dict] = {
    "sensor_781c3ce6ad3c": {
        "name": "Hi-res PM sensor",
        "ootype": "Specialty",
        "city": "Gdańsk",
        "country": "PL",
        "lon": 18.5753,
        "lat": 54.4109,
    },
    "sensor_pollish_external": {
        "name": "Gdańsk station (CAQI feed)",
        "ootype": "External",
        "city": "Gdańsk",
        "country": "PL",
        "lon": 18.6466,
        "lat": 54.3520,
    },
    "ext_sensor_47589": {
        "name": "Hannover (sensor.community)",
        "ootype": "External",
        "city": "Hannover",
        "country": "DE",
        "lon": 9.0560,
        "lat": 52.2980,
    },
}

_OOTYPE_LABEL = {1: "POI", 2: "Stationary", 3: "Mobile"}

# Normalize a MAC to its table suffix: lower-case, strip -/:/. separators
# (plan §1.3 quirks #6/#7).
_MAC_STRIP = str.maketrans("", "", "-:.")


def shape_of(table: str) -> str:
    """Classify a sensor table into its column shape (A/B/C/Ext)."""
    if table == _SHAPE_B:
        return "B"
    if table == _SHAPE_C:
        return "C"
    if table.startswith("ext_sensor"):
        return "Ext"
    return "A"


@st.cache_data(ttl=3600, show_spinner=False)
def _columns_of(table: str) -> frozenset[str]:
    """The set of column names on a (validated) sensor table."""
    safe_sensor_table(table)  # validate against the allowlist; raises on unknown
    rows = read_sql(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = :schema AND table_name = :table
        """,
        {"schema": SCHEMA, "table": table},
    )
    return frozenset(rows["column_name"])


def available_metrics(table: str) -> list[tuple[Metric, str]]:
    """Metrics displayable for a table, as ``(Metric, db_column)`` pairs.

    Resolves each registry metric to its column on this shape and keeps
    only those that physically exist (e.g. PM maps to ``mass_pm2_5`` on
    shape B; CO₂/climate are simply absent there).
    """
    shape = shape_of(table)
    cols = _columns_of(table)
    out: list[tuple[Metric, str]] = []
    for metric in METRICS.values():
        col = metric.column_for(shape)
        if col in cols:
            out.append((metric, col))
    return out


def _clean_expr(col: str, metric: Metric, alias: str | None = None) -> str:
    """SQL expression that nulls out a sentinel reading before aggregation.

    ``alias`` qualifies the column (e.g. ``t."pm2_5"``) for queries where
    the bare name would be ambiguous across joined relations.
    """
    ref = f'{alias}."{col}"' if alias else f'"{col}"'
    if metric.sentinel is None:
        return ref
    return f"CASE WHEN {ref} >= {metric.sentinel} THEN NULL ELSE {ref} END"


# --- Device catalog ---------------------------------------------------------


@st.cache_data(ttl=3600, show_spinner=False)
def _coverage() -> pd.DataFrame:
    """Per-table row count and ts span for every existing sensor table."""
    tables = sorted(sensor_table_allowlist())
    if not tables:
        return pd.DataFrame(columns=["table_name", "n_rows", "first_ts", "last_ts"])
    parts, params = [], {}
    for i, t in enumerate(tables):
        safe = safe_sensor_table(t)
        params[f"t{i}"] = t
        parts.append(
            f"SELECT :t{i} AS table_name, count(*) AS n_rows, "
            f"min(ts) AS first_ts, max(ts) AS last_ts FROM {safe}"
        )
    return read_sql(" UNION ALL ".join(parts), params)


@st.cache_data(ttl=3600, show_spinner="Loading device catalog…")
def load_devices() -> pd.DataFrame:
    """Device & place catalog — the basis for every selector and the map.

    One row per registered observed-object (joined to its type and
    location) plus the three unregistered specialty/external tables.

    Columns:
        oo_id, name, ootype, mac, table_name, table_exists, has_data,
        n_rows, first_ts, last_ts, shape, is_mobile, city, country,
        lon, lat
    """
    oo = read_sql(
        f"""
        SELECT oo.id AS oo_id, oo.name, oo.ootype_id, oo.mac,
               oo.description, oo.icon, oo.datacapture,
               lj.loc_id, loc.city, loc.country, loc.street, loc.postcode,
               ST_X(loc.coordinates) AS lon, ST_Y(loc.coordinates) AS lat
        FROM {SCHEMA}.tbl_observedobject oo
        LEFT JOIN {SCHEMA}.tbl_location_join_oo lj ON lj.oo_id = oo.id
        LEFT JOIN {SCHEMA}.tbl_location loc ON loc.id = lj.loc_id
        ORDER BY oo.id
        """
    )
    oo["ootype"] = oo["ootype_id"].map(_OOTYPE_LABEL).fillna("Other")
    # MAC -> table name (lower, strip separators); plan §1.3 quirks #6/#7.
    oo["table_name"] = oo["mac"].apply(
        lambda m: f"sensor_{str(m).lower().translate(_MAC_STRIP)}" if pd.notna(m) else None
    )

    allow = sensor_table_allowlist()
    cov = _coverage().set_index("table_name")

    # Append the unregistered specialty/external tables as catalog rows.
    extra = []
    linked = set(oo["table_name"].dropna())
    for tbl, meta in SPECIALTY_TABLES.items():
        if tbl in allow and tbl not in linked:
            extra.append(
                {
                    "oo_id": pd.NA,
                    "name": meta["name"],
                    "ootype_id": pd.NA,
                    "ootype": meta["ootype"],
                    "mac": None,
                    "city": meta["city"],
                    "country": meta["country"],
                    "lon": meta["lon"],
                    "lat": meta["lat"],
                    "table_name": tbl,
                }
            )
    devices = pd.concat([oo, pd.DataFrame(extra)], ignore_index=True) if extra else oo

    # na_action="ignore" leaves rows with no table_name as NA instead of
    # calling the mapper on a NaN (pandas 3.0 Arrow strings store None as NA).
    devices["table_exists"] = devices["table_name"].isin(allow)
    devices["n_rows"] = (
        devices["table_name"]
        .map(lambda t: int(cov["n_rows"].get(t, 0)), na_action="ignore")
        .fillna(0)
        .astype(int)
    )
    devices["first_ts"] = devices["table_name"].map(lambda t: cov["first_ts"].get(t), na_action="ignore")
    devices["last_ts"] = devices["table_name"].map(lambda t: cov["last_ts"].get(t), na_action="ignore")
    devices["has_data"] = devices["n_rows"] > 0
    # Named table_shape (not "shape") to avoid colliding with DataFrame.shape.
    devices["table_shape"] = devices["table_name"].map(shape_of, na_action="ignore")
    devices["is_mobile"] = devices["ootype"] == "Mobile"

    return devices.drop(columns=["ootype_id"])


def sensors_with_data() -> pd.DataFrame:
    """Catalog rows that actually have measurements (drives selectors)."""
    devices = load_devices()
    return devices[devices["has_data"]].copy()


# --- Latest snapshot (KPI tiles) -------------------------------------------


@st.cache_data(ttl=600, show_spinner=False)
def load_latest(
    table: str, baseline_seconds: int | None = 86400
) -> tuple[pd.DataFrame, pd.Timestamp | None]:
    """Latest reading per metric + a trend delta (KPI tiles, plan §6.2).

    Returns ``(long_df, latest_ts)`` where ``long_df`` has one row per
    available metric with columns ``metric, value, delta`` (delta =
    latest − mean over the baseline window, sentinels excluded). Empty
    frame if the table has no rows.

    ``baseline_seconds`` sets the trend baseline window ending at the
    latest reading: e.g. ``86400`` = vs. the previous 24 h (default),
    ``604800`` = vs. the previous 7 d. ``None`` compares against the mean
    of **all** earlier readings (used for the "All" range). The caller is
    responsible for labelling the window so the displayed trend stays
    honest.
    """
    safe = safe_sensor_table(table)
    pairs = available_metrics(table)
    if not pairs:
        return pd.DataFrame(columns=["metric", "value", "delta"]), None

    base_cols = ", ".join(f'avg({_clean_expr(col, m, alias="t")}) AS {m.key}_base' for m, col in pairs)

    # latest = newest row (sentinels nulled); base = mean over the baseline
    # window (sentinels excluded). delta = latest − base = the KPI trend arrow.
    if baseline_seconds is None:
        base_where, params = "t.ts < l.ts", {}
    else:
        base_where = "t.ts >= l.ts - (:base_secs * interval '1 second') AND t.ts < l.ts"
        params = {"base_secs": int(baseline_seconds)}
    sql = f"""
        WITH latest AS (
            SELECT ts, {", ".join(f'{_clean_expr(col, m)} AS {m.key}' for m, col in pairs)}
            FROM {safe} ORDER BY ts DESC LIMIT 1
        ),
        base AS (
            SELECT {base_cols}
            FROM {safe} t, latest l
            WHERE {base_where}
        )
        SELECT latest.*, base.* FROM latest CROSS JOIN base
    """
    df = read_sql(sql, params)
    if df.empty:
        return pd.DataFrame(columns=["metric", "value", "delta"]), None

    row = df.iloc[0]
    latest_ts = pd.to_datetime(row["ts"]) if pd.notna(row["ts"]) else None
    records = []
    for m, _ in pairs:
        value = row.get(m.key)
        base = row.get(f"{m.key}_base")
        value = None if pd.isna(value) else float(value)
        delta = None if (value is None or pd.isna(base)) else value - float(base)
        records.append({"metric": m.key, "value": value, "delta": delta})
    return pd.DataFrame.from_records(records), latest_ts


@st.cache_data(ttl=600, show_spinner=False)
def load_range_summary(
    table: str, start: datetime, end: datetime
) -> tuple[pd.DataFrame, pd.Timestamp | None, pd.Timestamp | None]:
    """Per-metric **mean over [start, end)** + a period-over-period delta.

    The dashboard KPI strip uses this so the tiles reflect the selected
    time range (a 7-day pick shows the 7-day average), not a fixed
    snapshot. ``value`` is the sentinel-cleaned mean over the window;
    ``delta`` compares it to the mean over the **previous** equal-length
    window ``[start - (end - start), start)``.

    **Fallback baseline.** When that immediately-preceding window holds *no*
    readings — a gap in the record (e.g. picking "24 h" when the device went
    quiet for the prior days) — the delta would otherwise vanish. Instead we
    fall back to the most recent equal-length window that *does* have data:
    the one ending at the last reading before ``start``. ``baseline_end`` is
    returned ``None`` for the normal contiguous case (and when there is simply
    no prior reading at all, e.g. the "All" range), or the end of the fallback
    window when the comparison was shifted — so the UI can label the shifted
    baseline honestly ("previous 24 h *with data*").

    Returns ``(long_df[metric, value, delta], latest_ts, baseline_end)``.
    """
    safe = safe_sensor_table(table)
    pairs = available_metrics(table)
    if not pairs:
        return pd.DataFrame(columns=["metric", "value", "delta"]), None, None

    window = end - start
    prev_start = start - window
    cur_cols = ", ".join(
        f"avg({_clean_expr(col, m)}) FILTER (WHERE ts >= :start AND ts < :end) AS {m.key}"
        for m, col in pairs
    )
    prev_cols = ", ".join(
        f"avg({_clean_expr(col, m)}) FILTER (WHERE ts >= :pstart AND ts < :start) AS {m.key}_prev"
        for m, col in pairs
    )
    sql = f"""
        SELECT max(ts) FILTER (WHERE ts >= :start AND ts < :end) AS _last,
               count(*) FILTER (WHERE ts >= :pstart AND ts < :start) AS _prev_n,
               {cur_cols}, {prev_cols}
        FROM {safe}
        WHERE ts >= :pstart AND ts < :end
    """
    df = read_sql(sql, {"start": start, "end": end, "pstart": prev_start})
    if df.empty:
        return pd.DataFrame(columns=["metric", "value", "delta"]), None, None

    row = df.iloc[0]
    latest_ts = pd.to_datetime(row["_last"]) if pd.notna(row["_last"]) else None

    # If the immediately-preceding window held nothing, compare against the
    # most recent equal-length window that does have data (the one ending at
    # the last reading before `start`). Two cheap, index-backed extra queries,
    # only on the gap path.
    baseline_end: pd.Timestamp | None = None
    fb: dict[str, float] = {}
    if int(row["_prev_n"] or 0) == 0:
        pl = read_sql(f"SELECT max(ts) AS prev_last FROM {safe} WHERE ts < :start", {"start": start})
        prev_last = (
            pd.to_datetime(pl.iloc[0]["prev_last"])
            if not pl.empty and pd.notna(pl.iloc[0]["prev_last"]) else None
        )
        if prev_last is not None:
            baseline_end = prev_last
            fb_cols = ", ".join(
                f"avg({_clean_expr(col, m)}) FILTER (WHERE ts >= :bstart AND ts < :bend) AS {m.key}"
                for m, col in pairs
            )
            fbdf = read_sql(
                f"SELECT {fb_cols} FROM {safe} WHERE ts >= :bstart AND ts < :bend",
                {"bstart": (prev_last - window).to_pydatetime(), "bend": prev_last.to_pydatetime()},
            )
            if not fbdf.empty:
                fb = {m.key: fbdf.iloc[0].get(m.key) for m, _ in pairs}

    records = []
    for m, _ in pairs:
        value = row.get(m.key)
        value = None if pd.isna(value) else float(value)
        prev = fb.get(m.key) if baseline_end is not None else row.get(f"{m.key}_prev")
        delta = None if (value is None or prev is None or pd.isna(prev)) else value - float(prev)
        records.append({"metric": m.key, "value": value, "delta": delta})
    return pd.DataFrame.from_records(records), latest_ts, baseline_end


# --- Time series ------------------------------------------------------------

# "Nice" bucket sizes in seconds: 30 s → 7 d. Auto-chosen to keep the
# rendered series near the target point count.
_NICE_BUCKETS = (30, 60, 120, 300, 600, 900, 1800, 3600, 7200, 10800, 21600, 43200, 86400, 604800)


def choose_bucket_seconds(start: datetime, end: datetime, target_points: int = 1500) -> int:
    """Pick the smallest nice bucket keeping the series ≲ target_points."""
    span = max((end - start).total_seconds(), 1.0)
    ideal = span / target_points
    for b in _NICE_BUCKETS:
        if b >= ideal:
            return b
    return _NICE_BUCKETS[-1]


@st.cache_data(ttl=600, show_spinner="Loading time series…")
def load_timeseries(
    table: str,
    metric_keys: tuple[str, ...],
    start: datetime,
    end: datetime,
    bucket_seconds: int | None = None,
    clean: bool = True,
) -> tuple[pd.DataFrame, dict[str, int], int]:
    """Downsampled time series for a sensor (plan §A2/§A3).

    Aggregates each metric to time buckets via ``avg``. When ``clean`` is
    True (default) saturation sentinels are excluded *before* averaging;
    when False the raw values are averaged so the user can inspect the
    saturation behaviour directly (raw/cleaned toggle, plan §A3).

    Returns ``(df, hidden_counts, bucket_s)``:

        df            — columns: ts + one per requested+available metric
        hidden_counts — {metric_key: n}; with ``clean`` these are the
                        values *hidden*, otherwise the values the filter
                        *would* remove (so the UI can disclose the count
                        either way)
        bucket_s      — the bucket size actually used (seconds)
    """
    safe = safe_sensor_table(table)
    pairs = [(m, c) for m, c in available_metrics(table) if m.key in metric_keys]
    if not pairs:
        return pd.DataFrame(columns=["ts"]), {}, 0

    bs = bucket_seconds or choose_bucket_seconds(start, end)

    value_cols, hidden_cols = [], []
    for m, col in pairs:
        agg = _clean_expr(col, m) if clean else f'"{col}"'
        value_cols.append(f"avg({agg}) AS {m.key}")
        if m.sentinel is not None:
            hidden_cols.append(f'count(*) FILTER (WHERE "{col}" >= {m.sentinel}) AS {m.key}__hidden')

    select_extra = (", " + ", ".join(hidden_cols)) if hidden_cols else ""
    sql = f"""
        SELECT (to_timestamp(floor(extract(epoch FROM ts) / {bs}) * {bs})
                    AT TIME ZONE 'UTC') AS ts,
               {", ".join(value_cols)}{select_extra}
        FROM {safe}
        WHERE ts >= :start AND ts < :end
        GROUP BY 1
        ORDER BY 1
    """
    df = read_sql(sql, {"start": start, "end": end})

    hidden_counts: dict[str, int] = {}
    for m, _ in pairs:
        hcol = f"{m.key}__hidden"
        if hcol in df.columns:
            total = int(df[hcol].fillna(0).sum())
            if total:
                hidden_counts[m.key] = total
    df = df[[c for c in df.columns if not c.endswith("__hidden")]]
    return df, hidden_counts, bs


def build_comparison_frame(
    df: pd.DataFrame, metric_keys: list[str] | tuple[str, ...]
) -> pd.DataFrame:
    """Aligned multi-measure frame for correlation (correlation plan §C).

    On a single Shape-A sensor every measure of a moment shares one row
    and timestamp, so no time alignment is needed: we keep ``ts`` plus the
    chosen metric columns and drop any row where one of those measures is
    missing (a hidden sentinel or an outage), leaving only fully-paired
    samples. The caller can compare ``len`` before/after to disclose how
    many rows alignment removed.

    Returns an empty frame (with the requested columns) when none of the
    metric keys are present, rather than raising.
    """
    value_cols = [k for k in metric_keys if k in df.columns]
    cols = (["ts"] if "ts" in df.columns else []) + value_cols
    if not value_cols:
        return df.loc[:, cols].iloc[0:0] if cols else df.iloc[0:0]
    return df.loc[:, cols].dropna(subset=value_cols).reset_index(drop=True)


# --- Comparison (bars + box stats) -----------------------------------------


@st.cache_data(ttl=600, show_spinner="Comparing sensors…")
def load_comparison(
    tables: tuple[str, ...],
    metric_key: str,
    start: datetime,
    end: datetime,
) -> pd.DataFrame:
    """Per-sensor summary of one metric over a range (Comparison page).

    Sentinels are excluded from the statistics but **counted** in
    ``n_hidden`` for honest disclosure. Columns: ``table_name, n, avg,
    min, q1, median, q3, max, n_hidden``. One row per table that exposes
    the metric.
    """
    metric = get(metric_key)
    parts, params = [], {"start": start, "end": end}
    for i, table in enumerate(tables):
        cols = {m.key: c for m, c in available_metrics(table)}
        if metric_key not in cols:
            continue  # metric not present on this shape — skip honestly
        safe = safe_sensor_table(table)
        col = cols[metric_key]
        clean = _clean_expr(col, metric)
        n_hidden = (
            f'count(*) FILTER (WHERE "{col}" >= {metric.sentinel})'
            if metric.sentinel is not None
            else "0"
        )
        params[f"t{i}"] = table
        parts.append(
            f"""
            SELECT :t{i} AS table_name,
                   count({clean}) AS n,
                   avg({clean}) AS avg,
                   min({clean}) AS min,
                   percentile_cont(0.25) WITHIN GROUP (ORDER BY {clean}) AS q1,
                   percentile_cont(0.50) WITHIN GROUP (ORDER BY {clean}) AS median,
                   percentile_cont(0.75) WITHIN GROUP (ORDER BY {clean}) AS q3,
                   max({clean}) AS max,
                   {n_hidden} AS n_hidden
            FROM {safe}
            WHERE ts >= :start AND ts < :end
            """
        )
    if not parts:
        return pd.DataFrame(
            columns=["table_name", "n", "avg", "min", "q1", "median", "q3", "max", "n_hidden"]
        )
    return read_sql(" UNION ALL ".join(parts), params)


# --- Geo --------------------------------------------------------------------


@st.cache_data(ttl=3600, show_spinner=False)
def load_locations() -> pd.DataFrame:
    """Fixed map markers: located observed-objects + specialty points.

    Columns: ``name, ootype, city, lon, lat, table_name, has_data``.
    Coordinates are (lon, lat); the axis-swapped hi-res sensor is already
    corrected via :data:`SPECIALTY_TABLES`.
    """
    devices = load_devices()
    located = devices[devices["lon"].notna() & devices["lat"].notna()].copy()
    cols = ["name", "ootype", "city", "lon", "lat", "table_name", "has_data"]
    return located[cols].reset_index(drop=True)


@st.cache_data(ttl=3600, show_spinner="Loading track…")
def load_tracks(table: str) -> pd.DataFrame:
    """Deduplicated, time-ordered GPS track for a mobile sensor.

    ``DISTINCT`` removes the A3 duplicate-row artefact (plan §1.3 quirk
    #2). Columns: ``ts, lon, lat``. Empty if the table carries no
    geometry (e.g. stationary sensors).
    """
    safe = safe_sensor_table(table)
    if "pos" not in _columns_of(table):
        return pd.DataFrame(columns=["ts", "lon", "lat"])
    df = read_sql(
        f"""
        SELECT DISTINCT ts, ST_X(pos) AS lon, ST_Y(pos) AS lat
        FROM {safe}
        WHERE pos IS NOT NULL
        ORDER BY ts
        """
    )
    return df


# --- Mobile routes (track segmentation) ------------------------------------


def segment_routes(
    points: pd.DataFrame, gap_seconds: int = 3600, min_points: int = 2
) -> pd.DataFrame:
    """Split an ordered GPS point frame into trips by a time gap (plan §C).

    Pure (no DB) so it is unit-testable. Steps: drop the A3 duplicate-row
    artefact (identical ``ts``), order by ``ts``, then start a new
    ``route_id`` whenever the gap to the previous point exceeds
    ``gap_seconds``. Routes with fewer than ``min_points`` points are
    dropped (a lone point is not a path) and the surviving ids are
    renumbered consecutively from 0 so the UI can label them "Route 1…N".

    ``points`` must carry a ``ts`` column; any other columns (lon/lat/PM)
    pass through untouched. Returns a copy with an added ``route_id``.
    """
    cols = list(points.columns) + ["route_id"]
    if points.empty:
        return pd.DataFrame(columns=cols)
    df = points.copy()
    df["ts"] = pd.to_datetime(df["ts"])
    df = df.drop_duplicates(subset=["ts"]).sort_values("ts").reset_index(drop=True)
    raw_id = (df["ts"].diff() > pd.Timedelta(seconds=gap_seconds)).cumsum()
    sizes = raw_id.groupby(raw_id).transform("size")
    df = df[sizes >= min_points].copy()
    # Renumber the surviving routes 0..k so labels are gap-free.
    df["route_id"] = pd.factorize(raw_id[sizes >= min_points])[0]
    return df.reset_index(drop=True)


@st.cache_data(ttl=3600, show_spinner="Segmenting routes…")
def load_routes(
    table: str,
    gap_seconds: int = 3600,
    min_points: int = 2,
    start: datetime | None = None,
    end: datetime | None = None,
) -> pd.DataFrame:
    """A mobile sensor's GPS track split into trips (plan §C/§E).

    Reads the de-duplicated, time-ordered points (optionally within a
    ``[start, end)`` window) carrying PM2.5 (sentinels cleaned, so the
    saturation ceiling never skews the colour scale), then segments them
    with :func:`segment_routes`. Columns: ``ts, lon, lat, pm2_5,
    route_id``. Empty if the table has no geometry (e.g. a stationary
    sensor).
    """
    cols = ["ts", "lon", "lat", "pm2_5", "route_id"]
    safe = safe_sensor_table(table)
    if "pos" not in _columns_of(table):
        return pd.DataFrame(columns=cols)
    pm_col = {m.key: c for m, c in available_metrics(table)}.get("pm2_5")
    pm_select = f', {_clean_expr(pm_col, get("pm2_5"))} AS pm2_5' if pm_col else ""
    where = ["pos IS NOT NULL"]
    params: dict = {}
    if start is not None and end is not None:
        where.append("ts >= :start AND ts < :end")
        params["start"], params["end"] = start, end
    df = read_sql(
        f"SELECT DISTINCT ts, ST_X(pos) AS lon, ST_Y(pos) AS lat{pm_select} "
        f"FROM {safe} WHERE {' AND '.join(where)} ORDER BY ts",
        params,
    )
    if df.empty:
        return pd.DataFrame(columns=cols)
    if "pm2_5" not in df.columns:
        df["pm2_5"] = pd.NA
    return segment_routes(df, gap_seconds=gap_seconds, min_points=min_points)


# Shape-B (hi-res) particle size classes: column -> display label.
_PARTICLE_MASS = (("mass_pm1_0", "PM1.0"), ("mass_pm2_5", "PM2.5"), ("mass_pm4", "PM4"), ("mass_pm10", "PM10"))
_PARTICLE_NUMBER = (
    ("number_pm0_5", "PM0.5"), ("number_pm1_0", "PM1.0"), ("number_pm2_5", "PM2.5"),
    ("number_pm4", "PM4"), ("number_pm10", "PM10"),
)


@st.cache_data(ttl=600, show_spinner=False)
def load_particle_sizes(table: str, start: datetime, end: datetime) -> pd.DataFrame:
    """Mean particle concentration per size class for the hi-res sensor.

    Drives the particle-size distribution drill-down (plan §3 candidate 8),
    only meaningful for Shape-B (``sensor_781c3ce6ad3c``). Returns a tidy
    long frame: ``kind`` ("Mass (µg/m³)" | "Number (#/cm³)"),
    ``size_class``, ``value`` — empty if the table has no such columns.
    """
    safe = safe_sensor_table(table)
    cols = _columns_of(table)
    mass = [(c, lbl) for c, lbl in _PARTICLE_MASS if c in cols]
    number = [(c, lbl) for c, lbl in _PARTICLE_NUMBER if c in cols]
    if not mass and not number:
        return pd.DataFrame(columns=["kind", "size_class", "value"])

    selects = ", ".join(f'avg("{c}") AS "{c}"' for c, _ in (mass + number))
    df = read_sql(
        f"SELECT {selects} FROM {safe} WHERE ts >= :start AND ts < :end",
        {"start": start, "end": end},
    )
    if df.empty:
        return pd.DataFrame(columns=["kind", "size_class", "value"])
    row = df.iloc[0]
    records = [
        {"kind": "Mass (µg/m³)", "size_class": lbl, "value": float(row[c])}
        for c, lbl in mass if pd.notna(row[c])
    ] + [
        {"kind": "Number (#/cm³)", "size_class": lbl, "value": float(row[c])}
        for c, lbl in number if pd.notna(row[c])
    ]
    return pd.DataFrame.from_records(records)


# --- User-content loaders (interactivity plan §B) ---------------------------
# These read the dashboard_* tables written by the interactivity layer
# (created by scripts/add_dashboard_tables.py). TTLs are short because,
# unlike the frozen measurement data, this content changes at runtime;
# the write layer also clears these caches on every successful write.


@st.cache_data(ttl=3600, show_spinner=False)
def dashboard_tables_ready() -> bool:
    """True iff all four ``dashboard_*`` tables exist (migration applied)."""
    rows = read_sql(
        """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = :schema AND table_name LIKE 'dashboard\\_%'
        """,
        {"schema": SCHEMA},
    )
    found = set(rows["table_name"])
    needed = {
        "dashboard_annotations",
        "dashboard_reading_flags",
        "dashboard_thresholds",
        "dashboard_saved_views",
    }
    return needed.issubset(found)


@st.cache_data(ttl=60, show_spinner=False)
def load_annotations(table_name: str) -> pd.DataFrame:
    """Time-range annotations for a sensor, oldest first (plan §B4).

    Keyed by the sensor's ``table_name`` (stored in the ``mac`` column).
    Columns: ``id, ts_from, ts_to, label, note, created_at``. Empty frame
    if the migration has not run or the name is not a sensor table.
    """
    cols = ["id", "ts_from", "ts_to", "label", "note", "created_at"]
    if not dashboard_tables_ready() or not is_sensor_table(table_name):
        return pd.DataFrame(columns=cols)
    return read_sql(
        f"""
        SELECT id, ts_from, ts_to, label, note, created_at
        FROM {SCHEMA}.dashboard_annotations
        WHERE mac = :mac
        ORDER BY ts_from, id
        """,
        {"mac": table_name},
    )


@st.cache_data(ttl=60, show_spinner=False)
def load_reading_flags(table_name: str) -> pd.DataFrame:
    """All reading flags attached to one sensor table (plan §B5).

    Columns: ``id, reading_id, flag, note, created_at``. Callers filter
    to the displayed ids in pandas (flag counts are tiny). Empty frame if
    the migration has not run.
    """
    cols = ["id", "reading_id", "flag", "note", "created_at"]
    if not dashboard_tables_ready() or not is_sensor_table(table_name):
        return pd.DataFrame(columns=cols)
    return read_sql(
        f"""
        SELECT id, reading_id, flag, note, created_at
        FROM {SCHEMA}.dashboard_reading_flags
        WHERE table_name = :t
        ORDER BY reading_id
        """,
        {"t": table_name},
    )


@st.cache_data(ttl=60, show_spinner=False)
def load_raw_readings(
    table: str, start: datetime, end: datetime, limit: int = 200
) -> pd.DataFrame:
    """Raw (un-aggregated) rows with their ``id`` for the flag inspector.

    The time-series chart is downsampled, so flagging an individual point
    needs the real row ids. Returns ``id, ts`` + every available metric
    column for the newest ``limit`` rows in range. Sentinels are **not**
    cleaned here — this view exists precisely to inspect them (plan §B5).
    """
    safe = safe_sensor_table(table)
    pairs = available_metrics(table)
    metric_cols = ", ".join(f'"{c}" AS {m.key}' for m, c in pairs)
    select = f"id, ts{', ' + metric_cols if metric_cols else ''}"
    return read_sql(
        f"""
        SELECT {select} FROM {safe}
        WHERE ts >= :start AND ts < :end
        ORDER BY ts DESC
        LIMIT :limit
        """,
        {"start": start, "end": end, "limit": int(limit)},
    )


@st.cache_data(ttl=60, show_spinner=False)
def load_thresholds() -> pd.DataFrame:
    """Persisted metric thresholds (plan §B6).

    Columns: ``id, metric, value, label, created_at``. Empty if the
    migration has not run.
    """
    cols = ["id", "metric", "value", "label", "created_at"]
    if not dashboard_tables_ready():
        return pd.DataFrame(columns=cols)
    return read_sql(
        f"""
        SELECT id, metric, value, label, created_at
        FROM {SCHEMA}.dashboard_thresholds
        ORDER BY metric, value
        """
    )


@st.cache_data(ttl=60, show_spinner=False)
def load_saved_views() -> pd.DataFrame:
    """Persisted saved views, newest first (plan §A7 → §B6).

    Columns: ``id, name, params_json (dict), created_at``. Empty if the
    migration has not run.
    """
    cols = ["id", "name", "params_json", "created_at"]
    if not dashboard_tables_ready():
        return pd.DataFrame(columns=cols)
    return read_sql(
        f"""
        SELECT id, name, params_json, created_at
        FROM {SCHEMA}.dashboard_saved_views
        ORDER BY created_at DESC, id DESC
        """
    )


@st.cache_data(ttl=60, show_spinner=False)
def load_feature_flags() -> pd.DataFrame:
    """The ``func_*`` UI feature flags from ``tbl_systemconfiguration`` (§B3).

    Columns: ``id, ckey, ctype, cvalue, active``. These drive optional
    modules — a page reads them on load to show/hide a feature.
    """
    return read_sql(
        f"""
        SELECT id, ckey, ctype, cvalue, active
        FROM {SCHEMA}.tbl_systemconfiguration
        WHERE ckey LIKE 'func\\_%'
        ORDER BY ckey
        """
    )


def feature_enabled(ckey: str, default: bool = True) -> bool:
    """Whether a named feature flag is active (missing key → ``default``)."""
    flags = load_feature_flags()
    hit = flags[flags["ckey"] == ckey]
    if hit.empty:
        return default
    return bool(hit.iloc[0]["active"])
