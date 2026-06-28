"""Error & Empty States — a hidden gallery of the app's feedback messages.

Not in the navigation rail (registered ``visibility="hidden"`` in ``app.py``);
reachable only by URL at ``/states``. It reproduces every
``st.error`` / ``st.warning`` / ``st.info`` / ``st.success`` the app shows — with
the exact text + icon as at the live call site (cited under each block) — so each
can be screenshotted for the usability report without recreating the triggering
condition. A few also occur naturally: deselect every sensor (filter-bar warning)
or pick an empty time range (the "no … in range" infos).

Companion to the hidden Theme page (``/theme``). Pure presentation — no DB, no
writes; the strings mirror the call sites and are kept in step by hand.
"""

from __future__ import annotations

import streamlit as st

st.title(":material/report: Error & Empty States")
st.caption(
    "A hidden gallery (reachable at /states) of the app's feedback messages, "
    "reproduced verbatim for documentation screenshots. The label under each "
    "message says where it appears in the app."
)

# === The four generic feedback styles =======================================
with st.container(border=True, key="box_states_styles"):
    st.markdown(
        "**:material/notifications: The four feedback styles**",
        help="Streamlit's alert variants, used across the app so every action and "
             "every empty state gets a visible response (Shneiderman #3: feedback).",
    )
    st.success("Success — an action completed.", icon=":material/check_circle:")
    st.info("Info — a neutral hint or empty-state explanation.", icon=":material/info:")
    st.warning("Warning — needs attention but isn't fatal.", icon=":material/warning:")
    st.error("Error — an action failed or a precondition is missing.", icon=":material/error:")

# === Empty / no-data states =================================================
with st.container(border=True, key="box_states_empty"):
    st.markdown("**:material/search_off: Empty & no-data states**")

    st.warning("Select at least one sensor to see data.", icon=":material/info:")
    st.caption(":material/place: Filter bar — no sensor selected · `src/components/filter_bar.py`")

    st.info(
        "No routes in the selected range — widen the time range (Reset, or try All).",
        icon=":material/info:",
    )
    st.caption(":material/place: Dashboard bento — mobile device, no trips in range · `app_pages/dashboard.py`")

    st.info("No routes in the selected range — widen the time range above.", icon=":material/info:")
    st.caption(":material/place: Dashboard Routes list — same condition, list section · `app_pages/dashboard.py`")

    st.info("Pick at least two measures to see whether they relate.", icon=":material/info:")
    st.caption(":material/place: Correlation — fewer than two measures chosen · `app_pages/correlation.py`")

    st.warning(
        "Not enough paired readings in this range to compare these measures.",
        icon=":material/info:",
    )
    st.caption(":material/place: Correlation — too few overlapping readings · `app_pages/correlation.py`")

# === Route-detail link states ===============================================
with st.container(border=True, key="box_states_route"):
    st.markdown("**:material/route: Route-detail link states**")

    st.info(
        "Open a trip from the Dashboard's **Routes** list to see its details.",
        icon=":material/info:",
    )
    st.caption(":material/place: Route detail — opened with no trip selected · `app_pages/route.py`")

    st.error("This route link is incomplete or malformed.", icon=":material/error:")
    st.caption(":material/place: Route detail — bad / garbled URL params · `app_pages/route.py`")

    st.warning(
        "That trip is no longer in the selected range (the time window or split gap may have changed).",
        icon=":material/info:",
    )
    st.caption(":material/place: Route detail — stale link after the window/gap changed · `app_pages/route.py`")

# === Settings states ========================================================
with st.container(border=True, key="box_states_settings"):
    st.markdown("**:material/tune: Settings states**")

    st.warning(
        "The dashboard tables are not present yet. Run "
        "`uv run python scripts/add_dashboard_tables.py` to enable thresholds "
        "and saved views.",
        icon=":material/info:",
    )
    st.caption(":material/place: Settings — `dashboard_*` tables not migrated · `app_pages/settings.py`")

    st.info("Run the migration to enable saved thresholds.", icon=":material/info:")
    st.caption(":material/place: Settings — thresholds section when not migrated · `app_pages/settings.py`")

    st.success("Threshold saved.", icon=":material/check_circle:")
    st.caption(":material/place: Settings — after a successful save · `app_pages/settings.py`")

    st.error(
        'Could not save: duplicate key value violates unique constraint '
        '"dashboard_thresholds_pkey"',
        icon=":material/error:",
    )
    st.caption(
        ":material/place: Settings — a write that raised; the text after "
        "“Could not save:” is the live exception · `app_pages/settings.py`"
    )

# === Database unreachable (full-page block) =================================
with st.container(border=True, key="box_states_db"):
    st.markdown(
        "**:material/database_off: Database unreachable — full-page block**",
        help="Shown by app.py before any page runs if the cached DB health check "
             "fails; the app then st.stop()s, so in reality this replaces the whole page.",
    )
    st.error(
        "**The dashboard can't reach its database.**\n\n"
        "This app reads an air-quality PostgreSQL + PostGIS database. "
        "On Streamlit Community Cloud, set a `DATABASE_URL` secret pointing "
        "at a hosted Postgres+PostGIS instance (see `DEPLOY.md`). Locally, "
        "start the bundled container with `docker compose up -d`.",
        icon=":material/database_off:",
    )
    with st.expander("Technical detail"):
        st.code(
            "(psycopg.OperationalError) connection failed: connection to server at "
            '"localhost" (127.0.0.1), port 5432 failed: Connection refused\n'
            "\tIs the server running on that host and accepting TCP/IP connections?"
        )
    st.caption(":material/place: app.py — DB health check failed; the real block is followed by `st.stop()`")
