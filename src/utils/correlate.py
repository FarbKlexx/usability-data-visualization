"""Correlation maths for the multi-measure / correlation graph
(implementation plan ``implementation_plan_correlation_graph.md`` §B/§E).

Pure pandas/numpy — no DB, no Streamlit — so it is trivially testable and
reusable. Three small responsibilities:

* :func:`normalize_frame` — per-measure min–max scaling to 0–1 for the
  *shape comparison* overlay (§B1). It returns the real ranges alongside
  the scaled frame so the absolute scale stays recoverable (honesty:
  normalization is disclosed, never hidden).
* :func:`compute_correlation` — Pearson/Spearman ``r`` + sample size
  ``n`` for two measures, or a full correlation matrix for three or more
  (§B3). Supports a lag offset so the user can probe whether one measure
  *leads* another (§D).
* :func:`correlation_verdict` — a lay-friendly reading of a coefficient:
  a 3-band strength (no/weak · moderate · strong, by ``|r|``) plus a
  signed direction, carried by **word + arrow** (shape/text), with a
  neutral badge colour for the strength band — so the meaning never
  rests on colour alone (consolidation plan §B3).

Correlation uses pandas' own Pearson ``corr`` (pure numpy). Spearman ρ is
computed as Pearson on the column ranks — mathematically identical — so
the layer stays **scipy-free** (pandas' built-in ``method="spearman"``
would import scipy, which we don't ship). The least-squares trend line
uses ``numpy.polyfit``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

#: Supported correlation methods (pandas-native, no scipy needed).
CORRELATION_METHODS: tuple[str, ...] = ("pearson", "spearman")


@dataclass(frozen=True)
class CorrelationResult:
    """Outcome of :func:`compute_correlation`.

    For exactly two measures ``r`` (and, for Pearson, the least-squares
    ``slope``/``intercept`` of the trend line) is populated and ``matrix``
    is ``None``. For three or more measures ``matrix`` holds the full
    pairwise correlation frame and ``r`` is ``None``.
    """

    method: str
    keys: tuple[str, ...]
    n: int
    lag: int = 0
    r: float | None = None
    slope: float | None = None
    intercept: float | None = None
    matrix: pd.DataFrame | None = None


def normalize_frame(
    frame: pd.DataFrame, metric_keys: list[str] | tuple[str, ...]
) -> tuple[pd.DataFrame, dict[str, tuple[float, float]]]:
    """Min–max scale each metric column to 0–1 for shape comparison (§B1).

    Args:
        frame: a tidy frame with a ``ts`` column plus one column per
            metric key.
        metric_keys: which columns to scale.

    Returns:
        ``(scaled_frame, ranges)`` where ``scaled_frame`` is a copy with
        each metric mapped to ``[0, 1]`` over its visible min/max, and
        ``ranges`` maps each key to its real ``(min, max)`` so the caller
        can disclose and recover the absolute scale. A constant series
        (min == max) maps to the mid-line ``0.5``; ``NaN`` stays ``NaN``.
    """
    out = frame.copy()
    ranges: dict[str, tuple[float, float]] = {}
    for key in metric_keys:
        if key not in out.columns:
            continue
        col = pd.to_numeric(frame[key], errors="coerce")
        if col.notna().any():
            lo, hi = float(col.min()), float(col.max())
        else:
            lo = hi = float("nan")
        ranges[key] = (lo, hi)
        if pd.notna(lo) and pd.notna(hi) and hi > lo:
            out[key] = (col - lo) / (hi - lo)
        else:
            # Flat (or empty) series: draw at mid-height; keep gaps as gaps.
            out[key] = col.where(col.isna(), 0.5)
    return out, ranges


def compute_correlation(
    frame: pd.DataFrame,
    metric_keys: list[str] | tuple[str, ...],
    *,
    method: str = "pearson",
    lag: int = 0,
) -> CorrelationResult:
    """Correlation of the chosen measures over the aligned frame (§B3).

    For exactly two keys, returns Pearson (default) or Spearman ``r`` on
    the rows where both measures are present, plus the sample size ``n``
    and — for Pearson — a least-squares trend line. For three or more
    keys, returns the pairwise correlation ``matrix`` instead.

    Args:
        frame: aligned comparison frame (see
            :func:`src.data.build_comparison_frame`); rows should already
            be NULL-dropped, but this is robust to residual ``NaN``.
        metric_keys: 2+ metric columns present in ``frame``.
        method: ``"pearson"`` or ``"spearman"``.
        lag: with exactly two keys, shift the *second* measure by this
            many rows before correlating, so a positive lag asks "does
            measure A lead measure B?" (§D). Ignored for the matrix path.
    """
    if method not in CORRELATION_METHODS:
        raise ValueError(f"Unknown method {method!r}; expected one of {CORRELATION_METHODS}.")
    keys = tuple(k for k in metric_keys if k in frame.columns)
    if len(keys) < 2:
        return CorrelationResult(method, keys, n=0, lag=lag)

    sub = frame[list(keys)].apply(pd.to_numeric, errors="coerce")

    if len(keys) == 2:
        a, b = keys
        if lag:
            sub = sub.copy()
            sub[b] = sub[b].shift(lag)
        sub = sub.dropna()
        n = int(len(sub))
        if n < 2:
            return CorrelationResult(method, keys, n=n, lag=lag)
        # Spearman ρ == Pearson r on ranks (scipy-free; ties get mean ranks).
        ranked = sub.rank() if method == "spearman" else sub
        r = ranked[a].corr(ranked[b], method="pearson")
        r = None if pd.isna(r) else float(r)
        slope = intercept = None
        if method == "pearson" and r is not None:
            try:
                coeffs = np.polyfit(sub[a].to_numpy(dtype=float), sub[b].to_numpy(dtype=float), 1)
                slope, intercept = float(coeffs[0]), float(coeffs[1])
            except (np.linalg.LinAlgError, ValueError, TypeError):
                slope = intercept = None
        return CorrelationResult(method, keys, n=n, lag=lag, r=r, slope=slope, intercept=intercept)

    # Three or more measures -> correlation matrix (§B3 heatmap path).
    sub = sub.dropna()
    ranked = sub.rank() if method == "spearman" else sub
    matrix = ranked.corr(method="pearson")
    return CorrelationResult(method, keys, n=int(len(sub)), lag=lag, matrix=matrix)


@dataclass(frozen=True)
class CorrelationVerdict:
    """Lay-friendly reading of a coefficient (consolidation plan §B3).

    ``level`` is the strength band (``-1`` undefined, ``0`` no/weak,
    ``1`` moderate, ``2`` strong); ``badge`` is a neutral Streamlit badge
    colour for that band (correlation is not "good"/"bad", so the ramp is
    grey→blue→violet, never red/green). ``arrow`` (``↑``/``↓``) and the
    worded ``label`` carry the sign so colour is never the only channel.
    """

    r: float | None
    level: int
    strength: str  # "no / weak" | "moderate" | "strong" | "—"
    direction: str  # "positive" | "negative" | ""
    arrow: str  # "↑" | "↓" | ""
    label: str  # full phrase, e.g. "Strong positive"
    badge: str  # Streamlit badge colour for the strength band


def correlation_verdict(r: float | None) -> CorrelationVerdict:
    """Band a coefficient into a plain-language verdict (plan §B3).

    Lay 3-band cut-offs on ``|r|``: **no/weak** below 0.3, **moderate**
    from 0.3 to 0.7 inclusive, **strong** above 0.7. For a missing ``r``
    (a constant series or too few samples) the verdict is an explicit
    "Not enough data" rather than a misleading 0.
    """
    if r is None or pd.isna(r):
        return CorrelationVerdict(None, -1, "—", "", "", "Not enough data", "gray")
    magnitude = abs(r)
    if magnitude < 0.3:
        level, strength, badge = 0, "no / weak", "gray"
    elif magnitude <= 0.7:
        level, strength, badge = 1, "moderate", "blue"
    else:
        level, strength, badge = 2, "strong", "violet"
    direction = "positive" if r > 0 else "negative"
    if level == 0:  # too weak to trust the sign — don't imply a direction
        return CorrelationVerdict(float(r), level, strength, direction, "", "No / weak link", badge)
    arrow = "↑" if r > 0 else "↓"
    return CorrelationVerdict(
        float(r), level, strength, direction, arrow, f"{strength.capitalize()} {direction}", badge
    )
