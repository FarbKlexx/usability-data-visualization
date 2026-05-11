"""Database access layer.

Exposes a cached SQLAlchemy engine for the air-quality Postgres
instance. Pages should not import psycopg or SQLAlchemy directly;
instead call ``get_engine()`` and pass the result to pandas or
queries defined in ``queries.py``.
"""

from src.db.connection import get_engine

__all__ = ["get_engine"]
