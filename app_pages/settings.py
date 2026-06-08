"""Manage page — live configuration & persisted UI state (plan §B3, §B6).

A small admin surface that writes back to the database:

* **Feature flags (§B3)** — the ``func_*`` rows of ``tbl_systemconfiguration``
  become live toggles. Dashboard-owned flags (``func_dashboard_*``) gate
  optional modules on the Time Series page; flipping one here shows/hides
  that module on the next visit.
* **Thresholds (§B6)** — persisted metric thresholds that the Time Series
  page loads as default reference lines.
* **Saved views (§A7 → §B6)** — named filter states; *Apply* reopens the
  Time Series page with that exact sensor/measures/range/bucket.

Every control is reversible (Shneiderman #6) and reports its result
(#3 feedback). Writes go through ``src.db`` and clear the relevant caches.
"""

from __future__ import annotations

import streamlit as st

from src.data import (
    dashboard_tables_ready,
    load_feature_flags,
    load_saved_views,
    load_thresholds,
)
from src.db import (
    delete_threshold,
    delete_view,
    save_threshold,
    set_feature_flag,
)
from src.utils.metrics import METRICS, get
from src.utils.text import escape_md

st.title(":material/tune: Manage")
st.caption("Configure optional modules and manage saved thresholds and views.")

dash_ready = dashboard_tables_ready()
if not dash_ready:
    st.warning(
        "The dashboard tables are not present yet. Run "
        "`uv run python scripts/add_dashboard_tables.py` to enable thresholds "
        "and saved views. Feature flags below still work.",
        icon=":material/info:",
    )

# --- Feature flags (B3) -----------------------------------------------------
st.subheader(":material/toggle_on: Optional modules")
st.caption("Turn dashboard modules on or off. Changes take effect immediately.")

flags = load_feature_flags()
dash_flags = flags[flags["ckey"].str.startswith("func_dashboard_")]
other_flags = flags[~flags["ckey"].str.startswith("func_dashboard_")]


def _toggle(ckey: str, label: str, active: bool, help_text: str | None = None) -> None:
    """Render a flag toggle; persist + rerun when the user flips it."""
    new = st.toggle(label, value=active, key=f"ff_{ckey}", help=help_text)
    if new != active:
        set_feature_flag(ckey, new)
        st.toast(f"{label}: {'on' if new else 'off'}", icon=":material/check:")
        st.rerun()


if dash_flags.empty:
    st.info("No dashboard modules registered.", icon=":material/info:")
else:
    for _, r in dash_flags.iterrows():
        label = str(r["cvalue"]) if r["cvalue"] else str(r["ckey"])
        _toggle(str(r["ckey"]), label, bool(r["active"]), help_text=str(r["ckey"]))

with st.expander(f"Other app flags ({len(other_flags)})", expanded=False):
    st.caption("Legacy `func_*` flags from the source system, shown for completeness.")
    for _, r in other_flags.iterrows():
        _toggle(str(r["ckey"]), str(r["ckey"]), bool(r["active"]))

st.divider()

# --- Persisted thresholds (B6) ---------------------------------------------
st.subheader(":material/horizontal_rule: Saved thresholds")
st.caption("Defaults for the reference lines on the Time Series page.")

if not dash_ready:
    st.info("Run the migration to enable saved thresholds.", icon=":material/info:")
else:
    thr = load_thresholds()
    if thr.empty:
        st.caption("No thresholds saved yet.")
    else:
        for _, t in thr.iterrows():
            m = get(t["metric"]) if t["metric"] in METRICS else None
            name = f"{m.label} ({m.unit})" if m else str(t["metric"])
            lc, dc = st.columns([0.85, 0.15], vertical_alignment="center")
            lc.markdown(
                f":blue-badge[{name}] **{t['value']:g}**"
                f"{(' · ' + escape_md(t['label'])) if t['label'] else ''}"
            )
            if dc.button("Delete", icon=":material/delete:", key=f"del_thr_{t['id']}"):
                delete_threshold(int(t["id"]))
                st.rerun()

    with st.form("add_threshold", border=True):
        st.markdown("**Add a threshold**")
        ac1, ac2, ac3 = st.columns([0.4, 0.3, 0.3])
        metric_key = ac1.selectbox(
            "Measure", options=list(METRICS), format_func=lambda k: get(k).label
        )
        value = ac2.number_input("Value", value=float(round(get(metric_key).vmax * 0.2, 1)), step=1.0)
        tlabel = ac3.text_input("Label", placeholder="e.g. WHO daily")
        if st.form_submit_button("Save threshold", icon=":material/save:", type="primary"):
            try:
                save_threshold(metric_key, float(value), tlabel.strip())
                st.success("Threshold saved.", icon=":material/check_circle:")
                st.rerun()
            except Exception as exc:  # noqa: BLE001
                st.error(f"Could not save: {exc}", icon=":material/error:")

st.divider()

# --- Saved views (A7 → B6) --------------------------------------------------
st.subheader(":material/bookmarks: Saved views")
st.caption("Reopen a saved Time Series view exactly as it was. Create views from the Time Series page.")

if not dash_ready:
    st.info("Run the migration to enable saved views.", icon=":material/info:")
else:
    views = load_saved_views()
    if views.empty:
        st.caption("No saved views yet — use 'Save this view' on the Time Series page.")
    else:
        for _, v in views.iterrows():
            params = v["params_json"] or {}
            measures = params.get("measures", [])
            summary = (
                f"{params.get('table', '?')} · {', '.join(measures) or 'no measures'} · "
                f"{params.get('range', '?')} · {params.get('bucket', 'Auto')}"
            )
            nc, ac, dc = st.columns([0.6, 0.2, 0.2], vertical_alignment="center")
            nc.markdown(f"**{escape_md(v['name'])}**  \n:gray-badge[{escape_md(summary)}]")
            if ac.button("Apply", icon=":material/open_in_new:", key=f"apply_view_{v['id']}"):
                st.session_state["ts_sensors"] = params.get("table")
                st.session_state["ts_range"] = params.get("range", "30 d")
                st.session_state["ts_measures"] = list(measures)
                st.session_state["ts_bucket"] = params.get("bucket", "Auto")
                st.switch_page("app_pages/timeseries.py")
            if dc.button("Delete", icon=":material/delete:", key=f"del_view_{v['id']}"):
                delete_view(int(v["id"]))
                st.rerun()
