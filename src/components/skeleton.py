"""Skeleton loaders — content-shaped placeholders shown while data loads.

Usability rationale (CONTEXT.md §Feedback / Shneiderman #1): an abstract,
*content-shaped* grey placeholder is perceived as faster than a spinner and,
unlike a spinner, tells the user **what** is loading and **where** it will
appear (NN/g "skeleton screens"; Wroblewski). The shapes here mirror the real
widgets they stand in for — a tile-shaped block for a tile, a chart-shaped
block for a chart — so the layout doesn't jump when the data arrives (no
cumulative layout shift, Shneiderman #3 feedback without disorientation).

Mechanics (Streamlit's synchronous model): a page reserves a slot with
``st.empty()``, fills it with one of these skeletons, runs the (blocking,
cached) loader, then swaps the real content into the *same* slot. Streamlit
flushes the skeleton delta to the browser before the blocking query, so it is
visible during a real load; with ``@st.cache_data`` the swap is instant on a
cache hit, so the skeleton only actually shows when something is genuinely
being fetched.

Theming: every block is styled by the global CSS in ``app.py`` (the ``.aq-skel*``
classes, theme-safe via ``light-dark()``, with a ``prefers-reduced-motion``
guard that drops the shimmer). These helpers only emit the class'd markup — no
inline ``<style>``. This is a documented ``st.html`` exception, on the same
footing as the other chrome hooks in ``app.py``: Streamlit ships no
``st.skeleton`` widget, and the design system exposes no token for this, so the
markup escape hatch is the only way to render it while keeping the styling
centralised and theme-correct.
"""

from __future__ import annotations

import streamlit as st


def _bar(width: str = "100%", height: str = "0.85rem", margin_top: str = "0") -> str:
    """One shimmering grey block (the atom every skeleton is built from)."""
    return (
        "<div class='aq-skel' "
        f"style='width:{width};height:{height};margin-top:{margin_top}'></div>"
    )


def _emit(markup: str) -> None:
    """Render one skeleton group. Styling lives in app.py's global CSS."""
    st.html(markup)


def lines(widths: tuple[str, ...] = ("85%", "60%", "40%"), height: str = "0.85rem") -> None:
    """A stack of text-line placeholders (e.g. a verdict / caption block)."""
    _emit("".join(_bar(w, height, "0" if i == 0 else "0.55rem") for i, w in enumerate(widths)))


def block(height: int | str = 280) -> None:
    """A single large block sized like a chart or a map."""
    h = f"{height}px" if isinstance(height, int) else height
    _emit(_bar("100%", h))


def hero() -> None:
    """Skeleton for the hero card: a verdict heading above the slim AQ meter."""
    _emit(_bar("55%", "1.6rem") + _bar("100%", "8px", "0.8rem"))


def tiles(n: int) -> None:
    """A horizontal strip of ``n`` metric-tile-shaped skeleton cards."""
    card = "<div class='aq-skel-card'>" + _bar("70%", "0.7rem") + _bar("55%", "1.5rem", "0.6rem") + "</div>"
    _emit(f"<div class='aq-skel-row'>{card * n}</div>")


def tiles_stack(n: int) -> None:
    """``n`` metric-tile-shaped skeleton cards stacked vertically (a stat column)."""
    card = (
        "<div class='aq-skel-card' style='margin-bottom:0.5rem'>"
        + _bar("60%", "0.7rem")
        + _bar("45%", "1.4rem", "0.5rem")
        + "</div>"
    )
    _emit(card * n)
