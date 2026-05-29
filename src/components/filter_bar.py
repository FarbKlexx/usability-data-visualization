"""Global filter toolbar (implementation plan §5.1).

A single top-of-page toolbar — sensor selection + time-range preset —
that embodies several rules at once:

* **Screen edge as an infinite target** (Fitts) — it sits at the top.
* **User in control + reversibility** (Shneiderman #6/#7) — a **Reset**
  button is always present; nothing reloads mid-analysis.
* **Reduce memory load + feedback** (#3/#8) — the active selection is
  echoed back as chips, including the *resolved* date span, so the user
  never has to remember what is filtered.
* **Hick's law** — few, well-grouped controls; presets instead of a date
  picker for the common cases.

Time presets are resolved **relative to the data's own latest reading**,
not wall-clock now: the dataset ends in late 2025, so "last 24 h" means
the 24 h before the newest selected reading (otherwise every view would
be empty — a Gulf-of-Evaluation trap).

State is namespaced by ``prefix`` so multiple instances never collide.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

# label -> lookback window; None == all available data.
RANGE_PRESETS: dict[str, timedelta | None] = {
    "24 h": timedelta(hours=24),
    "7 d": timedelta(days=7),
    "30 d": timedelta(days=30),
    "All": None,
}


@dataclass(frozen=True)
class FilterState:
    """Resolved filter selection handed to the loaders."""

    tables: list[str]
    labels: list[str]
    start: datetime
    end: datetime
    range_key: str

    @property
    def is_empty(self) -> bool:
        return not self.tables


def device_label(row: pd.Series) -> str:
    """Human label for a catalog row: ``"SENSORpi s01 · Minden"``."""
    city = row.get("city")
    base = str(row["name"])
    return f"{base} · {city}" if isinstance(city, str) and city else base


def _label_map(pool: pd.DataFrame) -> dict[str, str]:
    return {r["table_name"]: device_label(r) for _, r in pool.iterrows()}


def filter_bar(
    devices: pd.DataFrame,
    *,
    prefix: str,
    multi: bool = False,
    pool: pd.DataFrame | None = None,
    default_tables: list[str] | None = None,
    default_range: str = "7 d",
) -> FilterState:
    """Render the toolbar and return the resolved :class:`FilterState`."""
    if pool is None:
        pool = devices[devices["has_data"]]
    pool = pool[pool["table_name"].notna()].copy()
    options = list(pool["table_name"])
    labels = _label_map(pool)

    k_sensors = f"{prefix}_sensors"
    k_range = f"{prefix}_range"

    if default_tables is None:
        default_tables = options[:1]
    default_tables = [t for t in default_tables if t in options] or options[:1]

    # Seed defaults once (widgets bind to these keys thereafter).
    if k_sensors not in st.session_state:
        st.session_state[k_sensors] = default_tables if multi else default_tables[0]
    if k_range not in st.session_state:
        st.session_state[k_range] = default_range

    def _reset() -> None:
        st.session_state[k_sensors] = default_tables if multi else default_tables[0]
        st.session_state[k_range] = default_range

    with st.container(border=True):
        c_sensor, c_range, c_reset = st.columns([0.56, 0.32, 0.12], vertical_alignment="bottom")
        with c_sensor:
            if multi:
                st.multiselect(
                    "Sensors", options=options, format_func=lambda t: labels.get(t, t),
                    key=k_sensors, help="Pick one or more sensors to display.",
                )
            else:
                st.selectbox(
                    "Sensor", options=options, format_func=lambda t: labels.get(t, t),
                    key=k_sensors, help="Pick the sensor to display.",
                )
        with c_range:
            st.segmented_control(
                "Time range", options=list(RANGE_PRESETS), key=k_range,
                help="Window before the most recent reading.",
            )
        with c_reset:
            st.button(
                "Reset", icon=":material/restart_alt:", on_click=_reset,
                width="stretch", help="Restore the default sensor and range.",
            )

    # Resolve selection -> tables + time window.
    raw = st.session_state[k_sensors]
    tables = list(raw) if isinstance(raw, list) else ([raw] if raw else [])
    range_key = st.session_state[k_range] or default_range

    if not tables:
        st.warning("Select at least one sensor to see data.", icon=":material/info:")
        now = datetime(2025, 1, 1)
        return FilterState([], [], now, now, range_key)

    sel = devices[devices["table_name"].isin(tables)]
    last_ts = pd.to_datetime(sel["last_ts"]).max()
    first_ts = pd.to_datetime(sel["first_ts"]).min()
    end = (last_ts + timedelta(seconds=1)).to_pydatetime()
    delta = RANGE_PRESETS[range_key]
    start = first_ts.to_pydatetime() if delta is None else (last_ts - delta).to_pydatetime()

    _render_chips([labels.get(t, t) for t in tables], range_key, start, end)
    return FilterState(tables, [labels.get(t, t) for t in tables], start, end, range_key)


def _render_chips(sensor_labels: list[str], range_key: str, start: datetime, end: datetime) -> None:
    """Echo the active filters back as badges (closure + memory relief)."""
    span = f"{start:%Y-%m-%d %H:%M} → {end:%Y-%m-%d %H:%M}"
    chips = " ".join(f":blue-badge[:material/sensors: {lbl}]" for lbl in sensor_labels)
    st.markdown(
        f"{chips}  :gray-badge[:material/schedule: {range_key}]  "
        f":gray-badge[:material/date_range: {span}]"
    )
