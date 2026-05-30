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
page.run()
