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


def test_interpret_r_words_and_undefined() -> None:
    from src.utils.correlate import interpret_r

    assert interpret_r(0.95) == "very strong positive"
    assert interpret_r(-0.4) == "moderate negative"
    assert interpret_r(0.02) == "negligible"
    assert interpret_r(None) == "undefined"


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
