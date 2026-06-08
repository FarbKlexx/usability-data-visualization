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
    </style>
    """
)

page.run()
