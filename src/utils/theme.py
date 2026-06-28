"""Read the live theme config (`.streamlit/config.toml`) at runtime.

The hidden **Theme & Design System** page (``app_pages/theme.py``) uses this
to document the *actual* tokens — primary/background/text colours, the
categorical + sequential chart palettes, the font — rather than a hardcoded
copy that could drift from the config. Pure file read, no DB/network, so a
page can stay I/O-free by importing this instead of opening the file itself.

The TOML nesting maps directly: ``[theme]`` → the returned dict, ``[theme.dark]``
→ its ``"dark"`` key, ``[[theme.fontFaces]]`` → its ``"fontFaces"`` list.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

# src/utils/theme.py → parents[2] is the repo root.
_CONFIG_PATH = Path(__file__).resolve().parents[2] / ".streamlit" / "config.toml"


def theme_config() -> dict:
    """Return the parsed ``[theme]`` table from ``.streamlit/config.toml``.

    Not cached on purpose: the parse is sub-millisecond and re-reading every
    rerun means the showcase always reflects the current config (e.g. while a
    colour is being tweaked). Returns ``{}`` if the file is missing.
    """
    try:
        with _CONFIG_PATH.open("rb") as fh:
            return tomllib.load(fh).get("theme", {})
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        return {}
