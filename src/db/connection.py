"""SQLAlchemy engine factory for the Postgres backend.

The engine is built lazily and cached per-process. When running inside
Streamlit it is cached at the resource level via ``@st.cache_resource``
so it survives reruns; outside Streamlit (CLI tools, tests) a
module-level cache is used.

**Connection URL resolution** (first match wins):

1. ``st.secrets["DATABASE_URL"]`` — how Streamlit Community Cloud injects
   the hosted-database URL (see ``DEPLOY.md``).
2. ``$DATABASE_URL`` — environment variable, for other hosts / shells.
3. :data:`DEFAULT_URL` — the local Docker container, for development.

A hosted provider (e.g. Neon) hands out a ``postgresql://…`` URL; we
rewrite the scheme to ``postgresql+psycopg://`` so SQLAlchemy uses the
installed psycopg 3 driver, and disable prepared-statement caching so a
pgbouncer-pooled endpoint can't trip over it.
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


def _normalize(url: str) -> str:
    """Force the psycopg-3 driver scheme (hosted URLs use bare ``postgresql``)."""
    for prefix in ("postgresql+psycopg://", "postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


def _secret_url() -> str | None:
    """Read ``DATABASE_URL`` from ``st.secrets`` if available, else ``None``.

    Accessing ``st.secrets`` with no secrets file raises; we swallow that
    so local dev (no secrets.toml) falls through to env / the default.
    """
    try:
        import streamlit as st

        return st.secrets.get("DATABASE_URL")  # type: ignore[no-any-return]
    except Exception:
        return None


def resolve_url() -> str:
    """The database URL to connect to (secrets → env → local default)."""
    url = _secret_url() or os.environ.get("DATABASE_URL") or DEFAULT_URL
    return _normalize(url)


def _build_engine(url: str) -> Engine:
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        future=True,
        # psycopg 3: don't auto-prepare statements — keeps us compatible with
        # transaction-pooled endpoints (e.g. Neon/pgbouncer pooled hosts).
        connect_args={"prepare_threshold": None},
    )


def _running_in_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
    except ImportError:
        return False
    return get_script_run_ctx(suppress_warning=True) is not None


@lru_cache(maxsize=1)
def _engine_outside_streamlit() -> Engine:
    return _build_engine(resolve_url())


def get_engine() -> Engine:
    """Return a cached SQLAlchemy engine.

    Inside Streamlit this is cached with ``st.cache_resource`` so the same
    engine (and its pool) is shared across reruns and sessions. Outside
    Streamlit a plain ``lru_cache`` is used.
    """

    if _running_in_streamlit():
        import streamlit as st

        @st.cache_resource(show_spinner=False)
        def _cached() -> Engine:
            return _build_engine(resolve_url())

        return _cached()
    return _engine_outside_streamlit()


def check_connection() -> str | None:
    """Return ``None`` if the database is reachable, else an error string.

    Used by the app to show a friendly "configure the database" message
    instead of a raw traceback when the backend is unreachable (e.g. a
    Cloud deploy with no ``DATABASE_URL`` secret set yet).
    """
    from sqlalchemy import text

    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return None
    except Exception as exc:  # noqa: BLE001 — surfaced to the user as guidance
        return str(exc)
