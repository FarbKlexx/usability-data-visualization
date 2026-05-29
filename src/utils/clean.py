"""Central sentinel / fault cleaning (implementation plan §6.3).

The dataset contains device saturation ceilings (PM2.5 caps at 999.9,
PM10 at 1999.9) and hard faults (temp1 at 85 °C). Plotting those would
distort axes and mislead — a dishonest chart (CONTEXT ethics, plan
§1.3 quirk #1).

This module replaces such readings with ``NaN`` (so the rest of the row
survives for other metrics) and **reports how many were hidden** so the
UI can disclose it ("n values ≥ measuring range hidden"). Cleaning is
applied centrally in the data layer, never re-invented per chart, so
every view tells the same story.

Nothing is dropped *silently*: the distribution view can still request
the raw frame to surface the ceilings honestly (plan §3 candidate 6).
"""

from __future__ import annotations

import pandas as pd

from src.utils.metrics import METRICS, get


def clean_series(s: pd.Series, key: str, *, drop_implausible: bool = False) -> tuple[pd.Series, int]:
    """Blank out sentinel (and optionally out-of-range) values in a series.

    Args:
        s: the raw values.
        key: metric key (looked up in the registry).
        drop_implausible: if True, also blank values outside the
            metric's plausible ``[vmin, vmax]`` range (used for charts
            that must not be skewed by obvious faults).

    Returns:
        ``(cleaned_series, n_hidden)`` — a copy with offending values set
        to ``NaN`` and the count of values hidden.
    """
    metric = get(key)
    numeric = pd.to_numeric(s, errors="coerce")
    mask = pd.Series(False, index=s.index)

    if metric.sentinel is not None:
        mask |= numeric >= metric.sentinel
    if drop_implausible:
        mask |= (numeric < metric.vmin) | (numeric > metric.vmax)

    n_hidden = int(mask.sum())
    cleaned = numeric.mask(mask)
    return cleaned, n_hidden


def clean_frame(
    df: pd.DataFrame,
    keys: list[str] | tuple[str, ...] | None = None,
    *,
    drop_implausible: bool = False,
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Clean every metric column present in ``df``.

    Args:
        df: tidy frame with one column per metric key.
        keys: which metric columns to clean; defaults to every known
            metric that appears in ``df``.
        drop_implausible: forwarded to :func:`clean_series`.

    Returns:
        ``(cleaned_df, hidden_counts)`` where ``hidden_counts`` maps a
        metric key to how many values were hidden (only non-zero entries
        are included, so an empty dict means "nothing hidden").
    """
    if keys is None:
        keys = [k for k in METRICS if k in df.columns]

    out = df.copy()
    counts: dict[str, int] = {}
    for key in keys:
        if key not in out.columns:
            continue
        out[key], n = clean_series(out[key], key, drop_implausible=drop_implausible)
        if n:
            counts[key] = n
    return out, counts


def hidden_notice(counts: dict[str, int]) -> str | None:
    """Build a one-line disclosure string from :func:`clean_frame` counts.

    Returns ``None`` when nothing was hidden, so callers can simply::

        if (msg := hidden_notice(counts)):
            st.caption(msg)
    """
    if not counts:
        return None
    parts = [f"{n} {get(k).label}" for k, n in counts.items()]
    joined = ", ".join(parts)
    return f"{joined} reading(s) at/above the sensor's measuring range were hidden."
