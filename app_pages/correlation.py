"""Correlation page — do two measures on one sensor move together?

Verdict-first |r| (a plain-language strength/direction badge) with the
chart as the *evidence*, not the headline. Two measures → a scatter (with
fit line) or a normalised overlay; three or more → a correlation heatmap.
Saturation sentinels are cleaned out before pairing and disclosed.

The layout mirrors the **Dashboard cockpit** so the two pages read as one
product: a verdict **hero card** (the strongest relationship, stated in
plain language above its r/n badges — the "single focal point") sits over
the **chart tile** (the evidence). Both are bordered ``box_*`` cards on the
off-white canvas with icon+title headers whose operating hints live in
tooltips, and a skeleton-swap load — exactly the Dashboard's bento
treatment.

This was the Dashboard's *Correlation* tab; it is now its own destination
with a single-sensor toolbar (``corr`` prefix) and bookmarkable URL state.
"""

from __future__ import annotations

import itertools

import streamlit as st

from src.components import charts, filter_bar, skeleton
from src.data import available_metrics, build_comparison_frame, load_devices, load_timeseries
from src.utils.clean import hidden_notice
from src.utils.correlate import compute_correlation, correlation_verdict, normalize_frame
from src.utils.metrics import get
from src.utils.state import csv_split, publish_query_params, seed_session_defaults

_PLOT = {"theme": "streamlit", "width": "stretch", "config": {"displaylogo": False}}
# The |r| reading, stated once and reused wherever the verdict is shown.
_R_HELP = (
    "Strength by |r|: <0.3 none/weak · 0.3–0.7 moderate · >0.7 strong. "
    "Sign (↑/↓) = rise together vs. move oppositely. Correlation is not causation."
)

st.title(":material/scatter_plot: Correlation")
st.caption("Do two measures on one sensor move together? The verdict comes first; the chart is the evidence.")

devices = load_devices()
pool = devices[devices["has_data"]]

# Restore a shared view from the URL before any widget binds (bookmarkable).
seed_session_defaults({"corr_sensors": str, "corr_range": str, "corr_measures": csv_split})
_valid_tables = set(pool["table_name"].dropna())
if st.session_state.get("corr_sensors") not in _valid_tables:
    st.session_state.pop("corr_sensors", None)

# === ZONE 0: single-sensor toolbar (same component + card as the hub) ========
fs = filter_bar(
    devices, prefix="corr", multi=False, pool=pool, group_by_type=True,
    default_tables=["sensor_000aeb8337ac"], default_range="7 d",
)
if fs.is_empty:
    st.stop()
table = fs.tables[0]

options = [m.key for m, _ in available_metrics(table)]
default_corr = [k for k in ("pm2_5", "temp1") if k in options] or options[:2]
if "corr_measures" in st.session_state:
    kept = [m for m in st.session_state["corr_measures"] if m in options]
    st.session_state["corr_measures"] = kept or default_corr
else:
    st.session_state["corr_measures"] = default_corr
corr_measures = st.multiselect(
    "Measures to relate", options=options, key="corr_measures", format_func=lambda k: get(k).label,
    help="Two or more measures recorded by this device; paired per reading.",
)

if len(corr_measures) < 2:
    st.info("Pick at least two measures to see whether they relate.", icon=":material/info:")
else:
    # Skeleton both cards (verdict hero + chart tile) while the paired-readings
    # query runs, then swap the real content into the same slot — the hub's load
    # pattern, so the layout never jumps (content-shaped, not a spinner).
    corr_ph = st.empty()
    with corr_ph.container():
        with st.container(border=True, key="box_corr_verdict_skel"):
            skeleton.lines(widths=("40%", "60%"), height="1.2rem")
        with st.container(border=True, key="box_corr_chart_skel"):
            skeleton.block(380)

    corr_df, corr_hidden, _ = load_timeseries(table, tuple(corr_measures), fs.start, fs.end, clean=True)

    with corr_ph.container():
        frame = build_comparison_frame(corr_df, corr_measures)
        if len(frame) < 2:
            st.warning(
                "Not enough paired readings in this range to compare these measures.",
                icon=":material/info:",
            )
        else:
            # Every pair's verdict; the strongest |r| becomes the focal hero
            # (the hub's "single focal point"), the rest are listed beneath it.
            pairs = [
                (a, b, res, correlation_verdict(res.r))
                for a, b in itertools.combinations(corr_measures, 2)
                for res in (compute_correlation(frame, (a, b)),)
            ]
            hero_i = max(
                range(len(pairs)),
                key=lambda i: abs(pairs[i][2].r) if pairs[i][2].r is not None else -1.0,
            )

            # === ZONE 1: verdict hero card (mirrors the hub's verdict hero) ===
            with st.container(border=True, key="box_corr_verdict"):
                st.markdown("**:material/compare_arrows: Relationship**", help=_R_HELP)
                a, b, res, v = pairs[hero_i]
                arrow = f"{v.arrow} " if v.arrow else ""
                st.subheader(f"{arrow}{v.label}")
                r_text = "–" if res.r is None else f"{res.r:+.2f}"
                st.markdown(
                    f":{v.badge}-badge[{get(a).short_label} ↔ {get(b).short_label}] "
                    f":gray-badge[r = {r_text}] :gray-badge[n = {res.n:,}]"
                )
                # Remaining pairs (only present when 3+ measures are selected).
                for i, (a2, b2, res2, v2) in enumerate(pairs):
                    if i == hero_i:
                        continue
                    arrow2 = f"{v2.arrow} " if v2.arrow else ""
                    r2 = "–" if res2.r is None else f"{res2.r:+.2f}"
                    st.markdown(
                        f":{v2.badge}-badge[{arrow2}{v2.label}] "
                        f"**{get(a2).short_label} ↔ {get(b2).short_label}** · r = {r2} · n = {res2.n:,}"
                    )

            # === ZONE 2: chart tile (the evidence; a hub bento cell) =========
            with st.container(border=True, key="box_corr_chart"):
                if len(corr_measures) == 2:
                    # Title left, view toggle top-right — the hub's bento header.
                    head, ctrl = st.columns([0.55, 0.45], vertical_alignment="center")
                    head.markdown(
                        "**:material/scatter_plot: How they relate**",
                        help="Scatter shows the relationship itself; Overlay compares the two curve shapes over time.",
                    )
                    with ctrl.container(horizontal=True, horizontal_alignment="right"):
                        view = st.segmented_control(
                            "Chart", options=["Scatter", "Overlay"], key="corr_view",
                            default="Scatter", label_visibility="collapsed",
                        ) or "Scatter"
                    a, b, res, _ = pairs[hero_i]
                    if view == "Scatter":
                        st.plotly_chart(
                            charts.scatter_correlation(frame, a, b, slope=res.slope, intercept=res.intercept),
                            **_PLOT,
                        )
                    else:
                        norm, ranges = normalize_frame(frame, corr_measures)
                        st.plotly_chart(charts.normalized_overlay(norm, corr_measures, ranges), **_PLOT)
                else:
                    st.markdown(
                        "**:material/grid_on: Correlation matrix**",
                        help="Pairwise r for every measure pair; the value is printed in each cell, "
                             "so colour is never the only signal.",
                    )
                    res = compute_correlation(frame, tuple(corr_measures))
                    st.plotly_chart(charts.correlation_heatmap(res.matrix), **_PLOT)

                if (notice := hidden_notice(corr_hidden)):
                    st.caption(f":material/visibility_off: {notice}")

# Publish the current view to the URL (shareable/bookmarkable).
publish_query_params(
    {"corr_sensors": table, "corr_range": fs.range_key, "corr_measures": st.session_state.get("corr_measures", [])}
)
