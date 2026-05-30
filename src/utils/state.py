"""Shared cross-filter & view-sharing state (interactivity plan §A1/§A7).

UI interactivity mostly means feeding the existing loaders different
parameters in response to user input. Two pieces of state are *shared*
across pages and therefore live here under one namespaced contract
(``xfilter_*``) instead of being re-invented per page:

* **Active window** — a ``(start, end)`` time window one page can set
  (e.g. by brushing the headline chart) and another reads (plan §A1).
* **Active sensor hand-off** — clicking a sensor on the Map can route the
  user to the Time Series page with that sensor pre-selected.

Plus thin helpers to mirror a view into ``st.query_params`` so a URL is
shareable/bookmarkable and restores the exact view (plan §A7). These are
deliberately tiny and side-effect-explicit: Streamlit binds widgets to
``st.session_state`` keys, so seeding must happen *before* the widget is
created — hence ``seed_session_defaults`` is meant to run at the top of a
page, ``publish_query_params`` at the bottom.
"""

from __future__ import annotations

from datetime import datetime
from typing import Callable

import streamlit as st

# --- Cross-filter window ----------------------------------------------------

_WIN_START = "xfilter_start"
_WIN_END = "xfilter_end"
_ACTIVE_SENSOR = "xfilter_sensor"


def set_active_window(start: datetime, end: datetime) -> None:
    """Publish a ``(start, end)`` window other pages can pick up."""
    st.session_state[_WIN_START] = start
    st.session_state[_WIN_END] = end


def get_active_window() -> tuple[datetime, datetime] | None:
    """Return the shared window, or ``None`` if none is set."""
    start = st.session_state.get(_WIN_START)
    end = st.session_state.get(_WIN_END)
    if isinstance(start, datetime) and isinstance(end, datetime):
        return start, end
    return None


def clear_active_window() -> None:
    """Forget the shared window (keeps Reset reachable, Shneiderman #6)."""
    st.session_state.pop(_WIN_START, None)
    st.session_state.pop(_WIN_END, None)


def hand_off_to_timeseries(table_name: str, *, ts_prefix: str = "ts") -> None:
    """Pre-select a sensor on the Time Series page, then switch to it.

    Sets the Time Series filter-bar's sensor key *before* navigating, so
    the page opens already focused on the clicked sensor (plan §A1 — map
    click → Time Series). ``filter_bar`` only seeds a default when its key
    is absent, so this selection wins.
    """
    st.session_state[f"{ts_prefix}_sensors"] = table_name
    st.session_state[_ACTIVE_SENSOR] = table_name
    st.switch_page("app_pages/timeseries.py")


# --- Query-param view sharing (A7) -----------------------------------------


def seed_session_defaults(specs: dict[str, Callable[[str], object]]) -> None:
    """Seed ``st.session_state`` keys from the URL query params, once.

    ``specs`` maps a session key to a parser for the raw query-param
    string (e.g. ``int``, ``str``, or a splitter for lists). A key is only
    seeded when it is **absent** from session state, so an in-progress
    selection is never clobbered on rerun. Call before any widget that
    binds these keys is created.
    """
    params = st.query_params
    for key, parse in specs.items():
        if key in st.session_state or key not in params:
            continue
        try:
            st.session_state[key] = parse(params[key])
        except (ValueError, TypeError):
            continue  # ignore malformed params rather than crash the page


def publish_query_params(values: dict[str, object]) -> None:
    """Mirror the current view into ``st.query_params`` for sharing.

    Lists are joined with commas; ``None`` drops the key. Writing is
    idempotent — we only assign when the serialized value changed, so we
    don't trigger needless reruns.
    """
    for key, value in values.items():
        if value is None or (isinstance(value, (list, tuple)) and not value):
            if key in st.query_params:
                del st.query_params[key]
            continue
        serialized = ",".join(map(str, value)) if isinstance(value, (list, tuple)) else str(value)
        if st.query_params.get(key) != serialized:
            st.query_params[key] = serialized


def csv_split(raw: str) -> list[str]:
    """Parse a comma-separated query param into a list (drops empties)."""
    return [part for part in raw.split(",") if part]
