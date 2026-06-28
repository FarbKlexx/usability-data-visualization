"""Entry point for the Air Quality Usability Dashboard.

This module is intentionally thin: it only wires up navigation and
shared chrome (page config, global header). All real content lives in
``app_pages/`` and all business logic lives in ``src/``.

Run locally with::

    uv run streamlit run app.py
"""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Air Quality Dashboard",
    page_icon=":material/air:",
    layout="wide",
    # Nav lives in the left sidebar; start it collapsed. On desktop the CSS in
    # this file restyles "collapsed" into an always-on icon rail (see
    # CLAUDE.md §Theming); the » control expands it to the labelled drawer.
    initial_sidebar_state="collapsed",
    menu_items={
        "About": "Air Quality Usability Dashboard — built for the Usability course.",
    },
)

# Grouped into two labelled sections so the menu reads as two sense-clusters
# rather than six equal-rank words (Hick's law + Miller at the menu level;
# 5Es weighting puts the admin surface last). Comparison is folded into the
# Dashboard's Compare tab; Manage became Settings.
PAGES = {
    "Monitor & Analyse": [
        st.Page(
            "app_pages/dashboard.py",
            title="Dashboard",
            icon=":material/dashboard:",
            default=True,
        ),
        st.Page(
            "app_pages/correlation.py",
            title="Correlation",
            icon=":material/scatter_plot:",
        ),
        # Drill-down from the Dashboard's mobile Routes list; not in the rail.
        st.Page(
            "app_pages/route.py",
            title="Route detail",
            icon=":material/route:",
            visibility="hidden",
        ),
    ],
    "Reference & Settings": [
        st.Page(
            "app_pages/devices.py",
            title="Devices & Data Quality",
            icon=":material/sensors:",
        ),
        st.Page(
            "app_pages/settings.py",
            title="Settings",
            icon=":material/tune:",
        ),
        # Design-system showcase; reachable only by URL (/theme), not in the rail.
        st.Page(
            "app_pages/theme.py",
            title="Theme & Design System",
            icon=":material/palette:",
            visibility="hidden",
        ),
    ],
}

page = st.navigation(PAGES, position="sidebar")


@st.cache_data(ttl=30, show_spinner=False)
def _db_error() -> str | None:
    """Cached health check so every rerun doesn't reconnect."""
    from src.db.connection import check_connection

    return check_connection()


db_error = _db_error()
if db_error:
    st.error(
        "**The dashboard can't reach its database.**\n\n"
        "This app reads an air-quality PostgreSQL + PostGIS database. "
        "On Streamlit Community Cloud, set a `DATABASE_URL` secret pointing "
        "at a hosted Postgres+PostGIS instance (see `DEPLOY.md`). Locally, "
        "start the bundled container with `docker compose up -d`.",
        icon=":material/database_off:",
    )
    with st.expander("Technical detail"):
        st.code(db_error)
    st.stop()

# Theme-safe CSS escape hatches for chrome Streamlit gives no config hook for
# (see CLAUDE.md §Theming for the full annotated list). All verified in light
# and dark. The sidebar expand control keeps Streamlit's own default glyph.
st.html(
    """
    <style>
    /* Dashboard filter bar (prefix "ov"): a full bordered card at rest that
       sticks to the top and condenses into a slim top bar once you scroll
       past it. Pure CSS, degrades gracefully.
       Sticky is applied to the bar's *layout wrapper* (selected via :has),
       not the bar itself — the bar's own wrapper is exactly the bar's height
       so it has no room to stick, whereas its parent (the main vertical
       block) is tall. The morph + theme-correct opaque background
       (light-dark(); the bar is otherwise transparent and would bleed when
       stuck) live on the bar. No scroll-timeline support → stays full-size
       sticky; no :has support → not sticky but otherwise unchanged. */
    [data-testid="stLayoutWrapper"]:has(> .st-key-ov_bar) {
        position: sticky;
        top: 3.5rem;  /* clear Streamlit's ~56px fixed header (it sits above) */
        z-index: 100;
    }
    .st-key-ov_bar {
        width: 100%;
        background: light-dark(rgb(255, 255, 255), rgb(13, 17, 23));
        transition: width .18s ease, max-width .18s ease, margin-left .18s ease,
                    padding .18s ease, border-radius .18s ease, box-shadow .18s ease;
        will-change: width, margin, padding, box-shadow, border-radius;
    }
    /* dashboard.py's tiny scroll-watcher toggles .ov-stuck when the bar reaches
       the top. A class + CSS transition (not a scroll-driven animation) is what
       makes this work in EVERY browser — Safari/Firefox don't support
       animation-timeline:scroll(), where the prior approach degraded to
       "always morphed". When stuck: condense, square the corners, drop a
       shadow. The full-bleed *geometry* (width / max-width / margin-left) is
       set inline by the watcher from the main content area's size, so it spans
       the main column and NOT the open sidebar (vw-based bleed would slide
       under it). */
    .st-key-ov_bar.ov-stuck {
        padding-top: 6px;
        padding-bottom: 6px;
        border-radius: 0;
        box-shadow: 0 8px 18px -8px rgba(0, 0, 0, 0.38);
    }

    /* Borderless white cards on the off-white canvas.
       Streamlit's bordered containers, st.metric tiles and st.form are
       transparent + a 1px borderColor stroke, and config.toml exposes no
       fill token for them — so the page canvas goes off-white via
       backgroundColor (config), and the boxes get a solid fill + the stroke
       removed here. The fill is light-dark() so dark mode gets an elevated
       surface, not white. Selectors are stable public hooks (stMetric /
       stForm testids) + the project's own .st-key-* keys (box_* on bordered
       st.container()s, *_bar on filter bars), so this rides out Streamlit's
       internal class churn. A faint shadow keeps the now-strokeless cards
       legible against the canvas. */
    [data-testid="stMetric"],
    [data-testid="stForm"],
    [class*="st-key-box_"],
    .st-key-ts_bar,
    .st-key-cmp_bar,
    .st-key-corr_bar {
        background-color: light-dark(rgb(255, 255, 255), rgb(28, 33, 40));
        border-color: transparent;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04),
                    0 1px 3px rgba(16, 24, 40, 0.06);
    }
    /* The sticky Dashboard filter bar keeps its own background + scroll-state
       shadow (above); just drop its stroke to match the other cards. */
    .st-key-ov_bar {
        border-color: transparent;
    }

    /* Filter bar: the segmented Time-range pills render shorter than the sensor
       select beside them, so the two controls didn't line up. Pin the pills to
       Streamlit's standard control height (the minElementHeight token, 2.5rem,
       which the select uses) — same rem unit, so they match at any root size. */
    .st-key-ov_bar [data-testid^="stBaseButton-segmented_control"],
    .st-key-ts_bar [data-testid^="stBaseButton-segmented_control"],
    .st-key-cmp_bar [data-testid^="stBaseButton-segmented_control"],
    .st-key-corr_bar [data-testid^="stBaseButton-segmented_control"] {
        min-height: 2.5rem;
    }

    /* --- Equal-height bento cards ------------------------------------------
       Zone 3 is a 2-cell row: the primary chart (or route map) beside its
       location-map / trip-stats context. Each st.container(border=True) sizes
       to its own content, so the cell with less below its chart (no "Full map"
       link, fewer trip tiles) ends up shorter and the row reads ragged.
       Streamlit exposes no "equal-height columns" knob, so stretch the row's
       columns to a shared height and let each card fill its column — the chart
       card and the map card then share one bottom edge. Scoped by :has() to the
       rows that actually hold a bento box, so the hero/KPI rows are untouched;
       vertical_alignment="top" sets align-self on the columns, so it is
       overridden to stretch here. Guarded to wide viewports — on phones the
       columns stack, where equal height is meaningless. */
    @media (min-width: 768px) {
        [data-testid="stHorizontalBlock"]:has(.st-key-box_pmtrend),
        [data-testid="stHorizontalBlock"]:has(.st-key-box_routemap) {
            align-items: stretch;
        }
        [data-testid="stHorizontalBlock"]:has(.st-key-box_pmtrend) > [data-testid="stColumn"],
        [data-testid="stHorizontalBlock"]:has(.st-key-box_routemap) > [data-testid="stColumn"] {
            align-self: stretch;
        }
        [data-testid="stHorizontalBlock"]:has(.st-key-box_pmtrend) > [data-testid="stColumn"] > [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"]:has(.st-key-box_routemap) > [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
            height: 100%;
        }
        .st-key-box_pmtrend, .st-key-box_locmap,
        .st-key-box_routemap, .st-key-box_tripstats {
            height: 100%;
        }
    }

    /* Air-quality meter (markup from src/components/meter.py): a slim pill bar
       with a fixed red→amber→green gradient and a positioned marker. Same
       documented escape hatch as the skeletons — the static look is here, only
       the marker's left offset + fill colour come inline per value. The
       left=worst / right=best ordering + the marker position are the real
       signal, so colour-blind readers lose nothing (colour is never the only
       channel). Gradient colours are the Okabe-Ito severity ramp; fixed in both
       themes because the semantics (red=bad, green=good) are theme-independent. */
    .aq-meter {
        position: relative;
        height: 8px;
        margin: 0.35rem 0 0.15rem;
        border-radius: 999px;
        background: linear-gradient(90deg,
            #D55E00 0%, #E69F00 35%, #F0E442 60%, #009E73 100%);
    }
    .aq-meter-dot {
        position: absolute;
        top: 50%;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        transform: translate(-50%, -50%);
        border: 3px solid #ffffff;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.45);
    }
    /* Subtle neutral band-boundary ticks (the CAQI thresholds): quiet grey
       notches so the scale shows the air-quality cut-offs without competing with
       the dot. The bar's gradient is theme-independent, so the tick colour is too
       (no light-dark needed). The dot is appended after the ticks, so it always
       paints on top. */
    .aq-meter-tick {
        position: absolute;
        top: -2px;
        bottom: -2px;
        width: 2px;
        transform: translateX(-50%);
        background: rgba(55, 60, 65, 0.40);
        border-radius: 1px;
        pointer-events: none;
    }
    /* Zone names above the bar (Good … Poor), so the scale reads without a
       legend. They sit on the card (not the gradient), so theme-aware grey;
       small + muted to stay subordinate to the verdict word and the dot. */
    .aq-meter-labels {
        position: relative;
        height: 1rem;
        margin-bottom: 5px;
        font-size: 0.7rem;
        line-height: 1rem;
    }
    .aq-meter-zone {
        position: absolute;
        transform: translateX(-50%);
        white-space: nowrap;
        color: light-dark(rgba(60, 66, 72, 0.80), rgba(214, 221, 228, 0.78));
    }

    /* Streamlit's fixed top bar is transparent by default, so it shows the
       off-white canvas through it. Fill it to match the cards (white in light,
       the elevated surface in dark) — no config token exists for it. */
    [data-testid="stHeader"] {
        background-color: light-dark(rgb(255, 255, 255), rgb(28, 33, 40));
    }

    /* Round the corners of charts and maps to match the cards (config
       baseRadius is 8px). Plotly draws square corners; clipping the chart
       container rounds both the line-chart plot background and — the main
       win — the opaque OpenStreetMap tiles, which otherwise show square
       corners inside the rounded card. */
    [data-testid="stPlotlyChart"],
    [data-testid="stPlotlyChart"] > div,
    [data-testid="stPlotlyChart"] .stPlotlyChart,
    [data-testid="stPlotlyChart"] .js-plotly-plot,
    [data-testid="stPlotlyChart"] .maplibregl-map {
        border-radius: 8px;
    }
    [data-testid="stPlotlyChart"] {
        overflow: hidden;
    }

    /* Page name surfaced in the fixed top header once the Dashboard filter bar
       sticks (a scroll-condense title). The watcher (end of app.py) injects it
       as a child of the header, sets its left edge to the main column so it
       sits over the stuck bar, and toggles `.ov-visible`. Hidden + inert until
       then. Theme-safe colour via light-dark(). */
    .ov-header-title {
        position: absolute;
        top: 0;
        bottom: 0;
        padding-left: 1rem;
        display: flex;
        align-items: center;
        font-weight: 600;
        font-size: 1.05rem;
        color: light-dark(rgb(31, 35, 40), rgb(230, 237, 243));
        white-space: nowrap;
        pointer-events: none;
        opacity: 0;
        transform: translateY(3px);
        transition: opacity .18s ease, transform .18s ease;
    }
    .ov-header-title.ov-visible {
        opacity: 1;
        transform: translateY(0);
    }

    /* Skeleton loaders — content-shaped placeholders shown while data loads.
       Streamlit ships no st.skeleton widget and the config exposes no token
       for this, so the markup is emitted as class'd divs by
       src/components/skeleton.py and styled here (one documented st.html
       exception, like the others above). Theme-safe via light-dark(); the
       shimmer is a moving highlight gradient over a flat grey fill, and a
       reduced-motion guard drops the animation for users who ask for it. */
    @keyframes aq-skel-shimmer {
        0%   { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    .aq-skel {
        border-radius: 6px;
        background-color: light-dark(rgb(224, 228, 234), rgb(40, 47, 56));
        background-image: linear-gradient(
            90deg,
            transparent 0%,
            light-dark(rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 0.07)) 50%,
            transparent 100%);
        background-size: 200% 100%;
        background-repeat: no-repeat;
        animation: aq-skel-shimmer 1.4s ease-in-out infinite;
    }
    /* a flex row of skeleton blocks (KPI strip, hero) — mirrors the real layout */
    .aq-skel-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    /* a tile-shaped skeleton: same fill, radius and shadow as the real cards
       (st.metric / box_*), so the strip doesn't reflow when values arrive */
    .aq-skel-card {
        flex: 1 1 7rem;
        min-width: 6.5rem;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        background-color: light-dark(rgb(255, 255, 255), rgb(28, 33, 40));
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04),
                    0 1px 3px rgba(16, 24, 40, 0.06);
    }
    @media (prefers-reduced-motion: reduce) {
        .aq-skel { animation: none; }
    }

    /* ===== Persistent navigation rail (desktop) ==========================
       Turn Streamlit's hide-completely collapsed sidebar into an always-on
       ICON RAIL, and its expanded state into a labelled DRAWER. A single
       toggle lives INSIDE the menu (the sidebar's own collapse button, a real
       toggle once it's clickable) and morphs ☰→✕ on open; Streamlit's top-bar
       expand button is removed. Categories render as static
       eyebrows (chevron hidden, header made non-interactive) instead of
       collapsible dropdowns. The app's flex layout (stAppViewContainer is
       display:flex with the sidebar as a flex child) means resizing the
       sidebar reflows the main column automatically — no margin maths.
       Desktop only (min-width:768px); on phones Streamlit's off-canvas burger
       behaviour is left untouched, and with no CSS it degrades to that too. */
    @media (min-width: 768px) {
        /* RAIL — collapsed becomes a narrow on-screen strip, not hidden */
        section[data-testid="stSidebar"][aria-expanded="false"] {
            width: 4.5rem !important;
            min-width: 4.5rem !important;
            transform: none !important;
            visibility: visible !important;
            transition: width .18s ease;
        }
        /* centre each icon and drop the row padding meant for the 300px drawer */
        section[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNavLink"] {
            justify-content: center;
            padding-left: 0.25rem;
            padding-right: 0.25rem;
        }
        /* hide the page-name labels in the rail (icons only) */
        section[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNavLink"] span[label] {
            display: none;
        }
        /* the category eyebrows have no room in the rail */
        section[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stNavSectionHeader"] {
            display: none;
        }
        /* tighten the nav's own gutters so a 4.5rem rail isn't cramped */
        section[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNav"],
        section[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarUserContent"] {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        /* SINGLE in-menu toggle. The sidebar's own collapse button
           (stSidebarCollapseButton) is a true toggle — when actually clickable
           it expands while collapsed and collapses while expanded — and it
           lives INSIDE the menu, so it is the one control we keep. Force it
           always-visible in the rail (Streamlit otherwise only reveals it on
           hover) and centre it at the top of the icon column. */
        section[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarCollapseButton"] {
            visibility: visible !important;
        }
        section[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarHeader"] {
            justify-content: center;
        }
        /* Remove the top-bar menu logic entirely: Streamlit's toolbar expand
           button is gone, so the in-menu toggle above is the only way to open. */
        [data-testid="stExpandSidebarButton"] {
            display: none !important;
        }
        /* Morph the toggle glyph: a hamburger (menu) when closed, an X (close)
           when open. The two glyphs sit on ::before/::after of the button's icon
           span and cross-fade + quarter-rotate when aria-expanded flips, so the
           swap reads as a morph; the native chevron glyph is hidden underneath. */
        [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"] {
            visibility: hidden;
            position: relative;
        }
        [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]::before,
        [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]::after {
            visibility: visible;
            position: absolute;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: opacity .2s ease, transform .2s ease;
        }
        [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]::before {
            content: "\\e5d2";  /* Material Symbols: menu (hamburger) */
        }
        [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]::after {
            content: "\\e5cd";  /* Material Symbols: close (X) */
        }
        section[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]::before {
            opacity: 1; transform: rotate(0);
        }
        section[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]::after {
            opacity: 0; transform: rotate(-90deg);
        }
        section[data-testid="stSidebar"][aria-expanded="true"] [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]::before {
            opacity: 0; transform: rotate(90deg);
        }
        section[data-testid="stSidebar"][aria-expanded="true"] [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]::after {
            opacity: 1; transform: rotate(0);
        }

        /* DRAWER — eyebrow styling + remove the collapsible-dropdown affordance.
           pointer-events:none makes the section header a static label, so a
           click can't collapse the group (the pages are never hidden); the
           chevron glyph is dropped so it reads as a kicker, not a toggle. */
        [data-testid="stNavSectionHeader"] {
            pointer-events: none;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-size: 0.72rem;
            opacity: 0.55;
        }
        [data-testid="stNavSectionHeader"] [data-testid="stIconMaterial"] {
            display: none;
        }
    }
    </style>
    """
)

page.run()

# Sticky Dashboard filter bar + scroll-condense header title. Runs GLOBALLY
# (in the entrypoint, on every page) — not in dashboard.py — because the header
# title is a child of the persistent top header, so something must run on the
# *other* pages too to hide it (else a stale "Dashboard" would linger after you
# scroll the hub then navigate away). Done in JS (not a CSS scroll-timeline) so
# it works in Safari/Firefox. In a 0-height same-origin iframe reaching the
# parent DOM. The iframe can be destroyed/recreated on navigation, so it must
# NOT gate re-binding on flags parked on persistent DOM — each run re-binds
# fresh in its own live context, tearing down the prior run's listener
# (stMain.__ovSync), ResizeObserver (stMain.__ovRO) and MutationObserver
# (window.parent.__ovMO) first. On non-Dashboard pages `.st-key-ov_bar` is
# absent, so sync() just hides the title and returns.
components.html(
    """
    <script>
    (function () {
      const W = window.parent;
      const doc = W.document;
      const STICK_TOP = 58;  /* matches the CSS sticky offset (top: 3.5rem) */
      function headerTitle() {
        let t = doc.querySelector('.ov-header-title');
        if (!t) {
          const header = doc.querySelector('[data-testid="stHeader"]');
          if (!header) return null;
          t = doc.createElement('div');
          t.className = 'ov-header-title';
          header.appendChild(t);
        }
        return t;
      }
      function sync() {
        const bar = doc.querySelector('.st-key-ov_bar');
        const main = doc.querySelector('[data-testid="stMain"]');
        const title = headerTitle();
        if (!bar || !main) {            /* not the Dashboard -> never show the title */
          if (title) title.classList.remove('ov-visible');
          return;
        }
        const stuck = bar.getBoundingClientRect().top <= STICK_TOP;
        bar.classList.toggle('ov-stuck', stuck);
        if (title) {
          /* clean page name from the active nav link's label (no icon glyph) */
          const active = doc.querySelector('[data-testid="stSidebarNavLink"][aria-current="page"] span[label]');
          const name = (active && (active.getAttribute('label') || active.textContent.trim())) || 'Dashboard';
          if (title.textContent !== name) title.textContent = name;
          /* align the title's left edge with the main column (= the stuck bar's
             full-bleed left). The header's own positioned origin is offset by
             the rail/drawer width, so subtract it. */
          const header = doc.querySelector('[data-testid="stHeader"]');
          const headerLeft = header ? header.getBoundingClientRect().left : 0;
          title.style.left = Math.round(main.getBoundingClientRect().left - headerLeft) + 'px';
          title.classList.toggle('ov-visible', stuck);
        }
        if (stuck) {
          /* span the main content column (NOT the viewport), so the bar never
             slides under an open sidebar; clientWidth excludes the scrollbar. */
          const wrap = bar.parentElement;
          const leftGutter = wrap.getBoundingClientRect().left - main.getBoundingClientRect().left;
          const w = main.clientWidth;
          bar.style.width = w + 'px';
          bar.style.maxWidth = w + 'px';
          bar.style.marginLeft = (-leftGutter) + 'px';
        } else {
          bar.style.width = '';
          bar.style.maxWidth = '';
          bar.style.marginLeft = '';
        }
      }
      function bind() {
        const sc = doc.querySelector('[data-testid="stMain"]');
        /* `__ovSync` holds the live sync fn of whichever iframe bound this node;
           a different value means a fresh iframe / new node -> (re)bind without
           stacking listeners. */
        if (sc && sc.__ovSync !== sync) {
          if (sc.__ovSync) sc.removeEventListener('scroll', sc.__ovSync);
          sc.addEventListener('scroll', sync, { passive: true });
          sc.__ovSync = sync;
          if (sc.__ovRO) { try { sc.__ovRO.disconnect(); } catch (e) {} }
          sc.__ovRO = new ResizeObserver(sync);  /* fires on sidebar open/close + resize */
          sc.__ovRO.observe(sc);
        }
        sync();
      }
      if (W.__ovMO) { try { W.__ovMO.disconnect(); } catch (e) {} }
      W.__ovMO = new MutationObserver(bind);
      W.__ovMO.observe(doc.documentElement, { childList: true, subtree: true });
      bind();
    })();
    </script>
    """,
    height=0,
)
