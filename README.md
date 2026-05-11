# Air Quality Usability Dashboard

A Streamlit dashboard built for the Usability course. The design
principles that drive every decision — Visual Perception, Gestalt,
Cognitive Load, Shneiderman, Accessibility — live in
[CONTEXT.md](CONTEXT.md). Read it before adding features.

## Quickstart

Requires [uv](https://docs.astral.sh/uv/) and Python ≥ 3.12.

```bash
uv sync                       # install dependencies
uv run streamlit run app.py   # start the dev server
```

The app opens at <http://localhost:8501>.

## Tests

```bash
uv run pytest
```

## Project layout

| Path              | Purpose                                              |
| ----------------- | ---------------------------------------------------- |
| `app.py`          | Entry point — registers pages via `st.navigation`.   |
| `app_pages/`      | One module per page; UI only, no data wrangling.     |
| `src/components/` | Reusable UI primitives (KPI tile, filter bar, …).    |
| `src/data/`       | Cached loaders for Postgres dump / CSV / Parquet.    |
| `src/utils/`      | Palettes, formatters, accessibility helpers.         |
| `assets/`         | Static files (logos, sample data, images).           |
| `tests/`          | Pytest suite — start with import smoke tests.        |
| `.streamlit/`     | Theme + runtime config (never customize via CSS).    |

## Status

Foundation only — no features yet.
