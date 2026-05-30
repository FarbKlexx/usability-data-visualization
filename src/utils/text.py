"""Small text helpers for safe rendering.

User-supplied strings (annotation labels/notes, saved-view names,
threshold labels) are written to the DB and later shown via
``st.markdown``. Streamlit escapes raw HTML, but it still *interprets*
Markdown — so a label like ``[click](http://evil)`` would render as a
link and ``**x**`` as bold. :func:`escape_md` defangs the inline Markdown
specials so user text shows literally, without reaching for raw HTML
(which CLAUDE.md forbids).
"""

from __future__ import annotations

# Inline Markdown specials that can alter rendering or inject links.
# Backslash must be escaped first (it is the escape character itself).
_MD_SPECIALS = "\\`*_[]()<>~|#"


def escape_md(value: object) -> str:
    """Backslash-escape inline Markdown specials in ``value``.

    Returns a string safe to interpolate into ``st.markdown`` so the text
    renders literally (no bold/italic/links/code/HTML from user input).
    """
    text = str(value)
    out = []
    for ch in text:
        if ch in _MD_SPECIALS:
            out.append("\\")
        out.append(ch)
    return "".join(out)
