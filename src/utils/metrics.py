"""Central metric registry — the single source of truth for displayable
measures (implementation plan §2).

Defining each measure *once* enforces consistency (Shneiderman #1) and
honest units/limits project-wide: every chart, KPI tile and tooltip
pulls its label, unit, plausible range, sentinel value, color and
number format from here, so nothing drifts.

The canonical metric ``key`` is the column name on the Shape-A SENSORpi
tables. Specialty shapes expose the same physical quantity under a
different column (e.g. the hi-res sensor stores PM2.5 in ``mass_pm2_5``);
``source_columns`` records that mapping so loaders can normalize.

Note on units: the on-device registry (``tbl_datatype``) labels PM as
"ppm", but particulate matter is conventionally mass concentration. We
label it **µg/m³** everywhere (plan §1.3 quirk #4).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.utils.palette import OKABE_ITO_NAMED as _C


@dataclass(frozen=True)
class Metric:
    """One displayable measure.

    Attributes:
        key: canonical column name (Shape-A SENSORpi tables).
        label: full human label, e.g. "Outdoor temperature".
        short_label: compact label for KPI tiles / chips.
        unit: display unit (already corrected, e.g. µg/m³ not ppm).
        vmin/vmax: plausible physical range — used for honest, fixed
            axis bounds and for flagging out-of-range readings. NOT a
            silent filter: values outside are kept unless they hit a
            ``sentinel``.
        sentinel: value at/above which a reading is a saturation ceiling
            or hard fault and must be hidden from trend charts/KPIs
            (``None`` = no sentinel). Counted and disclosed, never
            dropped silently (plan §1.3 quirk #1, CONTEXT ethics).
        color: stable categorical color (Okabe-Ito) so this metric looks
            the same in every chart.
        icon: Material icon name for KPI tiles / labels.
        decimals: number of decimal places when formatting a value.
        group: logical chunk ("pollutant" | "climate" | "index") for
            Miller-friendly grouping.
        source_columns: per-shape column name when it differs from
            ``key`` (shape letter -> column).
    """

    key: str
    label: str
    short_label: str
    unit: str
    vmin: float
    vmax: float
    sentinel: float | None
    color: str
    icon: str
    decimals: int
    group: str
    source_columns: dict[str, str] = field(default_factory=dict)

    def format(self, value: float | None) -> str:
        """Format a value with its unit, e.g. ``"7.3 µg/m³"``."""
        if value is None or (isinstance(value, float) and value != value):  # NaN
            return "–"
        return f"{value:.{self.decimals}f} {self.unit}"

    def column_for(self, shape: str) -> str:
        """Return the column name carrying this metric on a given shape."""
        return self.source_columns.get(shape, self.key)


# --- The registry -----------------------------------------------------------
# Order is display order. PM first (headline pollutants), then CO2, then
# climate. Keep <= ~7 per logical group (Miller).

_METRIC_LIST: tuple[Metric, ...] = (
    Metric(
        key="pm2_5",
        label="PM2.5",
        short_label="PM2.5",
        unit="µg/m³",
        vmin=0.0,
        vmax=500.0,
        sentinel=999.9,
        color=_C["orange"],
        icon=":material/blur_on:",
        decimals=1,
        group="pollutant",
        # B (hi-res) stores mass conc. under mass_pm2_5; C/Ext use pm2_5.
        source_columns={"B": "mass_pm2_5"},
    ),
    Metric(
        key="pm10_0",
        label="PM10",
        short_label="PM10",
        unit="µg/m³",
        vmin=0.0,
        vmax=600.0,
        sentinel=1999.9,
        color=_C["blue"],
        icon=":material/grain:",
        decimals=1,
        group="pollutant",
        source_columns={"B": "mass_pm10"},
    ),
    Metric(
        key="co2",
        label="CO₂",
        short_label="CO₂",
        unit="ppm",
        vmin=350.0,
        vmax=5000.0,
        sentinel=None,
        color=_C["bluish_green"],
        icon=":material/co2:",
        decimals=0,
        group="pollutant",
    ),
    Metric(
        key="temp1",
        label="Outdoor temperature",
        short_label="Temp.",
        unit="°C",
        vmin=-30.0,
        vmax=50.0,
        sentinel=85.0,
        color=_C["vermillion"],
        icon=":material/device_thermostat:",
        decimals=1,
        group="climate",
    ),
    Metric(
        key="inn_temp",
        label="Housing temperature",
        short_label="Housing temp.",
        unit="°C",
        vmin=-10.0,
        vmax=60.0,
        # The plan flags ≥ 53 °C as *suspect*, but that overlaps the plausible
        # range (warm enclosures are real), so we do NOT silently null it —
        # over-cleaning is dishonest too. No hard saturation ceiling here.
        sentinel=None,
        color=_C["reddish_purple"],
        icon=":material/thermostat:",
        decimals=1,
        group="climate",
    ),
    Metric(
        key="inn_hum",
        label="Humidity (housing)",
        short_label="Humidity",
        unit="%",
        vmin=0.0,
        vmax=100.0,
        sentinel=None,
        color=_C["sky_blue"],
        icon=":material/humidity_percentage:",
        decimals=0,
        group="climate",
    ),
    Metric(
        key="inn_pres",
        label="Pressure",
        short_label="Pressure",
        unit="hPa",
        vmin=950.0,
        vmax=1050.0,
        sentinel=None,
        color=_C["grey"],
        icon=":material/compress:",
        decimals=0,
        group="climate",
    ),
    # The *measured* CAQI from the Polish feed only (Shape C). It is the
    # independent plausibility check for our *computed* EU-CAQI band (see
    # aqi.py) — distinct things, hence the "(measured)" label. Selectable on
    # the Time Series page when the Gdańsk feed is chosen.
    Metric(
        key="caqi",
        label="CAQI (measured)",
        short_label="CAQI",
        unit="index",
        vmin=0.0,
        vmax=11.0,
        sentinel=None,
        color=_C["yellow"],
        icon=":material/speed:",
        decimals=1,
        group="index",
    ),
)

METRICS: dict[str, Metric] = {m.key: m for m in _METRIC_LIST}

# Convenience groupings (kept small per Miller).
POLLUTANTS: tuple[str, ...] = tuple(m.key for m in _METRIC_LIST if m.group == "pollutant")
CLIMATE: tuple[str, ...] = tuple(m.key for m in _METRIC_LIST if m.group == "climate")

# The headline measures shown on the Overview KPI row (≈ Miller 7±2).
HEADLINE_KPIS: tuple[str, ...] = ("pm2_5", "pm10_0", "co2", "temp1", "inn_hum")

# Measures actually offered for stationary A-sensors. temp2/temp3, pos and
# the pos_* family are entirely NULL on stationary units (plan §1.3 quirk #8),
# so we never offer them.
STATIONARY_METRICS: tuple[str, ...] = ("pm2_5", "pm10_0", "co2", "temp1", "inn_temp", "inn_hum", "inn_pres")


def get(key: str) -> Metric:
    """Look up a metric, raising a clear error on an unknown key."""
    try:
        return METRICS[key]
    except KeyError as exc:  # pragma: no cover - guards programmer error
        raise KeyError(f"Unknown metric {key!r}. Known: {sorted(METRICS)}") from exc


def label_with_unit(key: str) -> str:
    """Axis-style label, e.g. ``"PM2.5 (µg/m³)"``."""
    m = get(key)
    return f"{m.label} ({m.unit})"
