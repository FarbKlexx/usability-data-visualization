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
