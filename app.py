"""Entry point for the Air Quality Usability Dashboard.

This module is intentionally thin: it only wires up navigation and
shared chrome (page config, global header). All real content lives in
``app_pages/`` and all business logic lives in ``src/``.

Run locally with::

    uv run streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Air Quality Dashboard",
    page_icon=":material/air:",
    layout="wide",
    # Nav lives in the left sidebar; start it collapsed so it reads as a
    # burger menu (the » control at top-left slides it out).
    initial_sidebar_state="collapsed",
    menu_items={
        "About": "Air Quality Usability Dashboard — built for the Usability course.",
    },
)

# Grouped into two labelled sections so the menu reads as two sense-clusters
# rather than six equal-rank words (Hick's law + Miller at the menu level;
# 5Es weighting puts the admin surface last). Comparison is folded into the
# Dashboard's Compare tab; Manage became Settings.
PAGES = {
    "Monitor & Analyse": [
        st.Page(
            "app_pages/dashboard.py",
            title="Dashboard",
            icon=":material/dashboard:",
            default=True,
        ),
        st.Page(
            "app_pages/timeseries.py",
            title="Time Series",
            icon=":material/timeline:",
        ),
        st.Page(
            "app_pages/map.py",
            title="Map",
            icon=":material/map:",
        ),
    ],
    "Reference & Settings": [
        st.Page(
            "app_pages/devices.py",
            title="Devices & Data Quality",
            icon=":material/sensors:",
        ),
        st.Page(
            "app_pages/settings.py",
            title="Settings",
            icon=":material/tune:",
        ),
    ],
}

page = st.navigation(PAGES, position="sidebar")


@st.cache_data(ttl=30, show_spinner=False)
def _db_error() -> str | None:
    """Cached health check so every rerun doesn't reconnect."""
    from src.db.connection import check_connection

    return check_connection()


db_error = _db_error()
if db_error:
    st.error(
        "**The dashboard can't reach its database.**\n\n"
        "This app reads an air-quality PostgreSQL + PostGIS database. "
        "On Streamlit Community Cloud, set a `DATABASE_URL` secret pointing "
        "at a hosted Postgres+PostGIS instance (see `DEPLOY.md`). Locally, "
        "start the bundled container with `docker compose up -d`.",
        icon=":material/database_off:",
    )
    with st.expander("Technical detail"):
        st.code(db_error)
    st.stop()

# The sidebar nav opens from a left burger menu. Streamlit's expand control
# defaults to a » chevron and exposes no config hook for that glyph, so this
# is the one unavoidable CSS escape hatch: swap *only the glyph* to the
# Material Symbols "menu" hamburger (☰, codepoint \e5d2). Colour/size stay
# theme-driven (the original span keeps its layout; we overlay the glyph via
# ::after, inheriting the icon font + current colour), so dark mode is intact.
st.html(
    """
    <style>
    [data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {
        visibility: hidden;
        position: relative;
    }
    [data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"]::after {
        content: "\\e5d2";  /* Material Symbols: menu */
        visibility: visible;
        position: absolute;
        inset: 0;
    }

    /* Dashboard filter bar (prefix "ov"): a full bordered card at rest that
       sticks to the top and condenses into a slim top bar once you scroll
       past it. Pure CSS, degrades gracefully.
       Sticky is applied to the bar's *layout wrapper* (selected via :has),
       not the bar itself — the bar's own wrapper is exactly the bar's height
       so it has no room to stick, whereas its parent (the main vertical
       block) is tall. The morph + theme-correct opaque background
       (light-dark(); the bar is otherwise transparent and would bleed when
       stuck) live on the bar. No scroll-timeline support → stays full-size
       sticky; no :has support → not sticky but otherwise unchanged. */
    [data-testid="stLayoutWrapper"]:has(> .st-key-ov_bar) {
        position: sticky;
        top: 3.5rem;  /* clear Streamlit's ~56px fixed header (it sits above) */
        z-index: 100;
    }
    .st-key-ov_bar {
        width: 100%;
        background: light-dark(rgb(255, 255, 255), rgb(13, 17, 23));
        transition: width .18s ease, max-width .18s ease, margin-left .18s ease,
                    padding .18s ease, border-radius .18s ease, box-shadow .18s ease;
        will-change: width, margin, padding, box-shadow, border-radius;
    }
    /* dashboard.py's tiny scroll-watcher toggles .ov-stuck when the bar reaches
       the top. A class + CSS transition (not a scroll-driven animation) is what
       makes this work in EVERY browser — Safari/Firefox don't support
       animation-timeline:scroll(), where the prior approach degraded to
       "always morphed". When stuck: condense, square the corners, drop a
       shadow. The full-bleed *geometry* (width / max-width / margin-left) is
       set inline by the watcher from the main content area's size, so it spans
       the main column and NOT the open sidebar (vw-based bleed would slide
       under it). */
    .st-key-ov_bar.ov-stuck {
        padding-top: 6px;
        padding-bottom: 6px;
        border-radius: 0;
        box-shadow: 0 8px 18px -8px rgba(0, 0, 0, 0.38);
    }

    /* Borderless white cards on the off-white canvas.
       Streamlit's bordered containers, st.metric tiles and st.form are
       transparent + a 1px borderColor stroke, and config.toml exposes no
       fill token for them — so the page canvas goes off-white via
       backgroundColor (config), and the boxes get a solid fill + the stroke
       removed here. The fill is light-dark() so dark mode gets an elevated
       surface, not white. Selectors are stable public hooks (stMetric /
       stForm testids) + the project's own .st-key-* keys (box_* on bordered
       st.container()s, *_bar on filter bars), so this rides out Streamlit's
       internal class churn. A faint shadow keeps the now-strokeless cards
       legible against the canvas. */
    [data-testid="stMetric"],
    [data-testid="stForm"],
    [class*="st-key-box_"],
    .st-key-ts_bar,
    .st-key-cmp_bar {
        background-color: light-dark(rgb(255, 255, 255), rgb(28, 33, 40));
        border-color: transparent;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04),
                    0 1px 3px rgba(16, 24, 40, 0.06);
    }
    /* The sticky Dashboard filter bar keeps its own background + scroll-state
       shadow (above); just drop its stroke to match the other cards. */
    .st-key-ov_bar {
        border-color: transparent;
    }

    /* Streamlit's fixed top bar is transparent by default, so it shows the
       off-white canvas through it. Fill it to match the cards (white in light,
       the elevated surface in dark) — no config token exists for it. */
    [data-testid="stHeader"] {
        background-color: light-dark(rgb(255, 255, 255), rgb(28, 33, 40));
    }

    /* Skeleton loaders — content-shaped placeholders shown while data loads.
       Streamlit ships no st.skeleton widget and the config exposes no token
       for this, so the markup is emitted as class'd divs by
       src/components/skeleton.py and styled here (one documented st.html
       exception, like the others above). Theme-safe via light-dark(); the
       shimmer is a moving highlight gradient over a flat grey fill, and a
       reduced-motion guard drops the animation for users who ask for it. */
    @keyframes aq-skel-shimmer {
        0%   { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    .aq-skel {
        border-radius: 6px;
        background-color: light-dark(rgb(224, 228, 234), rgb(40, 47, 56));
        background-image: linear-gradient(
            90deg,
            transparent 0%,
            light-dark(rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 0.07)) 50%,
            transparent 100%);
        background-size: 200% 100%;
        background-repeat: no-repeat;
        animation: aq-skel-shimmer 1.4s ease-in-out infinite;
    }
    /* a flex row of skeleton blocks (KPI strip, hero) — mirrors the real layout */
    .aq-skel-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    /* a tile-shaped skeleton: same fill, radius and shadow as the real cards
       (st.metric / box_*), so the strip doesn't reflow when values arrive */
    .aq-skel-card {
        flex: 1 1 7rem;
        min-width: 6.5rem;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        background-color: light-dark(rgb(255, 255, 255), rgb(28, 33, 40));
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04),
                    0 1px 3px rgba(16, 24, 40, 0.06);
    }
    @media (prefers-reduced-motion: reduce) {
        .aq-skel { animation: none; }
    }
    </style>
    """
)

page.run()
