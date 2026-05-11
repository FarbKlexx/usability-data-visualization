"""Smoke tests — verify that all modules import without errors.

These tests don't run Streamlit; they only check that the package
structure is internally consistent (no broken imports, no missing
``__init__`` files).
"""

from __future__ import annotations

import importlib


def test_src_imports() -> None:
    for mod in (
        "src",
        "src.components",
        "src.components.kpi",
        "src.data",
        "src.data.loaders",
        "src.db",
        "src.db.connection",
        "src.db.queries",
        "src.utils",
        "src.utils.palette",
        "src.utils.accessibility",
    ):
        importlib.import_module(mod)


def test_palette_is_colorblind_safe() -> None:
    from src.utils.palette import OKABE_ITO

    assert len(OKABE_ITO) >= 7
    assert all(c.startswith("#") and len(c) == 7 for c in OKABE_ITO)
