"""Smoke tests.

Two layers:

* **Pure** tests (no DB) check the package imports cleanly and that the
  metric registry / sentinel cleaning / CAQI logic behave — these are the
  honest-data guarantees the whole dashboard rests on.
* A **DB-gated** integration test exercises the loaders against the live
  Postgres container; it ``skip``s cleanly when the DB is unreachable, so
  the suite still passes in pip-only / CI environments.
"""

from __future__ import annotations

import importlib

import pytest


def test_src_imports() -> None:
    for mod in (
        "src",
        "src.components",
        "src.components.kpi",
        "src.components.filter_bar",
        "src.components.charts",
        "src.data",
        "src.data.loaders",
        "src.db",
        "src.db.connection",
        "src.db.queries",
        "src.utils",
        "src.utils.palette",
        "src.utils.accessibility",
        "src.utils.metrics",
        "src.utils.clean",
        "src.utils.aqi",
        "src.utils.correlate",
    ):
        importlib.import_module(mod)


def test_palette_is_colorblind_safe() -> None:
    from src.utils.palette import OKABE_ITO

    assert len(OKABE_ITO) >= 7
    assert all(c.startswith("#") and len(c) == 7 for c in OKABE_ITO)


# --- Metric registry --------------------------------------------------------


def test_metric_registry_consistency() -> None:
    from src.utils.metrics import METRICS

    for key, m in METRICS.items():
        assert m.key == key
        assert m.unit and m.label
        assert m.vmin < m.vmax
        if m.sentinel is not None:
            assert m.sentinel > m.vmax  # a sentinel is above the plausible range


def test_pm_labelled_micrograms_not_ppm() -> None:
    # Quirk #4: the on-device registry mislabels PM as ppm; we must not.
    from src.utils.metrics import get

    assert get("pm2_5").unit == "µg/m³"
    assert get("pm10_0").unit == "µg/m³"


# --- Sentinel cleaning ------------------------------------------------------


def test_clean_hides_sentinels_and_counts_them() -> None:
    import pandas as pd

    from src.utils.clean import clean_series, hidden_notice

    s = pd.Series([2.8, 999.9, 5.0, 1500.0])
    cleaned, n = clean_series(s, "pm2_5")
    assert n == 2
    assert cleaned.isna().sum() == 2
    assert cleaned.dropna().tolist() == [2.8, 5.0]
    assert hidden_notice({"pm2_5": 2})  # non-empty notice
    assert hidden_notice({}) is None


# --- Multi-measure / correlation graph --------------------------------------


def test_build_comparison_frame_drops_unpaired_rows() -> None:
    import pandas as pd

    from src.data.loaders import build_comparison_frame

    df = pd.DataFrame(
        {
            "ts": pd.date_range("2025-01-01", periods=4, freq="h"),
            "pm2_5": [1.0, None, 3.0, 4.0],
            "temp1": [10.0, 11.0, None, 13.0],
            "co2": [400, 410, 420, 430],  # not selected -> excluded from frame
        }
    )
    out = build_comparison_frame(df, ["pm2_5", "temp1"])
    # Only rows where BOTH selected measures are present survive (rows 0 and 3).
    assert list(out.columns) == ["ts", "pm2_5", "temp1"]
    assert len(out) == 2
    assert out["pm2_5"].tolist() == [1.0, 4.0]


def test_normalize_frame_scales_to_unit_range_and_keeps_real_ranges() -> None:
    import pandas as pd

    from src.utils.correlate import normalize_frame

    frame = pd.DataFrame({"ts": [1, 2, 3], "temp1": [10.0, 20.0, 30.0], "inn_hum": [50.0, 50.0, 50.0]})
    scaled, ranges = normalize_frame(frame, ["temp1", "inn_hum"])
    assert scaled["temp1"].tolist() == [0.0, 0.5, 1.0]
    assert ranges["temp1"] == (10.0, 30.0)
    # A constant series has no shape -> mapped to the mid-line, range recorded.
    assert scaled["inn_hum"].tolist() == [0.5, 0.5, 0.5]
    assert ranges["inn_hum"] == (50.0, 50.0)


def test_compute_correlation_two_measures_perfect_and_fit() -> None:
    import pandas as pd

    from src.utils.correlate import compute_correlation

    frame = pd.DataFrame({"pm2_5": [1.0, 2.0, 3.0, 4.0], "temp1": [2.0, 4.0, 6.0, 8.0]})
    res = compute_correlation(frame, ("pm2_5", "temp1"))
    assert res.matrix is None
    assert res.n == 4
    assert res.r == pytest.approx(1.0)
    # y = 2x exactly -> least-squares slope 2, intercept 0.
    assert res.slope == pytest.approx(2.0)
    assert res.intercept == pytest.approx(0.0)


def test_compute_correlation_spearman_is_scipy_free_and_rank_based() -> None:
    import pandas as pd

    from src.utils.correlate import compute_correlation

    # Monotonic but non-linear (y = x**3): Spearman = 1 (perfect rank order),
    # Pearson < 1. Must not need scipy — pandas' native spearman would import it.
    frame = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0, 5.0], "b": [1.0, 8.0, 27.0, 64.0, 125.0]})
    sp = compute_correlation(frame, ("a", "b"), method="spearman")
    pe = compute_correlation(frame, ("a", "b"), method="pearson")
    assert sp.r == pytest.approx(1.0)
    assert pe.r < 0.99
    # Spearman draws no straight-line fit (it is rank-based).
    assert sp.slope is None and pe.slope is not None


def test_compute_correlation_matrix_for_three_measures() -> None:
    import pandas as pd

    from src.utils.correlate import compute_correlation

    frame = pd.DataFrame(
        {"pm2_5": [1.0, 2.0, 3.0], "temp1": [3.0, 2.0, 1.0], "co2": [1.0, 2.0, 3.0]}
    )
    res = compute_correlation(frame, ("pm2_5", "temp1", "co2"))
    assert res.r is None
    assert res.matrix is not None and res.matrix.shape == (3, 3)
    # pm2_5 and co2 move together; pm2_5 and temp1 move oppositely.
    assert res.matrix.loc["pm2_5", "co2"] == pytest.approx(1.0)
    assert res.matrix.loc["pm2_5", "temp1"] == pytest.approx(-1.0)


def test_compute_correlation_lag_shifts_second_measure() -> None:
    import pandas as pd

    from src.utils.correlate import compute_correlation

    # b runs one step ahead of a; shifting b forward by one bucket (lag=+1)
    # realigns them perfectly, scoring higher than the unshifted correlation.
    frame = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0, 5.0], "b": [2.0, 3.0, 4.0, 5.0, 9.0]})
    base = compute_correlation(frame, ("a", "b"))
    lagged = compute_correlation(frame, ("a", "b"), lag=1)
    assert lagged.r == pytest.approx(1.0)
    assert lagged.r > (base.r or 0)
    assert lagged.lag == 1


def test_correlation_verdict_lay_bands_and_sign() -> None:
    from src.utils.correlate import correlation_verdict

    # Cut-offs (plan §B3): <0.3 no/weak, 0.3–0.7 moderate, >0.7 strong.
    assert correlation_verdict(0.95).label == "Strong positive"
    assert correlation_verdict(0.95).arrow == "↑"
    assert correlation_verdict(-0.45).label == "Moderate negative"
    assert correlation_verdict(-0.45).arrow == "↓"
    # Boundaries: 0.3 is moderate (inclusive lower), 0.7 is moderate (inclusive upper).
    assert correlation_verdict(0.3).level == 1
    assert correlation_verdict(0.7).level == 1
    assert correlation_verdict(0.71).level == 2
    # Too weak to trust the sign -> no direction implied, neutral badge.
    weak = correlation_verdict(0.05)
    assert weak.level == 0 and weak.arrow == "" and weak.label == "No / weak link"
    # Missing r is explicit, never a misleading 0.
    assert correlation_verdict(None).label == "Not enough data"
    # Strength badges are a neutral ramp (never red/green = good/bad).
    assert {correlation_verdict(v).badge for v in (0.1, 0.5, 0.9)} == {"gray", "blue", "violet"}


# --- Route segmentation (adaptive device view) ------------------------------


def test_segment_routes_splits_dedups_and_drops_singletons() -> None:
    import pandas as pd

    from src.data.loaders import segment_routes

    base = pd.Timestamp("2025-01-01 00:00:00")
    rows = []
    # Trip A: 3 points 10 min apart.
    for i in range(3):
        rows.append({"ts": base + pd.Timedelta(minutes=10 * i), "lon": 8.0 + i, "lat": 52.0, "pm2_5": 5.0})
    # A duplicate row (same ts as A's first point) — the A3 artefact.
    rows.append({"ts": base, "lon": 8.0, "lat": 52.0, "pm2_5": 5.0})
    # Trip B: 2 points, starting 3 h later (gap > 1 h → new route).
    for i in range(2):
        rows.append({"ts": base + pd.Timedelta(hours=3, minutes=5 * i), "lon": 9.0 + i, "lat": 52.0, "pm2_5": 7.0})
    # A lone point 5 h after that (its own would-be route) — must be dropped.
    rows.append({"ts": base + pd.Timedelta(hours=8), "lon": 10.0, "lat": 52.0, "pm2_5": 9.0})

    out = segment_routes(pd.DataFrame(rows), gap_seconds=3600, min_points=2)
    # Two real trips survive; the singleton is dropped; the duplicate collapsed.
    assert sorted(out["route_id"].unique().tolist()) == [0, 1]
    assert (out["route_id"] == 0).sum() == 3  # trip A, duplicate removed
    assert (out["route_id"] == 1).sum() == 2  # trip B
    assert len(out) == 5


def test_segment_routes_empty_frame_has_route_id_column() -> None:
    import pandas as pd

    from src.data.loaders import segment_routes

    out = segment_routes(pd.DataFrame(columns=["ts", "lon", "lat", "pm2_5"]))
    assert "route_id" in out.columns and out.empty


# --- CAQI band --------------------------------------------------------------


def test_caqi_band_takes_the_worse_pollutant() -> None:
    from src.utils.aqi import caqi_band

    # PM2.5 says "Very low", PM10 says "Medium" -> worse (Medium) wins.
    band = caqi_band(pm2_5=5.0, pm10=70.0)
    assert band is not None and band.label == "Medium"
    assert caqi_band(None, None) is None


def test_caqi_bands_have_distinct_icons() -> None:
    # Color is never the sole channel: each band needs a distinct glyph.
    from src.utils.aqi import CAQI_BANDS

    icons = [b.icon for b in CAQI_BANDS]
    assert len(set(icons)) == len(icons)


def test_caqi_bands_carry_plain_language() -> None:
    # The hub leads with words, not a chart: every band needs a quality
    # word + a non-empty advice sentence, best→worst monotonic.
    from src.utils.aqi import CAQI_BANDS

    assert [b.quality for b in CAQI_BANDS] == ["Good", "Fair", "Moderate", "Poor", "Very poor"]
    assert all(b.advice.strip() for b in CAQI_BANDS)


def test_caqi_pm_thresholds_match_the_bands() -> None:
    # The chart's band-guide lines must be the same breakpoints the band
    # classification uses, each labelled with the band you enter above it.
    from src.utils.aqi import caqi_band, caqi_pm_thresholds

    pm25 = caqi_pm_thresholds("pm2_5")
    assert pm25 == [(15.0, "Low"), (30.0, "Medium"), (55.0, "High"), (110.0, "Very high")]
    # PM10 uses its own (higher) grid.
    assert caqi_pm_thresholds("pm10_0")[0] == (25.0, "Low")
    # A value just above each PM2.5 boundary classifies into the labelled band.
    for value, label in pm25:
        band = caqi_band(pm2_5=value + 0.1)
        assert band is not None and band.label == label


def test_caqi_meter_zones_label_each_quarter() -> None:
    # The meter names its four visible zones best→worst with the quality words,
    # at the quarter centres (positions in (0, 1)).
    from src.utils.aqi import caqi_meter_zones

    zones = caqi_meter_zones()
    assert [w for _, w in zones] == ["Good", "Fair", "Moderate", "Poor"]
    assert [round(p, 3) for p, _ in zones] == [0.875, 0.625, 0.375, 0.125]
    assert all(0.0 < p < 1.0 for p, _ in zones)


# --- DB-gated integration ---------------------------------------------------


@pytest.fixture(scope="session")
def db_or_skip():
    from sqlalchemy import text

    from src.db import get_engine

    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Postgres not reachable: {exc}")


def test_load_devices_against_db(db_or_skip) -> None:
    from src.data import load_devices, sensors_with_data

    devices = load_devices()
    # 40 registered objects; 24 of them carry a MAC (-> table) plus the 3
    # unregistered specialty/external tables = 27 table names.
    assert (devices["oo_id"].notna()).sum() == 40
    assert devices["table_name"].notna().sum() == 27
    # Exactly the populated tables show up as "has data".
    with_data = set(sensors_with_data()["table_name"])
    assert "sensor_000aeb8337ac" in with_data
    assert "sensor_b827ebbc6f21" not in with_data  # m13: registered, no table


def test_allowlist_blocks_unknown_tables(db_or_skip) -> None:
    from src.db import is_sensor_table, safe_sensor_table

    assert is_sensor_table("sensor_000aeb8337ac")
    assert not is_sensor_table("pg_user; DROP TABLE x")
    with pytest.raises(ValueError):
        safe_sensor_table("definitely_not_a_table")


def test_load_routes_segments_mobile_track(db_or_skip) -> None:
    from src.data import load_routes

    # SENSORpi m01 is a mobile sensor with a real GPS track (plan §C).
    routes = load_routes("sensor_b827eb0fae5c", gap_seconds=3600, min_points=2)
    assert not routes.empty
    assert {"ts", "lon", "lat", "pm2_5", "route_id"}.issubset(routes.columns)
    # Every surviving route has at least min_points; ids are gap-free 0..N.
    sizes = routes.groupby("route_id").size()
    assert (sizes >= 2).all()
    assert routes["route_id"].max() == routes["route_id"].nunique() - 1
    # A stationary sensor has no geometry → empty (the loader returns a stub).
    assert load_routes("sensor_000aeb8337ac").empty
