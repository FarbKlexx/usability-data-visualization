"""Derived air-quality category — EU CAQI (implementation plan §6.3, locked).

We classify a reading into one of the five EU **CAQI** (Common Air
Quality Index) bands — *very low → very high* — using the CiteAir
background-station hourly grid for PM2.5 and PM10. The band for a
reading is the **worse** of its PM2.5 and PM10 sub-bands.

This is a **computed** quantity (honesty, plan §2): the UI must label it
as derived. The real ``caqi`` column from the Polish feed serves only as
an independent plausibility check, not as the source here.

Crucially the category is **triple-encoded** — text label + distinct
Material icon (different glyph per band) + color — so it never relies on
color alone (CONTEXT: ~8 % color-vision deficiency).

CiteAir CAQI grid (hourly, background), upper bounds in µg/m³:

    Band        index    PM2.5      PM10
    Very low      0-25    0-15       0-25
    Low          25-50   15-30      25-50
    Medium       50-75   30-55      50-90
    High        75-100   55-110     90-180
    Very high    >100     >110       >180
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.utils.palette import OKABE_ITO_NAMED as _C

COMPUTED_NOTE = "Computed from PM2.5/PM10 via the EU CAQI grid — not a measured value."


@dataclass(frozen=True)
class CAQIBand:
    """One CAQI band, with everything the UI needs to render it."""

    level: int  # 0 (best) .. 4 (worst); sortable
    label: str
    color: str
    icon: str  # Material icon — distinct glyph per band (shape channel)
    pm2_5_hi: float  # inclusive upper bound for PM2.5 (µg/m³)
    pm10_hi: float  # inclusive upper bound for PM10 (µg/m³)

    @property
    def range_label(self) -> str:
        """Human band range for legends, e.g. ``"PM2.5 15–30 µg/m³"``."""
        lo_25 = 0 if self.level == 0 else CAQI_BANDS[self.level - 1].pm2_5_hi
        if math.isinf(self.pm2_5_hi):
            return f"PM2.5 > {lo_25:g} µg/m³"
        return f"PM2.5 {lo_25:g}–{self.pm2_5_hi:g} µg/m³"


# Ordinal severity ramp. Cool→warm reinforces severity, but the icon and
# label carry the meaning so red/green confusion never loses information.
CAQI_BANDS: tuple[CAQIBand, ...] = (
    CAQIBand(0, "Very low", _C["bluish_green"], ":material/sentiment_very_satisfied:", 15.0, 25.0),
    CAQIBand(1, "Low", _C["yellow"], ":material/sentiment_satisfied:", 30.0, 50.0),
    CAQIBand(2, "Medium", _C["orange"], ":material/sentiment_neutral:", 55.0, 90.0),
    CAQIBand(3, "High", _C["vermillion"], ":material/sentiment_dissatisfied:", 110.0, 180.0),
    CAQIBand(4, "Very high", "#7D2E68", ":material/sentiment_very_dissatisfied:", math.inf, math.inf),
)


def _band_for(value: float | None, attr: str) -> int | None:
    """Return the band *level* for a single pollutant value, or None."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if value < 0:
        return None
    for band in CAQI_BANDS:
        if value <= getattr(band, attr):
            return band.level
    return CAQI_BANDS[-1].level  # pragma: no cover - inf guard


def caqi_band(pm2_5: float | None = None, pm10: float | None = None) -> CAQIBand | None:
    """Classify a reading into a CAQI band (worse of PM2.5 / PM10).

    Returns ``None`` if neither pollutant has a usable value, so callers
    can render a clear "no data" state instead of a misleading band.
    """
    levels = [
        lvl
        for lvl in (_band_for(pm2_5, "pm2_5_hi"), _band_for(pm10, "pm10_hi"))
        if lvl is not None
    ]
    if not levels:
        return None
    return CAQI_BANDS[max(levels)]
