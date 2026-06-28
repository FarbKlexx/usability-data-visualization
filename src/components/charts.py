"""Plotly chart builders shared across pages.

Every figure here encodes the course's usability theory directly:

* **Consistency** — colors come from the metric registry, so PM2.5 is the
  same orange in every chart.
* **Split-attention** — legends and units live *on* the chart; tooltips
  carry value + unit + timestamp, never a separate table.
* **Direct manipulation** — plotly's drag-to-zoom and click-legend are
  left enabled; series toggle by clicking the legend.
* **Honesty** — concentration axes start at 0 (no truncation); units are
  always labelled; nothing is dual-axised onto a misleading second scale.
* **Color is never alone** — series are labelled in the legend; map
  markers carry a text + legend band, not just a hue.

These builders return ``plotly.graph_objects.Figure``; pages render them
with ``st.plotly_chart(fig, theme="streamlit")``.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.utils.metrics import METRICS, Metric, get, label_with_unit
from src.utils.palette import OKABE_ITO

_AXIS_FROM_ZERO = {"pm2_5", "pm10_0", "co2", "inn_hum", "caqi"}  # concentrations/counts
_TRANSPARENT = "rgba(0,0,0,0)"

# Line aesthetics (purely cosmetic; kept gentle so the curve doesn't lie about
# the data). `_SPLINE` is plotly's spline tension: 0 == linear, 1.3 == max — a
# low value rounds the joints without inventing peaks. `_FILL_ALPHA` is the
# peak opacity of the area gradient that fades to transparent toward the axis.
_SPLINE = 0.5
_FILL_ALPHA = 0.26


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """``"#E69F00"`` -> ``"rgba(230,159,0,0.26)"`` for translucent fills."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _area_gradient(hex_color: str) -> dict:
    """Vertical fill that is the line's colour at the top, transparent at 0."""
    return dict(
        type="vertical",
        colorscale=[[0.0, _hex_to_rgba(hex_color, 0.0)], [1.0, _hex_to_rgba(hex_color, _FILL_ALPHA)]],
    )


def _hovertemplate(metric: Metric) -> str:
    return f"%{{x|%Y-%m-%d %H:%M}}<br>{metric.label}: %{{y:.{metric.decimals}f}} {metric.unit}<extra></extra>"


def _empty(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, font=dict(size=14))
    fig.update_layout(
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        margin=dict(l=8, r=8, t=8, b=8), height=240,
    )
    return fig


def line_chart(
    df: pd.DataFrame,
    metric_keys: list[str] | tuple[str, ...],
    *,
    height: int = 380,
    smooth: pd.DataFrame | None = None,
    thresholds: dict[str, float] | None = None,
    annotations: list[dict] | None = None,
    band_guides: list[dict] | None = None,
) -> go.Figure:
    """Multi-series time line. Click a legend entry to toggle a series.

    All series share one honest Y axis only when they share a unit; if
    units differ the caller should prefer :func:`small_multiples` instead
    (no misleading dual axes).

    Optional interactivity overlays (plan §A2/§A4/§B4):

    * ``smooth`` — a frame aligned on ``ts`` carrying rolling-average
      columns (same metric keys); drawn as a thicker dashed overlay so the
      raw series stays visible underneath (honest: the smoothing is shown,
      not substituted).
    * ``thresholds`` — ``{metric_key: value}`` reference lines; points at
      or above the line are emphasised with markers (color is not the only
      channel — there is a labelled line + markers).
    * ``annotations`` — ``[{"ts_from", "ts_to", "label"}]`` shaded spans /
      vertical markers for saved notes.
    * ``band_guides`` — ``[{"y", "label", "color", "dash"}]`` faint reference
      lines (e.g. CAQI air-quality bands), drawn *under* the series. Filtered to
      the visible range so a high band never stretches the axis; labels are
      collision-avoided so they stay readable. Colour + dash + the label carry
      the meaning (e.g. dotted PM2.5 vs dashed PM10), never colour alone.
    """
    present = [k for k in metric_keys if k in df.columns and df[k].notna().any()]
    if df.empty or not present:
        return _empty("No data in the selected range.")

    fig = go.Figure()

    # Annotation bands first, so series draw on top of the shading.
    for ann in annotations or []:
        _add_annotation_shape(fig, ann)

    for key in present:
        metric = get(key)
        trace = dict(
            x=df["ts"], y=df[key], name=f"{metric.label}",
            mode="lines",
            line=dict(color=metric.color, width=2, shape="spline", smoothing=_SPLINE),
            hovertemplate=_hovertemplate(metric),
            connectgaps=True,  # bridge missing/sentinel points with a line (the
            # hidden-reading count is still disclosed via the caption's hidden_notice)
        )
        # Soft area gradient fading to transparent toward the axis — only for
        # zero-based measures, where filling down to 0 is meaningful (it would
        # be nonsense for temperature/pressure whose 0 is off-scale).
        if key in _AXIS_FROM_ZERO:
            trace["fill"] = "tozeroy"
            trace["fillgradient"] = _area_gradient(metric.color)
        fig.add_trace(go.Scatter(**trace))
        # Rolling-average overlay (plan §A2): dashed, same hue, on top.
        if smooth is not None and key in smooth.columns and smooth[key].notna().any():
            fig.add_trace(
                go.Scatter(
                    x=smooth["ts"], y=smooth[key], name=f"{metric.label} (avg)",
                    mode="lines", line=dict(color=metric.color, width=2.6, dash="dash"),
                    hovertemplate=_hovertemplate(metric), connectgaps=True,
                )
            )
        # Threshold line + emphasised exceedances (plan §A4).
        thr = (thresholds or {}).get(key)
        if thr is not None:
            fig.add_hline(
                y=thr, line=dict(color=metric.color, width=1.4, dash="dot"),
                annotation_text=f"{metric.short_label} ≥ {thr:g} {metric.unit}",
                annotation_position="top left", annotation_font_size=11,
            )
            over = df[df[key] >= thr]
            if not over.empty:
                fig.add_trace(
                    go.Scatter(
                        x=over["ts"], y=over[key], name=f"{metric.label} ≥ threshold",
                        mode="markers",
                        marker=dict(color=metric.color, size=7, symbol="circle-open", line=dict(width=2)),
                        hovertemplate=_hovertemplate(metric), showlegend=False,
                    )
                )

    # Air-quality band guides (e.g. CAQI). Each guide is a dict
    # {"y", "label", "color", "dash"}: faint coloured lines under the series,
    # range-filtered so a far band never stretches the axis, with collision-
    # avoided labels. Colour + dash + the label's pollutant prefix distinguish
    # e.g. PM2.5 from PM10 (never colour alone — colour-blind-safe).
    if band_guides:
        present_max = max(
            (float(df[k].max()) for k in present if df[k].notna().any()), default=None
        )
        if present_max is not None:
            shown = [g for g in band_guides if g["y"] <= present_max]
            # The nearest band above current levels, per colour (pollutant) group,
            # so each series still shows its next threshold — unless it is so far
            # above the data that drawing it would squash the series.
            nearest_above: dict[str, dict] = {}
            for g in sorted(band_guides, key=lambda d: d["y"]):
                if g["y"] > present_max:
                    nearest_above.setdefault(g["color"], g)
            for g in nearest_above.values():
                if present_max >= 0.4 * g["y"]:
                    shown.append(g)
            # Label only when far enough from the previous label to stay readable;
            # unlabelled lines still draw (colour + dash carry the meaning).
            sep = present_max * 0.05
            last_label_y = float("-inf")
            for g in sorted(shown, key=lambda d: d["y"]):
                show_label = (g["y"] - last_label_y) >= sep
                fig.add_hline(
                    y=g["y"], layer="below",
                    line=dict(color=_hex_to_rgba(g["color"], 0.38), width=1, dash=g.get("dash", "dot")),
                    annotation_text=(g["label"] if show_label else None),
                    annotation_position="top right",
                    annotation_font=dict(size=10, color=_hex_to_rgba(g["color"], 0.95)),
                )
                if show_label:
                    last_label_y = g["y"]

    units = {get(k).unit for k in present}
    y_title = next(iter(units)) if len(units) == 1 else "value"
    starts_zero = all(k in _AXIS_FROM_ZERO for k in present)
    fig.update_layout(
        height=height, margin=dict(l=8, r=8, t=8, b=8),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis_title=None, yaxis_title=y_title,
    )
    fig.update_yaxes(rangemode="tozero" if starts_zero else "normal")
    return fig


def _add_annotation_shape(fig: go.Figure, ann: dict) -> None:
    """Draw one annotation as a shaded span (range) or vline (point)."""
    ts_from = ann.get("ts_from")
    ts_to = ann.get("ts_to")
    label = str(ann.get("label", "")) or "note"
    band = "rgba(120,120,120,0.13)"
    if ts_to is not None and pd.notna(ts_to) and ts_to != ts_from:
        fig.add_vrect(
            x0=ts_from, x1=ts_to, fillcolor=band, line_width=0, layer="below",
            annotation_text=label, annotation_position="top left",
            annotation_font_size=11,
        )
    else:
        fig.add_vline(
            x=ts_from, line=dict(color="rgba(90,90,90,0.6)", width=1.2, dash="dot"),
            annotation_text=label, annotation_position="top",
            annotation_font_size=11,
        )


def small_multiples(df: pd.DataFrame, metric_keys: list[str] | tuple[str, ...], *, row_height: int = 150) -> go.Figure:
    """One stacked panel per metric, shared X axis.

    Used for climate measures whose units differ (°C / % / hPa): each
    gets its own honest Y scale instead of being forced onto a deceptive
    dual axis (CONTEXT ethics, plan §3 candidate 3).
    """
    present = [k for k in metric_keys if k in df.columns and df[k].notna().any()]
    if df.empty or not present:
        return _empty("No data in the selected range.")

    fig = make_subplots(
        rows=len(present), cols=1, shared_xaxes=True, vertical_spacing=0.06,
        subplot_titles=[label_with_unit(k) for k in present],
    )
    for i, key in enumerate(present, start=1):
        metric = get(key)
        sm = dict(
            x=df["ts"], y=df[key], name=metric.label, mode="lines",
            line=dict(color=metric.color, width=1.8, shape="spline", smoothing=_SPLINE),
            showlegend=False, hovertemplate=_hovertemplate(metric), connectgaps=True,
        )
        if key in _AXIS_FROM_ZERO:
            sm["fill"] = "tozeroy"
            sm["fillgradient"] = _area_gradient(metric.color)
        fig.add_trace(go.Scatter(**sm), row=i, col=1)
        if key in _AXIS_FROM_ZERO:
            fig.update_yaxes(rangemode="tozero", row=i, col=1)
    fig.update_layout(
        height=row_height * len(present), margin=dict(l=8, r=8, t=24, b=8),
        hovermode="x unified",
    )
    fig.update_annotations(font_size=13)
    return fig


def grouped_bar(stats: pd.DataFrame, metric_key: str, label_map: dict[str, str], *, height: int = 360) -> go.Figure:
    """Average-per-sensor bars with on-bar value labels (color not alone)."""
    metric = get(metric_key)
    if stats.empty:
        return _empty("No data for these sensors / range.")
    s = stats.sort_values("avg", ascending=False)
    labels = [label_map.get(t, t) for t in s["table_name"]]
    fig = go.Figure(
        go.Bar(
            x=labels, y=s["avg"], marker_color=metric.color,
            text=[metric.format(v) for v in s["avg"]], textposition="outside",
            hovertemplate=f"%{{x}}<br>avg {metric.label}: %{{y:.{metric.decimals}f}} {metric.unit}<extra></extra>",
        )
    )
    fig.update_layout(
        height=height, margin=dict(l=8, r=8, t=24, b=8),
        yaxis_title=label_with_unit(metric_key),
    )
    fig.update_yaxes(rangemode="tozero")
    return fig


def box_from_stats(stats: pd.DataFrame, metric_key: str, label_map: dict[str, str], *, height: int = 360) -> go.Figure:
    """Distribution box plot from precomputed quartiles (honest spread)."""
    metric = get(metric_key)
    if stats.empty:
        return _empty("No data for these sensors / range.")
    fig = go.Figure()
    for _, r in stats.iterrows():
        fig.add_trace(
            go.Box(
                name=label_map.get(r["table_name"], r["table_name"]),
                q1=[r["q1"]], median=[r["median"]], q3=[r["q3"]],
                lowerfence=[r["min"]], upperfence=[r["max"]], mean=[r["avg"]],
                marker_color=metric.color, boxpoints=False,
            )
        )
    fig.update_layout(
        height=height, margin=dict(l=8, r=8, t=24, b=8), showlegend=False,
        yaxis_title=label_with_unit(metric_key),
    )
    return fig


def map_figure(
    markers: pd.DataFrame | None = None,
    tracks: list[dict] | None = None,
    *,
    height: int = 520,
    show_text: bool = True,
) -> go.Figure:
    """MapLibre map: location markers (grouped by legend) + mobile tracks.

    Args:
        markers: rows with ``lat, lon, label, group, color`` (one trace
            per ``group`` so the legend doubles as a key — color is never
            the sole channel).
        tracks: list of ``{"label", "lat", "lon", "color"}`` polylines.
    Token-free OpenStreetMap tiles.
    """
    fig = go.Figure()
    lats: list[float] = []
    lons: list[float] = []

    if tracks:
        for tr in tracks:
            if not len(tr["lat"]):
                continue
            lats += list(tr["lat"]); lons += list(tr["lon"])
            fig.add_trace(
                go.Scattermap(
                    lat=tr["lat"], lon=tr["lon"], mode="lines",
                    line=dict(width=3, color=tr["color"]), name=tr["label"],
                    hoverinfo="name",
                )
            )

    if markers is not None and not markers.empty:
        for group, grp in markers.groupby("group", sort=False):
            lats += list(grp["lat"]); lons += list(grp["lon"])
            color = grp["color"].iloc[0]
            fig.add_trace(
                go.Scattermap(
                    lat=grp["lat"], lon=grp["lon"],
                    mode="markers+text" if show_text else "markers",
                    marker=dict(size=13, color=color),
                    text=grp["label"] if show_text else None,
                    textposition="top right", textfont=dict(size=11),
                    name=str(group),
                    customdata=grp[["label"]].to_numpy(),
                    hovertemplate="%{customdata[0]}<extra>" + str(group) + "</extra>",
                )
            )

    if lats:
        center = dict(lat=sum(lats) / len(lats), lon=sum(lons) / len(lons))
        span = max(max(lats) - min(lats), max(lons) - min(lons), 0.01)
        zoom = 4 if span > 5 else 6 if span > 1 else 9 if span > 0.1 else 12
    else:
        center, zoom = dict(lat=52.3, lon=8.9), 5

    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=0, b=0),
        map=dict(style="open-street-map", center=center, zoom=zoom),
        legend=dict(orientation="h", yanchor="top", y=0.99, xanchor="left", x=0.01,
                    bgcolor="rgba(255,255,255,0.8)"),
    )
    return fig


_TYPE_COLOR = {
    "Stationary": OKABE_ITO[5],   # blue
    "Mobile": OKABE_ITO[6],       # vermillion
    "POI": OKABE_ITO[7],          # reddish purple
    "External": OKABE_ITO[1],     # orange
    "Specialty": OKABE_ITO[3],    # bluish green
}


def build_location_markers(loc: pd.DataFrame, band_lookup: dict | None = None) -> pd.DataFrame:
    """Shape a locations frame into ``map_figure`` marker rows.

    When ``band_lookup`` (table_name -> CAQIBand) is given, located
    sensors with a live reading are grouped/colored by their CAQI band
    (legend = key); everything else falls back to its device type. Either
    way the legend label carries the meaning, so color is never alone.
    """
    rows = []
    for _, r in loc.iterrows():
        band = (band_lookup or {}).get(r.get("table_name"))
        if band is not None:
            group, color = f"AQI: {band.label}", band.color
        else:
            group = str(r["ootype"])
            color = _TYPE_COLOR.get(group, OKABE_ITO[0])
        rows.append(
            {"lat": r["lat"], "lon": r["lon"], "label": r["name"], "group": group, "color": color}
        )
    return pd.DataFrame(rows)


def _convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Convex hull of 2-D points (Andrew's monotone chain; scipy-free).

    Returns the hull vertices in order (counter-clockwise), or the points
    themselves if there are fewer than three distinct ones.
    """
    pts = sorted(set(points))
    if len(pts) < 3:
        return pts

    def cross(o: tuple, a: tuple, b: tuple) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list[tuple[float, float]] = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper: list[tuple[float, float]] = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def route_hulls(routes: pd.DataFrame) -> dict[int, dict]:
    """Per-trip convex-hull ring + centroid + label, keyed by ``route_id``.

    ``{rid: {"lat": [...], "lon": [...], "clat", "clon", "text"}}``. The
    Dashboard injects this into its hover watcher so a *single* reusable polygon
    + label trace can be repointed to the hovered trip — far lighter than one
    trace per trip. Trips with fewer than three distinct points are skipped.
    """
    out: dict[int, dict] = {}
    for i, rid in enumerate(dict.fromkeys(routes["route_id"])):
        seg = routes[routes["route_id"] == rid]
        hull = _convex_hull(list(zip(seg["lon"], seg["lat"], strict=False)))
        if len(hull) < 3:
            continue
        out[int(rid)] = {
            "lat": [p[1] for p in hull] + [hull[0][1]],
            "lon": [p[0] for p in hull] + [hull[0][0]],
            "clat": sum(p[1] for p in hull) / len(hull),
            "clon": sum(p[0] for p in hull) / len(hull),
            "text": f"Route {i + 1} · {len(seg)} pts",
        }
    return out


def route_map(
    routes: pd.DataFrame,
    *,
    height: int = 560,
    selected_route: int | None = None,
    color_metric: str = "pm2_5",
    clickable: bool = False,
    show_points: bool = True,
) -> go.Figure:
    """Mobile routes on a map (adaptive plan §B2).

    Two complementary, separately-labelled channels (color is never the
    only carrier):

    * **Trip identity** — each ``route_id`` is its own line. With few
      routes (≤ 8) each gets a distinct categorical colour + a "Route N"
      legend entry; with many, lines are drawn in neutral grey (a legend
      of 28 trips would defeat Hick's law) and the *selected* route is
      highlighted. Either way each trip is a separate path.
    * **Pollution along the path** — the points are coloured by PM value
      on the sequential **Viridis** scale with a colourbar legend and a
      value tooltip, so the air-quality payoff of a mobile sensor reads
      at a glance.

    ``routes`` is the frame from :func:`src.data.load_routes`
    (``ts, lon, lat, pm2_5, route_id``). ``selected_route`` highlights one
    trip and scopes the PM points to it.
    """
    if routes is None or routes.empty:
        return _empty("No routes in the selected range.")

    metric = get(color_metric) if color_metric in METRICS else None
    route_ids = list(dict.fromkeys(routes["route_id"]))
    legend = len(route_ids) <= 8  # distinct colours + legend only when few
    fig = go.Figure()
    lats: list[float] = []
    lons: list[float] = []

    # Hover overlay added FIRST so it sits *under* the route lines: a tinted hull
    # on top would intercept the click (it's hoverinfo="skip") and the line below
    # would never receive it. The Dashboard's watcher repoints this `activehull`
    # to the hovered trip; it's empty until then.
    if clickable:
        fig.add_trace(go.Scattermap(
            lat=[], lon=[], mode="lines", fill="toself",
            fillcolor="rgba(213, 94, 0, 0)", line=dict(width=0),
            hoverinfo="skip", showlegend=False, visible=True, name="activehull", meta="activehull",
        ))

    # One trace per trip (each its own path) — needed for distinct per-route
    # colours. On the dashboard every trip gets a cycling palette colour (not grey)
    # so adjacent trips are distinguishable even when there are many; the legend is
    # only shown for ≤8 (a 28-trip legend would defeat Hick). Each trip's line
    # carries route_id as 2-column customdata (last field) so a click/hover resolves
    # the trip — and because there is one trace per trip, the trace index is also
    # the route_id.
    for i, rid in enumerate(route_ids):
        seg = routes[routes["route_id"] == rid]
        lats += list(seg["lat"]); lons += list(seg["lon"])
        is_sel = selected_route == rid
        dim = selected_route is not None and not is_sel
        if show_points:
            color = OKABE_ITO[6] if is_sel else (track_palette(i) if legend else "#8A8F98")
        else:
            color = OKABE_ITO[6] if is_sel else track_palette(i)  # always distinct
        trace_kwargs: dict = dict(
            lat=seg["lat"], lon=seg["lon"],
            line=dict(width=3 if is_sel else 1.6, color=color),
            opacity=0.25 if dim else 0.9,
            name=f"Route {i + 1}", showlegend=legend,
        )
        if show_points:
            trace_kwargs.update(mode="lines", hoverinfo="name")
        else:
            # Thick line + same-colour markers of the same size sitting *on* the
            # line, so it still reads as one continuous route (no separate dots) —
            # but the markers are what makes it clickable: Streamlit's plotly
            # selection only fires for marker/point clicks, never line clicks.
            trace_kwargs["line"] = dict(width=4 if is_sel else 3, color=color)
            trace_kwargs.update(
                mode="lines+markers", marker=dict(size=4, color=color),
                customdata=[[int(rid), int(rid)]] * len(seg), hoverinfo="none",
            )
        fig.add_trace(go.Scattermap(**trace_kwargs))

    pts = routes if selected_route is None else routes[routes["route_id"] == selected_route]
    if show_points and metric is not None and color_metric in pts.columns and pts[color_metric].notna().any():
        fig.add_trace(
            go.Scattermap(
                lat=pts["lat"], lon=pts["lon"], mode="markers",
                marker=dict(
                    size=7, color=pts[color_metric], colorscale="Viridis", showscale=True,
                    colorbar=dict(title=f"{metric.short_label}<br>{metric.unit}"),
                ),
                # customdata[-1] = route_id, so a click on the map can resolve
                # which trip the point belongs to (the Dashboard navigates on it).
                customdata=pts[[color_metric, "route_id"]].to_numpy(),
                hovertemplate=(
                    f"{metric.label}: %{{customdata[0]:.{metric.decimals}f}} {metric.unit}"
                    + ("<br><i>Click to open this trip →</i>" if clickable else "")
                    + "<extra></extra>"
                ),
                name=metric.label, showlegend=False,
            )
        )

    if lats:
        center = dict(lat=sum(lats) / len(lats), lon=sum(lons) / len(lons))
        span = max(max(lats) - min(lats), max(lons) - min(lons), 0.005)
        zoom = 5 if span > 3 else 7 if span > 0.5 else 10 if span > 0.05 else 13
    else:
        center, zoom = dict(lat=52.3, lon=8.9), 6

    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=0, b=0),
        map=dict(style="open-street-map", center=center, zoom=zoom),
        legend=dict(orientation="h", yanchor="top", y=0.99, xanchor="left", x=0.01,
                    bgcolor="rgba(255,255,255,0.8)"),
    )
    return fig


def particle_size_bars(df: pd.DataFrame, *, height: int = 340) -> go.Figure:
    """Particle-size distribution as grouped bars (plan §3 candidate 8).

    Mass and number concentrations use different units, so each gets its
    own panel/axis (no misleading shared scale). ``df`` is the long frame
    from ``load_particle_sizes`` (kind / size_class / value).
    """
    if df.empty:
        return _empty("No particle-size data in the selected range.")
    kinds = list(dict.fromkeys(df["kind"]))
    fig = make_subplots(rows=1, cols=len(kinds), subplot_titles=kinds, horizontal_spacing=0.12)
    color = {"Mass (µg/m³)": OKABE_ITO[1], "Number (#/cm³)": OKABE_ITO[5]}
    for i, kind in enumerate(kinds, start=1):
        sub = df[df["kind"] == kind]
        dec = 2 if "Mass" in kind else 1
        fig.add_trace(
            go.Bar(
                x=sub["size_class"], y=sub["value"], marker_color=color.get(kind, OKABE_ITO[3]),
                text=[f"{v:.{dec}f}" for v in sub["value"]], textposition="outside",
                showlegend=False,
                hovertemplate="%{x}: %{y:." + str(dec) + "f}<extra>" + kind + "</extra>",
            ),
            row=1, col=i,
        )
        fig.update_yaxes(rangemode="tozero", row=1, col=i)
    fig.update_layout(height=height, margin=dict(l=8, r=8, t=28, b=8))
    fig.update_annotations(font_size=13)
    return fig


def coverage_timeline(df: pd.DataFrame, *, height: int = 420) -> go.Figure:
    """Data-availability Gantt: when each sensor has measurements.

    Expects columns ``label, first_ts, last_ts, n_rows``. Honest about
    gaps — a sensor with no data simply has no bar (plan §3 candidate 9).
    """
    data = df.dropna(subset=["first_ts", "last_ts"]).copy()
    if data.empty:
        return _empty("No sensor has measurements.")
    data = data.sort_values("first_ts")
    fig = px.timeline(
        data, x_start="first_ts", x_end="last_ts", y="label",
        color_discrete_sequence=[OKABE_ITO[5]],
        custom_data=["n_rows"],
    )
    fig.update_traces(
        hovertemplate="%{y}<br>%{x|%Y-%m-%d} → %{customdata[0]:,} rows<extra></extra>",
        marker_line_width=0,
    )
    fig.update_yaxes(autorange="reversed", title=None)
    fig.update_xaxes(title=None)
    fig.update_layout(height=height, margin=dict(l=8, r=8, t=8, b=8))
    return fig


# --- Multi-measure / correlation graph (correlation plan §B) ----------------


def normalized_overlay(
    df: pd.DataFrame,
    metric_keys: list[str] | tuple[str, ...],
    ranges: dict[str, tuple[float, float]] | None = None,
    *,
    height: int = 420,
) -> go.Figure:
    """Overlaid min–max-scaled lines for *shape* comparison (plan §B1).

    Every selected measure is drawn on one 0–1 axis so the user can see
    whether peaks and troughs line up in time despite wildly different
    units. ``df`` is the *scaled* frame from
    :func:`src.utils.correlate.normalize_frame`; ``ranges`` (its companion
    ``{key: (min, max)}``) lets the hover show each point's real value, so
    the absolute scale stays recoverable (honesty — normalization is
    disclosed, never hidden).
    """
    present = [k for k in metric_keys if k in df.columns and df[k].notna().any()]
    if df.empty or not present:
        return _empty("No paired data in the selected range.")

    fig = go.Figure()
    for key in present:
        metric = get(key)
        lo, hi = (ranges or {}).get(key, (None, None))
        # Recover the real value for the tooltip from the normalized one.
        if lo is not None and hi is not None and hi > lo:
            real = df[key] * (hi - lo) + lo
        else:
            real = df[key]
        hover = (
            f"%{{x|%Y-%m-%d %H:%M}}<br>{metric.label}: "
            f"%{{customdata:.{metric.decimals}f}} {metric.unit} "
            f"(norm %{{y:.2f}})<extra></extra>"
        )
        fig.add_trace(
            go.Scatter(
                x=df["ts"], y=df[key], name=metric.label, mode="lines",
                line=dict(color=metric.color, width=2, shape="spline", smoothing=_SPLINE),
                connectgaps=True, customdata=real, hovertemplate=hover,
            )
        )
    fig.update_layout(
        height=height, margin=dict(l=8, r=8, t=8, b=8), hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis_title=None, yaxis_title="normalized (0–1)",
    )
    fig.update_yaxes(range=[-0.02, 1.02])
    return fig


def scatter_correlation(
    frame: pd.DataFrame,
    x_key: str,
    y_key: str,
    *,
    slope: float | None = None,
    intercept: float | None = None,
    color_by_time: bool = True,
    height: int = 460,
) -> go.Figure:
    """Scatter of measure A (X) vs B (Y) — the relationship itself (§B3).

    One marker per aligned sample, optionally colored by time so within-
    period drift is visible, with an optional least-squares trend line
    (pass ``slope``/``intercept`` from
    :func:`src.utils.correlate.compute_correlation`).
    """
    mx, my = get(x_key), get(y_key)
    if frame.empty or x_key not in frame.columns or y_key not in frame.columns:
        return _empty("No paired samples in the selected range.")
    pts = frame[[c for c in ("ts", x_key, y_key) if c in frame.columns]].dropna(
        subset=[x_key, y_key]
    )
    if pts.empty:
        return _empty("No paired samples in the selected range.")

    fig = go.Figure()
    marker = dict(size=6, color=mx.color, opacity=0.6)
    hover = (
        f"{mx.label}: %{{x:.{mx.decimals}f}} {mx.unit}<br>"
        f"{my.label}: %{{y:.{my.decimals}f}} {my.unit}<extra></extra>"
    )
    if color_by_time and "ts" in pts.columns:
        t = pd.to_datetime(pts["ts"])
        tnum = (t - t.min()).dt.total_seconds()
        marker = dict(
            size=6, color=tnum, colorscale="Viridis", opacity=0.75,
            colorbar=dict(
                title="time", tickmode="array",
                tickvals=[float(tnum.min()), float(tnum.max())],
                ticktext=[f"{t.min():%Y-%m-%d}", f"{t.max():%Y-%m-%d}"],
            ),
        )
        hover = (
            f"%{{customdata|%Y-%m-%d %H:%M}}<br>{mx.label}: %{{x:.{mx.decimals}f}} {mx.unit}"
            f"<br>{my.label}: %{{y:.{my.decimals}f}} {my.unit}<extra></extra>"
        )
    fig.add_trace(
        go.Scatter(
            x=pts[x_key], y=pts[y_key], mode="markers", name="samples",
            marker=marker, customdata=pts["ts"] if "ts" in pts.columns else None,
            hovertemplate=hover,
        )
    )
    if slope is not None and intercept is not None:
        xs = [float(pts[x_key].min()), float(pts[x_key].max())]
        ys = [slope * xv + intercept for xv in xs]
        fig.add_trace(
            go.Scatter(
                x=xs, y=ys, mode="lines", name="least-squares fit",
                line=dict(color=OKABE_ITO[0], width=2, dash="dash"),
                hovertemplate="fit<extra></extra>",
            )
        )
    fig.update_layout(
        height=height, margin=dict(l=8, r=8, t=8, b=8),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis_title=label_with_unit(x_key), yaxis_title=label_with_unit(y_key),
    )
    if x_key in _AXIS_FROM_ZERO:
        fig.update_xaxes(rangemode="tozero")
    if y_key in _AXIS_FROM_ZERO:
        fig.update_yaxes(rangemode="tozero")
    return fig


def correlation_heatmap(matrix: pd.DataFrame | None, *, height: int | None = None) -> go.Figure:
    """Pairwise-correlation heatmap for 3+ measures (plan §B3).

    Viridis scale fixed to ``[-1, 1]`` with the ``r`` value printed in
    every cell, so the coefficient is legible as text and not conveyed by
    color alone. ``matrix`` is the frame from
    :func:`src.utils.correlate.compute_correlation`.
    """
    if matrix is None or matrix.empty:
        return _empty("Not enough paired data for a correlation matrix.")
    labels = [get(k).short_label if k in METRICS else str(k) for k in matrix.columns]
    z = matrix.to_numpy(dtype=float)
    text = [[("–" if pd.isna(v) else f"{v:.2f}") for v in row] for row in z]
    fig = go.Figure(
        go.Heatmap(
            z=z, x=labels, y=labels, zmin=-1.0, zmax=1.0, colorscale="Viridis",
            colorbar=dict(title="r"), text=text, texttemplate="%{text}",
            hovertemplate="%{y} vs %{x}: r = %{z:.2f}<extra></extra>",
        )
    )
    n = len(labels)
    fig.update_layout(
        height=height or (110 + 56 * n), margin=dict(l=8, r=8, t=8, b=8),
        yaxis=dict(autorange="reversed"),
    )
    return fig


def track_palette(i: int) -> str:
    """Stable, colorblind-safe color for the i-th mobile track."""
    # skip index 0 (black) and yellow (low contrast on map) for line colors
    picks = (OKABE_ITO[6], OKABE_ITO[5], OKABE_ITO[3], OKABE_ITO[7], OKABE_ITO[1], OKABE_ITO[2])
    return picks[i % len(picks)]
