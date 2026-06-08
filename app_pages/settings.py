"""Settings — persisted defaults (IA redesign, 2nd pass).

Collapsed to the one admin surface a lay-facing dashboard needs (user
direction A, 5Es: admin weighted last, Hick: fewer decisions):

* **Thresholds** — the page's main content: named reference values that
  the Time Series page draws as default reference lines.
* **Saved views** *(expander)* — reopen a saved Time Series view exactly
  as it was; a reversible capability (Shneiderman #6) kept, just demoted.

The feature-flag toggles were removed: the three optional modules now
render permanently (their flags default to *on*), so no capability was
lost — only a decision the user no longer has to make. Every control is
reversible (#6) and reports its result (#3 feedback).
"""

from __future__ import annotations

import streamlit as st

from src.data import (
    dashboard_tables_ready,
    load_saved_views,
    load_thresholds,
)
from src.db import (
    delete_threshold,
    delete_view,
    save_threshold,
)
from src.utils.metrics import METRICS, get
from src.utils.text import escape_md

st.title(":material/tune: Settings")

dash_ready = dashboard_tables_ready()
if not dash_ready:
    st.warning(
        "The dashboard tables are not present yet. Run "
        "`uv run python scripts/add_dashboard_tables.py` to enable thresholds "
        "and saved views.",
        icon=":material/info:",
    )

# --- Persisted thresholds (the page's main content) ------------------------
st.subheader(":material/horizontal_rule: Saved thresholds")
st.page_link(
    "app_pages/timeseries.py",
    label="Used as reference lines in Time Series",
    icon=":material/timeline:",
)

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

# --- Saved views (demoted into an expander) --------------------------------
with st.expander(":material/bookmarks: Saved views", expanded=False):
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
