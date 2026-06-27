"""Settings — persisted defaults (IA redesign, 2nd pass).

Collapsed to the one admin surface a lay-facing dashboard needs (user
direction A, 5Es: admin weighted last, Hick: fewer decisions):

* **Thresholds** — named reference values, persisted to the database;
  add and delete are reversible (Shneiderman #6) and report their result
  (#3 feedback).
"""

from __future__ import annotations

import streamlit as st

from src.data import (
    dashboard_tables_ready,
    load_thresholds,
)
from src.db import (
    delete_threshold,
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

