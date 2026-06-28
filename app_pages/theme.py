"""Theme & Design System — a hidden showcase of the live UI theme.

Not in the navigation rail (registered ``visibility="hidden"`` in ``app.py``);
reachable only by URL at ``/theme``. It documents the *actual* theme by reading
the real sources — the ``[theme]`` block of ``.streamlit/config.toml`` (via
``src.utils.theme``), the Okabe-Ito + Viridis palettes (``src.utils.palette``),
the CAQI bands (``src.utils.aqi``) and the metric registry — and by rendering the
real components, so it can never drift from what ships.

Styling rules are respected: colour swatches go through the **Plotly layer**
(``charts.palette_swatches``), not ad-hoc CSS; the typography and components on
show are the genuine widgets, themed by ``config.toml``. The page is built from
the same bordered ``box_*`` cards as the rest of the app, so it also demonstrates
the card surface itself.
"""

from __future__ import annotations

import math

import pandas as pd
import streamlit as st

from src.components import charts, skeleton
from src.components.kpi import aqi_tile, metric_tile
from src.components.meter import air_quality_meter
from src.utils.aqi import CAQI_BANDS, caqi_meter_zones, caqi_pm_thresholds
from src.utils.metrics import METRICS, get
from src.utils.palette import OKABE_ITO_NAMED
from src.utils.theme import theme_config

# Swatches are non-interactive (staticPlot); live demo charts keep the toolbar.
_SWATCH = {"theme": "streamlit", "width": "stretch",
           "config": {"displaylogo": False, "staticPlot": True}}
_PLOT = {"theme": "streamlit", "width": "stretch", "config": {"displaylogo": False}}

cfg = theme_config()
dark = cfg.get("dark", {})

st.title(":material/palette: Theme & Design System")
st.caption(
    "A living reference of this app's theme — colours, type scale and components. "
    "Hidden page (not in the menu), reachable at /theme. Everything below is read "
    "live from the config and the palette / registry modules, so it mirrors what ships."
)

# Active theme + base font, surfaced as badges (st.context.theme is best-effort).
try:
    _mode = st.context.theme.type  # "light" | "dark"
except Exception:  # noqa: BLE001 — older runtimes / headless: just omit it
    _mode = None
_badges = []
if _mode:
    _badges.append(f":gray-badge[Active theme: {_mode}]")
_badges.append(f":gray-badge[Font: {cfg.get('font', '—')}]")
_badges.append(f":gray-badge[Base size: {cfg.get('baseFontSize', '—')} px]")
st.markdown(" ".join(_badges))


def _tokens(src: dict) -> list[tuple[str, str]]:
    """The six base colour tokens of a theme block, as (hex, label) swatches."""
    keys = [
        ("primaryColor", "primary"),
        ("backgroundColor", "background"),
        ("secondaryBackgroundColor", "secondary bg"),
        ("textColor", "text"),
        ("linkColor", "link"),
        ("borderColor", "border"),
    ]
    return [(src[k], lbl) for k, lbl in keys if src.get(k)]


# === Base theme tokens (light + dark) ========================================
with st.container(border=True, key="box_theme_base"):
    st.markdown(
        "**:material/contrast: Base theme tokens**",
        help="From [theme] and [theme.dark] in .streamlit/config.toml. Only these six "
             "are overridden in dark mode; the palettes below are shared by both themes.",
    )
    st.caption("Light")
    st.plotly_chart(charts.palette_swatches(_tokens(cfg), ncols=6), key="sw_base_l", **_SWATCH)
    st.caption("Dark")
    st.plotly_chart(charts.palette_swatches(_tokens(dark), ncols=6), key="sw_base_d", **_SWATCH)

# === Categorical palette (Okabe-Ito) =========================================
with st.container(border=True, key="box_theme_categorical"):
    st.markdown(
        "**:material/category: Categorical palette — Okabe-Ito**",
        help="Colour-blind-safe categorical palette (src/utils/palette.py). Used for "
             "chart series, map groups and route colours — always paired with a label, "
             "shape or legend, never colour alone.",
    )
    okabe = [(hexv, name.replace("_", " ")) for name, hexv in OKABE_ITO_NAMED.items()]
    st.plotly_chart(charts.palette_swatches(okabe, ncols=3), key="sw_okabe", **_SWATCH)
    cat = cfg.get("chartCategoricalColors") or []
    if cat:
        st.caption(
            "Streamlit chart colorway (config.toml `chartCategoricalColors`) — the same "
            "hues, minus black, kept in sync with the palette module:"
        )
        st.plotly_chart(
            charts.palette_swatches([(c, f"#{i + 1}") for i, c in enumerate(cat)], ncols=7),
            key="sw_cat", **_SWATCH,
        )

# === Sequential palette (Viridis) ============================================
with st.container(border=True, key="box_theme_sequential"):
    st.markdown(
        "**:material/gradient: Sequential palette — Viridis**",
        help="Perceptually-uniform sequential scale (config.toml `chartSequentialColors`). "
             "Used for continuous colour: PM along routes, time-coloured scatter, the "
             "correlation heatmap colourbar.",
    )
    seq = cfg.get("chartSequentialColors") or []
    if seq:
        st.plotly_chart(
            charts.palette_swatches([(c, f"{i}") for i, c in enumerate(seq)], ncols=5),
            key="sw_seq", **_SWATCH,
        )

# === Semantic colours — CAQI air-quality bands ===============================
with st.container(border=True, key="box_theme_status"):
    st.markdown(
        "**:material/speed: Semantic colours — CAQI bands**",
        help="The computed EU-CAQI band colours (src/utils/aqi.py). Triple-encoded: "
             "icon + word + colour, so the band reads without relying on hue.",
    )
    bands = [(b.color, f"{b.label} / {b.quality}") for b in CAQI_BANDS]
    st.plotly_chart(charts.palette_swatches(bands, ncols=5), key="sw_caqi", **_SWATCH)

    st.caption("Air-quality meter (red→green gradient + position + zone words):")
    air_quality_meter(0.72, CAQI_BANDS[0].color, zone_labels=caqi_meter_zones())

    def _hi(v: float) -> str:
        return "—" if math.isinf(v) else f"{v:g}"

    band_rows = [
        {
            "Band": b.label, "Quality word": b.quality, "Colour": b.color,
            "PM2.5 ≤ (µg/m³)": _hi(b.pm2_5_hi), "PM10 ≤ (µg/m³)": _hi(b.pm10_hi),
        }
        for b in CAQI_BANDS
    ]
    st.dataframe(pd.DataFrame(band_rows), hide_index=True, width="stretch")

# === Metric registry colours =================================================
with st.container(border=True, key="box_theme_metrics"):
    st.markdown(
        "**:material/insights: Metric registry colours**",
        help="Every chart series/marker uses its metric's stable registry colour "
             "(metric.color in src/utils/metrics.py), so a measure looks the same everywhere.",
    )
    metric_items = [(m.color, m.short_label) for m in METRICS.values()]
    st.plotly_chart(charts.palette_swatches(metric_items, ncols=4), key="sw_metrics", **_SWATCH)

# === Typography ==============================================================
with st.container(border=True, key="box_theme_type"):
    st.markdown(
        "**:material/title: Typography**",
        help=f"Base font {cfg.get('font', '—')}; baseFontSize {cfg.get('baseFontSize', '—')} px; "
             f"heading weights {cfg.get('headingFontWeights', '—')}.",
    )
    st.title("Title — st.title (h1)")
    st.header("Header — st.header (h2)")
    st.subheader("Subheader — st.subheader (h3)")
    st.markdown("**Card title** — bold markdown, the box-header idiom used across the app")
    st.markdown(
        "Body — st.markdown. The quick brown fox jumps over the lazy dog. "
        "Glyphs in use: µg/m³ · °C · ↑ ↓ · Gdańsk"
    )
    st.caption("Caption — st.caption (muted; reserved for honesty disclosures)")
    st.code("value = metric.format(reading)  # st.code — monospace", language="python")
    st.markdown("**Badges**")
    st.markdown(
        ":gray-badge[gray] :blue-badge[blue] :green-badge[green] "
        ":orange-badge[orange] :red-badge[red] :violet-badge[violet] :primary-badge[primary]"
    )

# === Components ==============================================================
with st.container(border=True, key="box_theme_kpi"):
    st.markdown("**:material/dashboard: KPI tiles & metrics**")
    k = st.columns(4)
    with k[0]:
        metric_tile("pm2_5", 12.3, -1.4, value_desc="demo value")
    with k[1]:
        metric_tile("temp1", 21.6, 0.5, value_desc="demo value")
    with k[2]:
        metric_tile("inn_hum", 48, None, value_desc="demo value")
    with k[3]:
        aqi_tile(CAQI_BANDS[0])

with st.container(border=True, key="box_theme_controls"):
    st.markdown("**:material/smart_button: Controls**")
    b = st.columns(3)
    b[0].button("Primary", type="primary", width="stretch", key="th_btn_p")
    b[1].button("Secondary", width="stretch", key="th_btn_s")
    b[2].button("Disabled", disabled=True, width="stretch", key="th_btn_d")
    st.segmented_control("Segmented control", options=["One", "Two", "Three"],
                         default="One", key="th_seg")
    cc = st.columns(2)
    cc[0].selectbox("Selectbox", options=["Option A", "Option B", "Option C"], key="th_sel")
    cc[1].slider("Slider", 0, 100, 50, key="th_slider")
    st.toggle("Toggle", value=True, key="th_toggle")

with st.container(border=True, key="box_theme_skeleton"):
    st.markdown(
        "**:material/pending: Skeleton loaders**",
        help="Content-shaped placeholders shown while data loads; theme-safe shimmer.",
    )
    skeleton.hero()
    skeleton.tiles(4)
    skeleton.block(110)

with st.container(border=True, key="box_theme_chart"):
    st.markdown(
        "**:material/show_chart: Charts in the theme**",
        help="A demo line chart on synthetic data: spline lines in the metric registry "
             "colours, the fade-to-axis area gradient, and CAQI band guides "
             "(PM2.5 dotted / PM10 dashed, labelled — colour is never the only channel).",
    )
    _n = 60
    _ts = pd.date_range("2025-06-01", periods=_n, freq="h")
    demo = pd.DataFrame({
        "ts": _ts,
        "pm2_5": [16 + 9 * math.sin(i / 5) + (i % 4) for i in range(_n)],
        "pm10_0": [28 + 13 * math.sin(i / 5 + 1.0) + (i % 6) for i in range(_n)],
    })
    _guides = (
        [{"y": v, "label": f"PM2.5 · {bnd}", "color": get("pm2_5").color, "dash": "dot"}
         for v, bnd in caqi_pm_thresholds("pm2_5")]
        + [{"y": v, "label": f"PM10 · {bnd}", "color": get("pm10_0").color, "dash": "dash"}
           for v, bnd in caqi_pm_thresholds("pm10_0")]
    )
    st.plotly_chart(
        charts.line_chart(demo, ("pm2_5", "pm10_0"), height=300, band_guides=_guides),
        key="th_linechart", **_PLOT,
    )
