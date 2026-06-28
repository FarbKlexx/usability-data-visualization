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
    quality: str  # plain-language air-quality word (hub status, consolidation §B1)
    advice: str  # one-sentence lay explanation / what-it-means

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
    CAQIBand(0, "Very low", _C["bluish_green"], ":material/sentiment_very_satisfied:", 15.0, 25.0,
             quality="Good", advice="Air quality is good — particulate pollution is very low."),
    CAQIBand(1, "Low", _C["yellow"], ":material/sentiment_satisfied:", 30.0, 50.0,
             quality="Fair", advice="Air quality is fair — particulate pollution is low."),
    CAQIBand(2, "Medium", _C["orange"], ":material/sentiment_neutral:", 55.0, 90.0,
             quality="Moderate", advice="Moderate pollution — sensitive groups should take it easy outdoors."),
    CAQIBand(3, "High", _C["vermillion"], ":material/sentiment_dissatisfied:", 110.0, 180.0,
             quality="Poor", advice="High pollution — consider limiting prolonged outdoor exertion."),
    CAQIBand(4, "Very high", "#7D2E68", ":material/sentiment_very_dissatisfied:", math.inf, math.inf,
             quality="Very poor", advice="Very high pollution — avoid prolonged outdoor exertion."),
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


# Continuous CiteAir CAQI sub-index breakpoints: (concentration µg/m³, index).
# The band table above is the *stepped* version of this; these let us place a
# marker *within* a band (so "just into Low" and "almost High" don't collapse to
# one dot). Index runs 0 (cleanest) .. 100 (top of "High"); "Very high" caps at
# 100 for placement. Same worse-of-PM2.5/PM10 rule as the band.
_PM25_GRID: tuple[tuple[float, float], ...] = ((0, 0), (15, 25), (30, 50), (55, 75), (110, 100))
_PM10_GRID: tuple[tuple[float, float], ...] = ((0, 0), (25, 25), (50, 50), (90, 75), (180, 100))


def _subindex(value: float | None, grid: tuple[tuple[float, float], ...]) -> float | None:
    """Linear-interpolate one pollutant's CAQI sub-index (0..100), or None."""
    if value is None or (isinstance(value, float) and math.isnan(value)) or value < 0:
        return None
    if value >= grid[-1][0]:
        return 100.0  # at/above the "Very high" floor — pin to the worst end
    for (c0, i0), (c1, i1) in zip(grid, grid[1:]):
        if value <= c1:
            return i0 + (i1 - i0) * (value - c0) / (c1 - c0)
    return 100.0  # pragma: no cover - covered by the >= guard above


def caqi_index(pm2_5: float | None = None, pm10: float | None = None) -> float | None:
    """Continuous CAQI index (0 cleanest .. 100 worst), worse of PM2.5/PM10.

    The companion to :func:`caqi_band` for *positioning* (e.g. a marker on a
    red→green meter); returns ``None`` when neither pollutant is usable.
    """
    subs = [s for s in (_subindex(pm2_5, _PM25_GRID), _subindex(pm10, _PM10_GRID)) if s is not None]
    return max(subs) if subs else None


def caqi_pm_thresholds(pollutant: str = "pm2_5") -> list[tuple[float, str]]:
    """Finite CAQI band-boundary concentrations (µg/m³) for a PM pollutant.

    Each boundary is paired with the band you *enter* when you cross above it,
    e.g. PM2.5 → ``[(15, "Low"), (30, "Medium"), (55, "High"), (110, "Very high")]``.
    Used to draw subtle air-quality reference lines on a concentration chart
    (the stepped form of the same grid the band classification uses).
    """
    attr = "pm10_hi" if pollutant in ("pm10_0", "pm10") else "pm2_5_hi"
    out: list[tuple[float, str]] = []
    for i, band in enumerate(CAQI_BANDS[:-1]):
        hi = getattr(band, attr)
        if math.isfinite(hi):
            out.append((float(hi), CAQI_BANDS[i + 1].label))
    return out


def caqi_meter_zones() -> list[tuple[float, str]]:
    """``(centre 0..1, plain-language quality word)`` for each visible meter zone.

    The red→green meter spans CAQI index 0..100 (best → top of "High"); its three
    interior ticks cut it into four zones whose centres get a word — right→left
    Good · Fair · Moderate · Poor — matching the hero verdict. The fifth band,
    "Very poor", is off this 0-100 scale (the worst edge), so it has no zone.
    """
    edges = (0.0, 25.0, 50.0, 75.0, 100.0)  # CAQI index band edges (worse-of grid)
    zones: list[tuple[float, str]] = []
    for i, band in enumerate(CAQI_BANDS[:4]):
        centre_index = (edges[i] + edges[i + 1]) / 2.0
        zones.append((1.0 - centre_index / 100.0, band.quality))
    return zones


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
