"""SQLAlchemy engine factory for the Postgres dump.

The engine is built lazily and cached per-process. When running inside
Streamlit, it is also cached at the resource level via
``@st.cache_resource`` so it survives reruns; outside Streamlit
(e.g. the CLI connection test) we fall back to a module-level cache.
"""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

load_dotenv()

DEFAULT_URL = (
    "postgresql+psycopg://smartmonitoring_airquality"
    "@localhost:5432/smartmonitoring_airquality"
)


def _build_engine(url: str) -> Engine:
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        future=True,
    )


def _running_in_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
    except ImportError:
        return False
    return get_script_run_ctx(suppress_warning=True) is not None


@lru_cache(maxsize=1)
def _engine_outside_streamlit() -> Engine:
    return _build_engine(os.environ.get("DATABASE_URL", DEFAULT_URL))


def get_engine() -> Engine:
    """Return a cached SQLAlchemy engine.

    Inside Streamlit, this is cached with ``st.cache_resource`` so the
    same engine (and its pool) is shared across reruns and sessions.
    Outside Streamlit, a plain ``lru_cache`` is used.
    """

    if _running_in_streamlit():
        import streamlit as st

        @st.cache_resource(show_spinner=False)
        def _cached() -> Engine:
            return _build_engine(os.environ.get("DATABASE_URL", DEFAULT_URL))

        return _cached()
    return _engine_outside_streamlit()
