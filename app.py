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
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Air Quality Usability Dashboard — built for the Usability course.",
    },
)

PAGES = [
    st.Page(
        "app_pages/overview.py",
        title="Overview",
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
    st.Page(
        "app_pages/comparison.py",
        title="Comparison",
        icon=":material/compare_arrows:",
    ),
    st.Page(
        "app_pages/devices.py",
        title="Devices & Data Quality",
        icon=":material/sensors:",
    ),
    st.Page(
        "app_pages/manage.py",
        title="Manage",
        icon=":material/tune:",
    ),
]

page = st.navigation(PAGES, position="top")


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

page.run()
