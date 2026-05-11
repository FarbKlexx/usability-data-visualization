"""Data access layer.

Wraps every source of truth (Postgres dump in ``pgsql/``, CSV/Parquet
in ``assets/``, remote APIs) behind cached loader functions so pages
never touch I/O directly.
"""
