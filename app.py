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
        "app_pages/explore.py",
        title="Explore",
        icon=":material/insights:",
    ),
]

page = st.navigation(PAGES, position="top")
page.run()
