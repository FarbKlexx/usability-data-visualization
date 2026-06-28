# Prompt Logbook

A running record of every prompt given to Claude Code on this project.
Each entry captures the **Title** (a short label), the **concrete
Prompt** (verbatim), and a **Summary of changes** (what was actually
done in response).

Newest entries are appended at the bottom.

---

## 1. Set up a prompt logbook

**Prompt:**

> I want you to write every single prompt i give you into a prompt
> logbook markdownfile displaying the following information: Title,
> concrete Prompt, summary of changes. add this to the CLAUDE.md and
> add the logbook to the docs folder

**Summary of changes:**

- Created this file, [`docs/prompt_logbook.md`](prompt_logbook.md), with
  a documented format (Title / concrete Prompt / Summary of changes) and
  seeded it with this first entry.
- Added a **Prompt logbook** section to
  [`CLAUDE.md`](../CLAUDE.md) instructing Claude Code to append every
  future user prompt here as a new entry.

---

## 2. Neuordnung des Dashboards nach Usability-Prinzipien (IA-Vorschlag)

**Prompt:**

> # Agent-Prompt: Neuordnung eines Dashboards nach Usability-Prinzipien
>
> **Rolle:** Erfahrener Product-/UX-Architekt (Informationsarchitektur,
> Dashboard-Design). Aufgabe ist *nicht*, Funktionen zu erfinden oder zu
> entfernen, sondern die bestehende Funktionalität neu zu strukturieren,
> sodass das Dashboard übersichtlicher, konsistenter und intuitiver wird.
>
> **Verbindliche Grundlage:** Zuerst `CONTEXT.md` vollständig lesen; die
> dortigen Usability-Prinzipien sind die alleinige Quelle der Wahrheit.
> Keine eigenen Prinzipien erfinden; jede Strukturentscheidung namentlich
> auf ein CONTEXT.md-Prinzip zurückführen; Mehrdeutigkeiten/Lücken explizit
> benennen statt still anzunehmen.
>
> **Ausgangsproblem:** Informationen/Funktionen sind „all over the place"
> verstreut — Zusammengehöriges liegt weit auseinander, Ähnliches ist
> unterschiedlich gelöst, der Nutzer muss zu viel suchen.
>
> **Aufgabe:** Bestehende Struktur analysieren und neue Anordnung entwerfen —
> Gruppierung, Übersichtlichkeit, Redundanz, Auffindbarkeit.
>
> **Harte Leitplanken:** Kein Auslagern als Standardlösung (muss echtes
> Dashboard bleiben; Unterseite nur bei selten/sekundär/zu umfangreich, je
> begründet); keine Funktion geht verloren (Konsolidieren erlaubt, ersatzlos
> streichen nur bei reiner Redundanz); jede Entscheidung begründet.
>
> **Vorgehen/Output:** (1) Analyse der Ist-Situation (Inventar + Probleme
> mit Prinzipienbezug), (2) Neue Informationsarchitektur (Gruppierung als
> grobes Text-Wireframe), (3) Entscheidungslog (Was/Warum/welches Problem),
> (4) Begründung der Verteilung (Dashboard vs. Unterseiten), (5) Offene
> Fragen/Annahmen. Rückfragen stellen, falls wesentliche Infos zur
> aktuellen Struktur fehlen.

**Summary of changes:**

- Kein App-Code geändert — reiner Analyse-/Design-Liefergegenstand (spiegelt
  das Stage-1-„nur vorschlagen"-Muster der vorigen Konsolidierungsrunde).
- `CONTEXT.md`, alle 6 Seiten (`app_pages/*.py`), `app.py` und
  `src/components/filter_bar.py` sowie die vorhandenen Konsolidierungs-Docs
  (`consolidation_audit.md`, `implementation_plan_consolidation.md`) gelesen,
  um auf der **bereits erfolgten** ersten Konsolidierung (7 → 6 Seiten)
  aufzusetzen statt sie zu wiederholen.
- Neues Dokument [`docs/ia_redesign_proposal.md`](ia_redesign_proposal.md)
  erstellt: IA-relevante Rubrik (K1–K10), Inventar, Problemkatalog (P1–P10,
  je verletztes Prinzip), neue IA in 4 Maßnahmen (A Nav-Gruppierung &
  Umbenennung „Manage"→„Settings"; B eine Edit-/Konfig-Regel; C Doppelungen
  auflösen / KPI-Reihe in den Primärbereich; D konsistentes Scoping & ein
  Saved-view-System), Text-Wireframes (Dashboard + Settings), Entscheidungslog
  (D1–D9), Verteilungs-Begründung gegen die „kein Auslagern"-Leitplanke,
  Annahmen + benannte CONTEXT.md-Lücken (Nav-Taxonomie, Edit-im-Kontext) +
  Rückfragen.

---

## 3. Dashboard-Hub Redesign (3-Zonen-Hub, KPI-Reihe über dem Fold, Seitenreduktion)

**Prompt:**

> (Sub-Agent-Auftrag, Designer-Rolle) Produziere EIN vollständiges Redesign
> in der Philosophie PROGRESSIVE 3-ZONE HUB: Zone 1 Hero-Antwort (Status +
> Geräte-Identität), Zone 2 At-a-glance KPIs + Karte + Trend in einem
> Mehrspalten-Grid (alles über dem Fold), Zone 3 Deep-Dive-Tabs. Moderate
> Seitenreduktion, starke konventionelle Dashboard-Hierarchie, sehr intuitiv
> für Laien. Anforderungen: (1) volle Seitenliste entscheiden (Löschen/Mergen
> erlaubt; Admin kollabiert auf Thresholds). (2) explizites, baubares
> Streamlit-Wireframe das alle vier C-Beschwerden behebt (KPIs über dem Fold,
> unverwechselbare aktive Geräte-Identität, Karte neben einem Element mit
> sinnvollem Seitenverhältnis, klare visuelle Hierarchie). (3) Prosa durch
> Tooltips/help/Icons ersetzen. (4) jede Entscheidung an CONTEXT.md-Prinzipien
> namentlich und an Research-Exemplaren begründen.

**Summary of changes:**

- Kein App-Code geändert — reiner Design-/Strukturvorschlag (strukturiertes
  Designer-Output an die Orchestrierung; Stage-1-Muster).
- `CONTEXT.md`, `docs/ia_redesign_proposal.md`, `app.py`, `app_pages/dashboard.py`
  und `app_pages/manage.py` sowie `src/components/filter_bar.py`,
  `src/components/kpi.py` und die `charts.py`-Höhensignaturen gelesen, um das
  Redesign auf reale Funktionssignaturen und die bestehende Problemanalyse
  (P1–P10, C1–C4) zu stützen.
- Vollständiges 3-Zonen-Hub-Redesign als strukturierte Antwort geliefert:
  Seitenliste (Manage→Settings nur Thresholds; Comparison als Dashboard-Tab
  „Compare"; Nav in zwei benannte Cluster), explizites ASCII-Streamlit-Wireframe
  mit `st.columns`-Gewichten, Container-Bordern und Chart-Höhen in px, das alle
  vier C-Defekte behebt; Tooltip-/help-Strategie statt Prosa; Risiken.

---

## 3. Dashboard re-layout + page consolidation (IA redesign, Stage 2)

**Prompt:**

> **zu A:** du darfst seiten löschen, wenn es sinnvoll ist und du die
> funktionen auf andere seiten packen kannst. es geht hierbei darum dem
> nutzer kognitive entscheidungen abzunehmen, und im einfach alle funktionen
> und was er machen kann ohne fließtext lesen zu müssen zu vermitteln. Dabei
> will ich vollkommen auf intuitive Elemente setzen als auf lange
> erklärungen, diese können in tooltips oder hover info boxen ausgelargert
> werden können. die admin settings des systems können komplett reduziert
> werden auf die thresholds
>
> **C:** bei dem dashboard geht es vor allem um eine umordnung der
> angezeigten elemente. Beispiele: KPI boxen sind erst nach scrollen
> einsehbar, es ist nicht wirklich ersichtlich welches Gerät grade
> angeschaut wird. die map ist sehr breit aber nicht sehr hoch (verhältnis
> ergibt keinen sinn, karte brauch auch keine eigene reihe, könnte neben
> einem anderen element stehen). elemente haben alle ähnliche größen ohne
> sich voneinander vernünftig abzugrenzen. orientiere dich dabei an den
> usability prinzipien aber auch an bereits erfolgreichen guten beispielen
> für dashboards

**Summary of changes:**

- Ran a multi-agent research+design **Workflow** (researched best-in-class
  air-quality/analytics dashboards, generated 3 redesigns, judged them
  against CONTEXT.md + the four C-defects, synthesized one buildable spec).
  Winner: a *monitoring-cockpit* layout with grafted page-reduction.
- **`app_pages/dashboard.py`** rewritten: Zone 1 **hero card** (the only
  `st.subheader`, *names the active device* via `device_label(drow)` +
  CAQI verdict + dominant-PM `metric_tile`) — fixes "unclear which device"
  (C2); Zone 2 **6-tile KPI strip** lifted out of the old *Measures & data*
  tab into `st.container(horizontal=True)`, rendered before any chart —
  fixes "KPIs only after scrolling" (C1); Zone 3 **`st.columns([2,1])`
  bento** — PM trend (or route map) beside a near-square location map /
  trip-stats card at matched `height=320`/`420` — fixes the wide-short
  full-width map (C3); one `st.divider` + a 3-tier size/weight ladder with
  Gestalt border cards — fixes uniform-size flatness (C4). The full
  multi-measure charter + per-device CSV were **cut** (live on Time Series,
  reached via an "Open in Time Series" hand-off); ov_measures dropped from
  URL state.
- **Page reduction:** `app_pages/comparison.py` → `render_compare()` mounted
  in a Dashboard **Compare** tab (`st.stop()`→`return`); removed from the
  top nav. **`app.py`** now uses a **grouped `st.navigation({...})` dict**
  (Monitor & Analyse / Reference & Settings) — 6→5 destinations.
- **Admin → thresholds:** `git mv manage.py settings.py`; cut the 3
  feature-flag toggles + the "other flags" expander (modules default on →
  nothing lost); kept the thresholds editor (+ a page_link to Time Series),
  demoted saved-views into an expander.
- **`app_pages/timeseries.py`:** the 3 optional modules render
  unconditionally (dropped `feature_enabled`); added a Settings page_link by
  the thresholds expander; zoom hint → tooltip.
- **`app_pages/map.py`:** replaced the duplicate 6-tile KPI block with a
  single CAQI tile + unified "Open in Time Series" hand-off.
- **`app_pages/devices.py`:** known-issues prose bullets → per-item
  expanders (audit table/timeline/catalog stay visible).
- **`src/components/filter_bar.py`:** namespaced the Reset button key
  (`{prefix}_reset`) so the hub + Compare-tab toolbars can coexist on one
  page (fixed a `StreamlitDuplicateElementId`).
- **`CLAUDE.md`** updated (pages table, navigation, feature-flag notes).
- **Verified** by running the app against the live DB and screenshotting at
  1280×720: 6 KPIs above the fold, device name in the hero, map beside the
  chart, grouped nav, and every page (Dashboard stationary+mobile, Settings,
  Map, Time Series, Devices) loads without exceptions.

---

## 4. Move navigation into a left burger menu

**Prompt:**

> put the whole navigation into a burger menu navigation, from the left

**Summary of changes:**

- **`app.py`**: switched `st.navigation(PAGES, position="top")` →
  `position="sidebar"`, and set `initial_sidebar_state="collapsed"` in
  `st.set_page_config` so the nav lives in a **left burger menu** —
  collapsed by default (the `»` control top-left opens it, `«` closes it).
  The two grouped sections (*Monitor & Analyse* / *Reference & Settings*)
  carry over into the sidebar unchanged.
- Collapsing the top nav frees a row, so even more of the Dashboard
  (hero + KPI strip + start of the bento) now sits above the fold.
- **`CLAUDE.md`**: updated the Navigation section to describe the
  sidebar/collapsed burger menu.
- Verified by screenshot: collapsed state shows the burger control and no
  top bar; expanded state shows the two-section grouped nav in the left rail.

---

## 5. Hamburger (☰) icon for the burger menu

**Prompt:**

> Use a burger menu icon for the menu from the google icon api

**Summary of changes:**

- The sidebar's expand control defaulted to a `»` chevron
  (`stIconMaterial` ligature `keyboard_double_arrow_right`). Replaced its
  glyph with the **Material Symbols `menu` hamburger (☰)** — the Google
  Material icon API — codepoint `\e5d2`.
- **`app.py`**: added a single, scoped `st.html(<style>)` that targets
  `[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"]`,
  hides the original glyph and overlays `content:"\e5d2"` via `::after`.
  Only the glyph changes — colour/size inherit from the theme, so dark
  mode stays intact.
- This is the **one deliberate exception** to the project's no-CSS rule
  (Streamlit exposes no config hook for the sidebar toggle icon).
  Documented as such in **CLAUDE.md** (Theming section).
- Verified by screenshot in **both light and dark mode**: the ☰ renders
  top-left in the theme-appropriate colour; the rest of the theme is
  unaffected.

---

## 6. Sticky, morphing filter bar on the Dashboard

**Prompt:**

> i want this first bar on the dashboard to be like it is but when you
> scroll past it it should become sticky and morph as a top bar

**Summary of changes:**

- The Dashboard's filter bar now stays a full bordered card at rest and,
  once you scroll past it, **sticks just below the header and condenses
  into a slim top bar** (reduced padding, squared top corners, drop
  shadow). Pure CSS, no JS.
- **`src/components/filter_bar.py`**: gave the toolbar container a
  `key=f"{prefix}_bar"` so it gets a stable `.st-key-{prefix}_bar` class
  (only the Dashboard's `ov` instance is styled).
- **`app.py`** (extending the existing chrome `st.html` block):
  - sticky is applied to the bar's `stLayoutWrapper` via
    `:has(> .st-key-ov_bar)` — the bar's own wrapper is exactly its height
    so it had no room to stick; its parent (the main vertical block) is
    tall, so the wrapper sticks correctly. `top: 3.5rem` clears Streamlit's
    56px fixed header (which sits at `z-index: 999990`).
  - the morph is a scroll-driven `@keyframes` (`animation-timeline:
    scroll(nearest)`, range `20px 150px`); the opaque background uses CSS
    `light-dark()` (Streamlit exposes no theme CSS var, and the bar is
    otherwise transparent → would bleed when stuck).
- **Investigated the live DOM first** (scroll container = `stMain`,
  `color-scheme` on `.stApp` → `light-dark()` resolves, `:has()` +
  scroll-timeline supported, the wrapper-height sticky trap, the 56px
  header offset) so the implementation rests on stable hooks.
- **Verified by screenshot** at rest and scrolled, in **light and dark**:
  pins at ~53px below the header, condenses (padding 14→6px) with a shadow,
  background stays theme-correct (white light / dark dark), content scrolls
  under it.
- **CLAUDE.md** Theming exception note updated to cover this second use.

---

## 7. Sticky filter bar goes full-width

**Prompt:**

> when becoming sticky, the bar should also become full width, and back to
> its original size when unsticking

**Summary of changes:**

- **`app.py`** (the `ov-bar-condense` scroll-driven keyframes): when the
  Dashboard filter bar sticks, it now **expands to the full viewport width**
  (edge-to-edge top bar) and reverts to its original contained card when
  scrolled back up.
- Implementation: animate `width: 100%` → `width: 100vw` plus
  `margin-left: calc(50% - 50vw)`; also lift `max-width` to `100vw` in the
  morph — the bar carries Streamlit's `max-width: 100%`, which was clamping
  `100vw` back to the content width (1130px). Diagnosed via DOM inspection
  (the bar is a `flex:1 1 0%` item with `max-width:100%`, so neither
  negative margins nor `width` alone expanded it). Retimed the range to
  `115px 175px` so the morph fires as the bar reaches the top.
- Because the morph is scroll-driven, the reversal ("back to original size
  when unsticking") is automatic.
- **Verified** by measuring `getBoundingClientRect` at rest vs. stuck:
  contained `left 75 → right 1205` (1130px, radius 8px) becomes
  `left 0 → right 1280` (full 1280px, radius 0) in light **and** dark, with
  no horizontal scrollbar (`.stApp` clips at the viewport).
- **CLAUDE.md** Theming-exception note updated.

---

## 8. Fix: sticky bar was *always* full width (Safari/Firefox)

**Prompt:**

> for me its always full width, not just when sticky

**Summary of changes:**

- **Root cause:** the morph used a CSS scroll-driven animation
  (`animation-timeline: scroll()`), which only Chromium supports. In
  Safari/Firefox the timeline is ignored, so `animation: … both` ran on
  the default 0-duration timeline and immediately filled to its *end*
  state — leaving the bar permanently morphed (full-width). My earlier
  "degrades gracefully" claim was wrong.
- **Fix — switched to a browser-agnostic approach:**
  - **`app.py`**: replaced the `@keyframes`/`animation-timeline` block with
    a plain `.st-key-ov_bar` (contained) + `.st-key-ov_bar.ov-stuck`
    (full-width/condensed) pair and a CSS `transition`. CSS transitions are
    universally supported.
  - **`app_pages/dashboard.py`**: added a 0-height `components.html` iframe
    running a tiny scroll-watcher that toggles `.ov-stuck` on the bar once
    its top reaches the sticky offset (~58px), re-binding across Streamlit
    reruns with a `MutationObserver` (reaches the parent DOM via
    `window.parent`, same-origin srcdoc).
- Now the bar is **contained at rest** and only goes full-width/sticky when
  scrolled past — in every browser. Safe fallback: if the JS doesn't run,
  the bar is simply a contained sticky bar (never "always full width").
- **Verified** in Chromium (logic is browser-agnostic; it no longer depends
  on scroll-timeline): REST → `stuck:false, width 1130, left 75`; SCROLLED
  → `stuck:true, width 1280, left 0`; BACK TO TOP → contained again.
- **CLAUDE.md** Theming-exception note rewritten (CSS + the JS watcher;
  noted the full-bleed assumes a collapsed sidebar).

---

## 9. Fix: sticky bar slid under the open sidebar

**Prompt:**

> the bar doesnt behave correctly when the burger menu is open

**Summary of changes:**

- **Cause:** the full-bleed used viewport units (`width:100vw`,
  `margin-left: calc(50% - 50vw)`), which ignore the sidebar — so with the
  burger menu open the stuck bar spanned the whole window and slid under
  the sidebar.
- **Fix:** the full-bleed geometry is now computed from the **main content
  column** instead of the viewport.
  - **`app.py`**: `.ov-stuck` no longer sets width/margin — it keeps only
    the non-geometry morph (padding, squared corners, shadow, `light-dark()`
    background).
  - **`app_pages/dashboard.py`**: the scroll-watcher sets the bar's
    `width`/`max-width`/`margin-left` **inline** from `stMain`'s
    `clientWidth` and left offset, so the bar spans exactly the main column
    (right of the sidebar, left of the scrollbar). Added a `ResizeObserver`
    on `stMain` so it re-syncs while the sidebar opens/closes (and on window
    resize); cleared the inline styles when unstuck.
- **Verified** in both states: sidebar collapsed → bar `left 0 → 1280`
  (full viewport); sidebar open → bar `left 300 → 1280` (width 980), exactly
  matching `stMain` (`left 300`, `clientWidth 980`) — no longer under the
  sidebar. Screenshot confirms the bar starts at the sidebar's right edge.
- **CLAUDE.md** Theming-exception note updated (geometry from `stMain`,
  `ResizeObserver`; dropped the old "assumes collapsed sidebar" caveat).

---

## 10. KPI trend baseline follows the selected time range

**Prompt:**

> the "Latest reading 2025-11-19 15:53 · trend vs. previous 24 h" section
> should change depending on which time range is selected

**Summary of changes:**

- The KPI "trend" was always computed against the **previous 24 h**
  regardless of the range, so relabeling the caption alone would have lied.
  Made the baseline window actually follow the selected range (honest data).
- **`src/data/loaders.py`**: `load_latest` gained a `baseline_seconds`
  parameter (default `86400`). The trend delta = latest − mean over that
  window before the latest reading; `None` compares against **all** earlier
  readings (for the "All" range).
- **`src/components/kpi.py`**: `metric_tile` gained a `baseline_label`
  (default "previous 24 h") so the tile tooltip names the right comparison
  window.
- **`app_pages/dashboard.py`**: a `_BASELINE` map turns the active range
  into `(seconds, label)` — 24 h→86400, 7 d→604800, 30 d→2592000,
  All→`(None, "the full record")`. `load_latest` is called with that
  window; the caption reads "trend vs. {label}" and both the hero and strip
  tiles pass the label. Map (`load_latest(chosen)`) keeps the 24 h default.
- **Verified** per range: caption shows "previous 24 h / 7 d / 30 d / the
  full record", and the PM2.5 delta genuinely changes with the baseline
  (−3.7 / +2.4 / +2.9 / +2.1 µg/m³) — relabel *and* recompute, not just text.

---

## 11. KPI tile values follow the selected time range

**Prompt:**

> [PM2.5 / PM10 / CO₂ / Temp / Humidity / Air-quality tiles] these should
> also change based on the selected time range

**Summary of changes:**

- The KPI tiles showed the **latest reading**, which is fixed for this
  frozen dataset — so they never changed with the range. Switched the whole
  snapshot zone to the **mean over the selected range** (the only way the
  values can honestly track the range), with the trend measured
  period-over-period.
- **`src/data/loaders.py`**: new `load_range_summary(table, start, end)` —
  per-metric sentinel-cleaned mean over `[start, end)` plus a delta vs. the
  **previous equal-length window** `[start-(end-start), start)` (`None` when
  that window is empty, e.g. "All"); also returns the latest ts in range for
  currency. Exported from `src/data/__init__.py`. `load_latest` is kept (the
  Map page still shows a live snapshot).
- **`src/components/kpi.py`**: `metric_tile` gained `value_desc` ("latest
  reading" vs e.g. "7 d average") and drops the "trend vs." clause from the
  tooltip when there's no delta.
- **`app_pages/dashboard.py`**: the hero (verdict + dominant-PM number +
  CAQI), the strip tiles and the CAQI tile all use `load_range_summary`, so
  they're internally consistent (hero PM == strip PM). Captions now read
  "{range} average · trend vs. previous {range}" (or "Full-record average"
  for All); hero meta reads "… · {range} average · through {ts}". Removed the
  now-unused `_BASELINE`/`load_latest` wiring.
- **Verified** per range: PM2.5 value changes **10.9 → 4.9 → 4.4 → 5.2 µg/m³**
  (24 h / 7 d / 30 d / All); deltas are period-over-period. Confirmed the
  "24 h" no-delta case is honest — the 24–48 h-before window genuinely has 0
  rows (a data gap), so no trend arrow is shown.

## 12. Off-white page canvas + borderless white cards

**Prompt:**

> i want you to change the way the outline boxes behave. first of all use an
> offwhite color for the background of the page. then remove the stroke from
> boxes and color them full white.

**Summary of changes:**

- **Page canvas → off-white.** `.streamlit/config.toml`: light-theme
  `backgroundColor` `#FFFFFF → #F1F3F7`. Dark theme unchanged.
- **Boxes → solid white, no stroke.** Streamlit's bordered containers,
  `st.metric(border=True)` tiles and `st.form(border=True)` are *transparent
  with a 1px `borderColor` stroke* (verified in the 1.57 bundle —
  `...border&&{border:1px solid borderColor}`, no fill), and `config.toml`
  exposes **no** fill token for them. So the fill + stroke-removal go in the
  existing documented `st.html(<style>)` block in **`app.py`**: the boxes get
  `background-color: light-dark(#FFF, #1C2128)` (dark mode gets an elevated
  surface, not white), `border-color: transparent`, and a faint shadow so the
  now-strokeless cards stay legible on the canvas.
- **Robust, version-proof selectors** (not fragile emotion classes): the
  stable public `[data-testid="stMetric"]` / `[data-testid="stForm"]` hooks,
  plus the project's own `.st-key-*` convention. Added `key="box_*"` to the
  seven bordered `st.container()`s (`app_pages/dashboard.py` ×5,
  `app_pages/timeseries.py`, `src/components/kpi.py`'s `aqi_tile`) and
  matched `[class*="st-key-box_"]`; the filter bars (`*_bar`) are folded in
  too (`ov_bar` keeps its sticky background/scroll-shadow, just loses its
  stroke).
- **Verified** by running the app and screenshotting both themes: light =
  off-white canvas with solid-white borderless cards; dark = dark canvas with
  elevated `#1C2128` cards. No stroke on metric tiles, content cards or filter
  bars in either mode.

## 13. Fill the Streamlit top bar white too

**Prompt:**

> make the streamlit topbar also filled white

**Summary of changes:**

- **`app.py`**: added `[data-testid="stHeader"] { background-color:
  light-dark(#FFF, #1C2128); }` to the existing `st.html(<style>)` block.
  Streamlit's fixed top bar is transparent by default, so it was showing the
  off-white canvas through it; now it matches the cards (white in light, the
  elevated surface in dark). No config token exists for the header, so this
  belongs with the other chrome CSS.
- **Verified** via a fresh light-mode screenshot: the top bar (burger menu /
  Deploy / ⋮) is solid white, distinct from the off-white canvas below.

## 14. Type icons in the sensor dropdown

**Prompt:**

> inside the dropdown menu, the devices have different types. Use
> corresponding icons for the device types on the left side of the type
> inside the drop down

**Summary of changes:**

- **`src/components/filter_bar.py`**: in the grouped (`group_by_type`) sensor
  picker, each option now leads with a per-type glyph: 📍 Stationary, 🚗 Mobile,
  🔬 Specialty, 🌐 External, 📌 POI (`_TYPE_ICON` map + `_TYPE_ICON_FALLBACK`).
  Added a local `_fmt` `format_func` used by both the selectbox and the
  multiselect; the icon is applied **only in the picker display** — the
  active-filter chips and the returned `FilterState` keep the icon-free label,
  and the hero title is unaffected (it builds from `device_label`, not the
  picker label).
- **Why emoji, not Material icons:** verified by a scratch app + screenshot
  that `st.selectbox`/`multiselect` render their option labels as **plain
  text** — a `:material/…:` shortcode shows literally, whereas emoji render
  natively. (CLAUDE.md prefers Material icons, but they don't work in option
  labels.)
- **Verified** on the live dropdown: 📍/🚗/🔬/🌐 all render in front of their
  type (closed box too). POI has no readings so it's excluded from the picker
  pool (`has_data`) — its icon is defined for completeness only.

## 15. Data-loading skeletons across the Dashboard

**Prompt:**

> Add data loading skeletons to the entire page. So wherever data is loaded
> in it shows an abstract loading representation of the content as long as
> its loading

**Summary of changes:**

- **New `src/components/skeleton.py`**: a small set of content-shaped
  placeholder builders — `hero()`, `tiles(n)` (a horizontal strip of
  tile-shaped cards), `tiles_stack(n)`, `block(height)` (chart/map), and
  `lines(widths)` — each emitting class'd `.aq-skel*` markup. Rationale doc'd
  in the module: a content-shaped grey placeholder is perceived as faster than
  a spinner and tells the user *what/where* is loading (NN/g skeleton screens;
  Shneiderman #3 feedback), and the shapes mirror the real widgets so the
  layout doesn't jump when data arrives (no layout shift).
- **`app.py`**: added the skeleton CSS to the existing global `st.html(<style>)`
  block — a shimmer keyframe over a flat grey fill, `.aq-skel-row` (flex row
  for the strip/hero) and `.aq-skel-card` (matches the real card fill/radius/
  shadow). Theme-safe via `light-dark()`, with a `prefers-reduced-motion`
  guard that drops the animation. Documented as one more `st.html` exception
  (Streamlit ships no `st.skeleton` and the config exposes no token).
- **`app_pages/dashboard.py`**: every on-page data load now paints a skeleton
  in its slot first, then swaps the real content into the **same** `st.empty()`
  slot once the (cached) query returns. Covered: the hero card + KPI strip
  (share one `load_range_summary` query → both skeletoned before it runs), the
  bento PM-trend chart / location map (stationary) and route map / trip-stats
  (mobile) — both cells skeletoned before either query runs so the row reads
  as loading at once — and the Correlation tab's verdict + chart. Static chrome
  (box + title + hand-off button) renders immediately; only the data area waits.
- **`app_pages/comparison.py`** (the Dashboard's Compare tab): the
  averages/distribution charts + numbers table skeleton (`block(360)`) while
  `load_comparison` runs, then swap in.
- On a `@st.cache_data` hit the swap is instant, so a skeleton only actually
  shows when something is genuinely being fetched (first visit / TTL miss).
- The toolbar's own `load_devices()` keeps its existing cache spinner (the
  picker layout isn't known until devices load, so it can't be skeletoned);
  Time Series / Map / Devices pages were left as-is (this pass targets the
  Dashboard hub) — the `skeleton` component is reusable if we extend later.
- **Verified**: `uv run pytest` (21 passed, 7 DB-skipped) and a focused
  `AppTest` exercising the exact mechanics — `st.empty().container()` swap with
  keyed bordered containers, refilling a placeholder created inside a column
  from outside its context, the horizontal strip refill, and `st.html`
  skeleton markup — all render the real content as final state with no errors.
- **Live-verified** by running the app (`streamlit run app.py` against the
  local Postgres) and driving it with headless Chrome: the settled Dashboard
  renders correctly, and clicking the heavier **All** range catches the bento
  cells showing chart/map-shaped grey skeleton blocks under their (instantly
  rendered) titles before swapping to the real chart + map — no page errors.

## 16. Remove the emoji icons from the device dropdown

**Prompt:**

> remove the icons from the device dropdown again. No emoji icons

**Summary of changes:**

- **`src/components/filter_bar.py`**: reverted the per-type emoji glyphs added
  in entry #14. Removed the `_TYPE_ICON` map and `_TYPE_ICON_FALLBACK`, and
  simplified the picker `format_func` (`_fmt`) to return the plain label. The
  grouped picker still prefixes the **type word** (`Stationary · …`,
  `Mobile · …`) so the kinds stay visible but unmixed; only the leading emoji
  is gone. Chips and the returned `FilterState` were already icon-free and are
  unchanged.
- **Live-verified**: reloaded the running app and opened the Sensor dropdown
  with headless Chrome — options now read `Stationary · SENSORpi s01 · Minden`,
  `Mobile · …`, `Specialty · …`, `External · …` with no 📍/🚗/🔬/🌐 glyph, and
  no page errors.

## 17. Persistent left navigation rail (icons → labelled drawer)

**Prompt:**

> make the navigation on the left always there (on desktop). find corresponding
> google font api icons for the pages. make it such that the icons are always
> shown on the left (collapsed) and if you open the sidebar the names of the
> pages are also shown. make it such that the pages are not hidden in a dropdown
> put categorized via an eyebrow above

**Decision:** asked how the rail should expand; user chose **click a toggle**
(content pushes right when open), not hover.

**Summary of changes:**

- **`app.py`** — added a `@media (min-width:768px)` block to the global
  `st.html(<style>)` that turns Streamlit's hide-completely collapsed sidebar
  into an always-on **icon rail** and its expanded state into a **labelled
  drawer**, keyed on `section[data-testid="stSidebar"][aria-expanded]`:
  - Collapsed → `width:4.5rem !important` + `transform:none` (stays on-screen);
    page-name `span[label]`s hidden, icons centred, gutters tightened. The
    app's `display:flex` layout reflows the main column automatically.
  - Expanded → native 300px drawer with icons **+** page names.
  - The native ☰ (expand) / « (collapse) controls toggle `aria-expanded`, so
    they double as the rail↔drawer toggle — no extra widget/JS.
  - Category headers (`stNavSectionHeader`) restyled as **static eyebrows**
    (uppercase, muted) with the collapsible-dropdown chevron hidden and
    `pointer-events:none` so a click can't hide the pages.
  - Desktop only; on phones the rail CSS is inert and Streamlit's off-canvas
    burger is kept. `initial_sidebar_state` stays `collapsed` → rail-by-default.
- **Icons**: the per-page Material Symbols (Google Fonts) icons were already
  set on each `st.Page` and are the rail glyphs — `dashboard`, `timeline`,
  `map`, `sensors`, `tune`; reviewed each as the right fit and kept them.
- **`CLAUDE.md`** — rewrote the Navigation section for the rail/drawer model
  and added it as Theming exception 4, including the gotcha below.
- **Debugging note (cost a while)**: a stray `<` inside a CSS *comment*
  (`rail<->drawer`, `<section>`) made Streamlit's HTML sanitiser mis-parse the
  `<style>` and **silently drop the entire `st.html` block** (all card /
  skeleton / nav CSS vanished). Fixed by using unicode arrows in comments;
  documented the trap in CLAUDE.md. Isolation-tested with a minimal app to
  localise it.
- **Live-verified** with headless Chrome: rail = 67.5px with 5 icons centred
  (icon centre x=33.75 in a 67.5px rail); ☰ opens the 300px drawer showing
  names + the two uppercase eyebrows with no chevron; « collapses back; the
  rail persists across page navigation; clicking a rail icon navigates
  (`/map` confirmed). No page errors in any state.

## 18. Remove the burger-menu glyph

**Prompt:**

> remove the burger menu icon now

**Summary of changes:**

- **`app.py`** — removed the oldest Theming exception: the CSS that hid the
  sidebar expand control's default glyph and overlaid a Material Symbols `menu`
  hamburger (☰, `\e5d2`) via `::after`. The control now shows Streamlit's
  native `»` (`keyboard_double_arrow_right`) chevron, which reads correctly as
  "expand the rail to the right." The open toggle still works — only the glyph
  changed. Tidied the surrounding `st.html` intro comment and the
  `initial_sidebar_state` comment.
- **`CLAUDE.md`** — dropped exception 1 (burger glyph) from the Theming list
  and renumbered (sticky bar → 1, skeletons → 2, nav rail → 3); updated the
  Navigation section's `☰`→`»` references and the exception cross-link.
- **Live-verified**: the expand control reports glyph
  `keyboard_double_arrow_right`, `visibility:visible`, `::after content:none`
  (overlay gone); the drawer still opens (`aria-expanded` → true); no errors.

## 19. One nav toggle, not two

**Prompt:**

> the problem is now, that there are two ways to open the navigation: on the
> main top bar and when the right bar is hovered on theres the same symbol
> again

**Summary of changes:**

- Diagnosed (headless Chrome) that the rail exposed **two** toggles: the
  toolbar `stExpandSidebarButton` (`»`, always visible, opens the drawer) and
  the sidebar's own `stSidebarCollapseButton` (`«`), which Streamlit keeps
  `visibility:hidden` but **reveals on hover** of the rail — a redundant second
  control (and a left-pointing « reads as "collapse," not "open").
- **`app.py`** — added one rule to the nav-rail CSS block:
  `section[data-testid="stSidebar"][aria-expanded="false"]
  [data-testid="stSidebarCollapseButton"] { display: none !important; }`.
  This overrides the hover-reveal, so in rail mode only the toolbar `»` shows;
  in the expanded drawer (`aria-expanded="true"`) the rule doesn't apply, so
  the « stays as the close button. Result: exactly one toggle per state.
- **`CLAUDE.md`** — noted the hidden hover-toggle in Theming exception 3.
- **Live-verified**: rail (no hover *and* hover) → collapse button
  `display:none`, only `»` visible; drawer → « visible (`display:block`,
  `aria-expanded=true`); no page errors.

## 20. Morphing ☰/✕ toggle inside the menu; drop the top-bar control

**Prompt:**

> add the burger menu icon inside the left menu. when the menu is closed its
> the burger menu icon, when its opened the icon morphs into an X. remove the
> whole left menu logic from the top bar

**Summary of changes:**

- Established (headless Chrome) that `stSidebarCollapseButton` is a **real
  two-way toggle** — when genuinely clickable it expands while collapsed and
  collapses while expanded (the prior "no-op" was its own `display:none`
  swallowing the React click). Since it lives **inside** the sidebar and is a
  single element, it can host the morphing glyph — no JS needed.
- **`app.py`** nav-rail CSS:
  - Reversed entry #19: instead of hiding the in-menu collapse button, force it
    `visibility:visible` in the rail and centre it at the top of the icon
    column (`stSidebarHeader { justify-content:center }`).
  - **Removed the top-bar control**: `[data-testid="stExpandSidebarButton"]
    { display:none !important }`.
  - **Morphing glyph**: hide the native chevron; put `menu` (`\e5d2`) on the
    icon span's `::before` and `close` (`\e5cd`) on `::after`; cross-fade +
    quarter-rotate them by `aria-expanded` so closed shows ☰ and open shows ✕.
- **`CLAUDE.md`** — updated the Navigation section and Theming exception 3 for
  the single in-menu morphing toggle.
- **Live-verified**: rail (`aria=false`) → toolbar expand button `display:none`,
  ☰ shown (`::before` opacity 1, `::after` 0), centred (cx≈38 in the rail);
  open (`aria=true`) → ✕ shown (opacity flips), at the drawer's top-right
  (cx≈266); clicking the in-menu button toggles **both** ways; no page errors.

## 21. Fix: sticky device selector loses full-width after a page round-trip

**Prompt:**

> ive found a bug with the sticky device selector. when i switch a page and
> return to the dashboard the sticky device selector is not full width anymore

**Diagnosis** (reproduced with headless Chrome): the Dashboard's sticky-bar
watcher runs in a `components.html` iframe. Switching pages **destroys** that
iframe, so its scroll listener + `ResizeObserver` + `MutationObserver` (all
owned by the iframe's JS context) die — but `stMain` **persists** across the
SPA navigation (confirmed: same stamped element on return). On return a new
iframe ran, but the old guards (`stMain.__ovBound`, `window.parent.__ovStickyInit`)
were still `true` on those persistent nodes, so it **skipped re-binding** —
leaving a dead scroll listener. Scrolling no longer triggered `sync()`, so the
bar never got its full-bleed geometry (measured `stuck:false`, `barW 1223` vs
the full `1373` after return).

**Fix** (`app_pages/dashboard.py`): the watcher no longer gates on persistent-DOM
flags. Every iframe run re-binds fresh in its own live context, first tearing
down the previous run's bindings via refs parked on the persistent nodes:
`stMain.__ovSync` (compare-and-swap the scroll listener — also prevents
stacking within a run), `stMain.__ovRO` (disconnect + re-arm the
`ResizeObserver`), and `window.parent.__ovMO` (disconnect the prior, now-dead
`MutationObserver`). Updated the sticky-bar note in CLAUDE.md (Theming
exception 1).

**Live-verified**: after returning from Map/Time Series/Devices the bar is
full-width again (`stuck:true`, `barW == mainClientW == 1373`) on **every**
round-trip, and a viewport resize after a round-trip still re-syncs the width
(1133 == 1133) — i.e. the `ResizeObserver` is alive too. No page errors.

## 22. Page name in the top header when the device selector sticks

**Prompt:**

> when the device selector becomes sticky i want the name of the page appear
> above it inside the streamlit top bar

**Summary of changes:**

- A scroll-condense title: when the Dashboard filter bar sticks, the page name
  surfaces in the fixed Streamlit top header, aligned above the bar.
- **Moved the sticky-bar watcher from `dashboard.py` to a global
  `components.html` at the end of `app.py`** and extended it. It now also
  injects a `.ov-header-title` element as a child of `stHeader`, fills it with
  the active nav link's clean `span[label]` text, aligns its left edge to the
  main column (`mainLeft − headerLeft`, since the header's positioned origin is
  offset by the rail/drawer width), and toggles `.ov-visible` with the bar's
  stuck state. **Global on purpose:** the title lives in the persistent header,
  so the watcher must run on *every* page to hide it when `.st-key-ov_bar` is
  absent — otherwise a stale "Dashboard" would linger after scrolling the hub
  then navigating away.
- **`app.py`**: added `import streamlit.components.v1 as components`, the
  `.ov-header-title` CSS (theme-safe `light-dark()` colour, fade+rise
  transition, hidden/inert until `.ov-visible`), and the watcher block.
- **`dashboard.py`**: removed its watcher block and the now-unused `components`
  import (left a pointer comment to app.py).
- **`CLAUDE.md`**: updated Theming exception 1 (watcher now global; header-title
  behaviour; why-global note).
- **Live-verified** (headless Chrome): at rest the title is `opacity:0`; on
  scroll it shows ("Dashboard", `ov-visible`, `y≈28` in the header, left edge
  `x=68` == the bar's `x=68`); scroll-up hides it; navigating to **Map while
  scrolled** hides it (no orphan); returning + scrolling shows it again. No
  page errors.

## 23. Rounded chart/map corners; smoothed line + fade-to-transparent gradient

**Prompt:**

> make sure that for the graphs and maps the corners are rounded accordingly.
> also for the graph: smooth the graph out a bit to make it look nicer and add a
> gradient below the graph that fades to transparent in the same color as the
> graph

**Summary of changes:**

- **`src/components/charts.py`**:
  - Added `_hex_to_rgba` + `_area_gradient` helpers and two tuning constants:
    `_SPLINE = 0.5` (gentle spline tension — kept low so the smoothing doesn't
    invent peaks, per the honesty rule) and `_FILL_ALPHA = 0.26` (peak opacity
    of the area gradient).
  - `line_chart`: the main series is now `line.shape="spline"` + `smoothing`,
    and for **zero-based** measures gets `fill="tozeroy"` + a vertical
    `fillgradient` (Plotly 6.7) fading from the line's colour at the top to
    transparent at the axis. Skipped for temp/pressure (filling to 0 is
    meaningless there). The rolling-average overlay and threshold markers are
    left unfilled.
  - `small_multiples` (spline + gradient on zero-based panels) and
    `normalized_overlay` (spline only — multiple lines, no fill) get the same
    smoothing for visual consistency.
- **`app.py`**: CSS rounds the corners of charts **and** maps —
  `stPlotlyChart { border-radius: 8px; overflow: hidden }` (+ inner
  `js-plotly-plot` / `maplibregl-map`), matching the cards' 8px radius. The big
  win is the opaque OSM map tiles, which previously showed square corners
  inside the rounded card.
- **`CLAUDE.md`**: noted the line aesthetics + corner-rounding on the charts.py
  architecture line.
- **Live-verified** (headless Chrome, 2× DPI): the PM trend shows smooth
  PM2.5/PM10 curves with orange/blue gradients fading to transparent; the
  location map has rounded corners; the legend and the hover modebar (top-right,
  next to a rounded corner) are **not** clipped by `overflow:hidden`. No page
  errors.

## 24. Bridge missing points with a line

**Prompt:**

> when data is missing between points still connect them via a line

**Summary of changes:**

- **`src/components/charts.py`**: flipped every time-series line trace from
  `connectgaps=False` to `connectgaps=True` — the raw `line_chart` series, its
  rolling-average overlay, `small_multiples`, and `normalized_overlay`. Missing
  points (outages / cleaned saturation sentinels) are now bridged by the line
  instead of leaving a break. The honesty disclosure is unchanged: hidden
  readings are still counted and surfaced in the chart's `hidden_notice`
  caption, so nothing is silently dropped — only the visual line is continuous.
- **Verified**: build check shows `connectgaps=True` on a frame with an
  injected NaN gap; the dashboard renders with no page errors; `uv run pytest`
  → 28 passed.

## 25. KPI trend at 24 h: fall back to the last window with data

**Prompt:**

> when i select the 24 hour range, why isnt there a trend comparison to the
> last 24 hours?

**Diagnosis** (queried the live DB): not a bug — the default device
(SENSORpi s01) has a ~4-day gap in its record (Nov 6 03:03 → Nov 10 12:34). At
24 h the current window (Nov 10→11) has 1,109 readings but the immediately-
preceding 24 h window (Nov 9→10) has **0** — it lands entirely in the gap — so
`load_range_summary` returned `delta=None` and the tiles correctly showed no
arrow (no misleading trend against an empty period). 7 d/30 d reach past the gap,
so they did show a trend.

**Decision:** asked the user; they chose **fall back to the last equal-length
window that has data** (over a "no-comparison" hint or leaving it blank).

**Summary of changes:**

- **`src/data/loaders.py`** — `load_range_summary` now: when the immediately-
  preceding window holds no readings (a `count(*) FILTER (...) == 0` check),
  it finds the last reading before `start` (`max(ts) WHERE ts < :start`, index-
  backed) and measures the delta against the equal-length window ending there
  instead. Two extra cheap queries, only on the gap path. New return value
  `baseline_end` (the fallback window's end, else `None`) signals the shift to
  the UI. The contiguous case and "All" (no prior reading) are unchanged.
- **`app_pages/dashboard.py`** — unpacks the new `baseline_end`; the trend label
  is now built after the query and reads **"previous 24 h with data (to Nov 06)"**
  when the baseline was shifted, plain **"previous 24 h"** otherwise. Moved the
  strip caption into a placeholder (`cap_ph`) since the label is only known
  post-query.
- **Live-verified**: at 24 h the hero/KPI tiles now show trend arrows (PM2.5
  ↑ +9.2 µg/m³) and the strip caption reads "24 h average · trend vs. previous
  24 h with data (to Nov 06)"; 7 d still uses the immediate prior window
  (delta +1.22, no "with data" suffix); "All" still shows no trend. `uv run
  pytest` → 28 passed; no page errors.

## 26. Check color contrasts against WCAG 2.0

> check the color contrasts, if they work according to WCAG 2.0

**No code change — audit only.** Computed WCAG contrast ratios for every
foreground/background pair in `.streamlit/config.toml` + `src/utils/palette.py`.

**Scope note:** WCAG **2.0** only sets contrast minimums for *text*
(1.4.3 AA 4.5:1 / 1.4.6 AAA 7:1; large text 3:1 / 4.5:1). It has **no**
non-text-contrast rule (that is 1.4.11, added in WCAG 2.1), so chart fills,
map markers, and component borders are out of WCAG-2.0 scope here.

**Result — all actual on-screen text passes WCAG 2.0 AA:**
- Body text: light `#1F2328` on canvas/white/secondary = 14.2–15.8:1 (**AAA**);
  dark `#E6EDF3` on bg/secondary = 14.6–16.0:1 (**AAA**).
- Links/primary: light blue `#0072B2` on canvas/white/secondary = 4.67–5.19:1
  (**AA**, just under the 7:1 AAA bar); dark `#56B4E9` = 7.5–8.2:1 (**AAA**).
- Raw palette accents (green/orange/red/yellow) fall **below** 4.5:1 as text on
  white *in the abstract*, but they are never used as raw text — they appear as
  chart fills/lines (backed by shape+label+position, satisfying 1.4.1) and as
  Streamlit `:color-badge[…]` / `st.metric` deltas, whose fg/bg pairing is
  managed by Streamlit's own (accessible) design system.

**Out of WCAG-2.0 scope but flagged for 2.1 (1.4.11):** borders
(`#D0D7DE` on white = 1.45:1; dark `#30363D` on bg = 1.55:1) and several chart
hues sit under 3:1 against their backgrounds — fine for 2.0, would fail 2.1
non-text contrast if borders were the sole means of identifying a component.

## 27. Remove the "Open in Time Series" buttons from the Dashboard

> remove the "Open In time series" buttons from the dashboard

**Summary of changes:**

- **`app_pages/dashboard.py`** — removed both `st.button("Open in Time Series",
  …, on_click=hand_off_to_timeseries, …)` calls: one under the mobile route-map
  bento cell and one under the desktop PM-trend bento cell. The bento boxes now
  show just their title + chart/map.
- Dropped the now-unused `hand_off_to_timeseries` import from the
  `src.utils.state` import line; updated the bento comment that referenced "the
  hand-off button". (The `src.utils.state` helper itself is unchanged and still
  used by the Map page's hand-off.)

## 28. Equal-height bento cards (graph / map row)

> make sure that the graph and the map sections have the same height, same for all boxes that are aligned in the same row

**Summary of changes:**

- **`app.py`** (documented `st.html(<style>)` exception) — added an
  equal-height rule for the Dashboard's Zone-3 bento row. Each bento cell is its
  own `st.container(border=True)` that sized to its own content, so the cell with
  a "Full map" link (or fewer trip-stat tiles) was shorter than its neighbour and
  the row read ragged. Streamlit has no equal-height-columns knob, so the rule
  (scoped via `:has()` to rows containing `.st-key-box_pmtrend` /
  `.st-key-box_routemap`) sets the row to `align-items: stretch`, overrides the
  per-column `align-self` that `vertical_alignment="top"` applies, makes the
  column's vertical block `height:100%`, and lets each bordered card
  (`box_pmtrend`/`box_locmap` desktop, `box_routemap`/`box_tripstats` mobile)
  fill its column — so the graph card and the map card share one bottom edge.
  Guarded to `@media (min-width:768px)` (columns stack on phones, where equal
  height is moot). Degrades gracefully: no `:has()`/CSS → the prior
  content-sized cards, never broken.

## 29. Move "Full map" link to the top-right of its box

> replace the "Full Map" button to the top right of its box

**Summary of changes:**

- **`app_pages/dashboard.py`** — in the desktop `box_locmap` (Location) bento
  cell, moved the `st.page_link("Full map")` from the bottom of the box up into
  a header row beside the "Location" title. The header is a two-column row
  (`st.columns([1, 1], vertical_alignment="center")`): the title on the left, and
  the link in a right-aligned horizontal container
  (`horizontal_alignment="right"`) so it sits flush to the box's top-right
  corner. The map then renders directly below the header.

## 30. Move the CAQI tooltip up to the "Air quality" title

> in the airquality box, put the tool tip thats next to "CAQI · computed" on the top next to " Air quality"

**Summary of changes:**

- **`src/components/kpi.py`** (`aqi_tile`) — moved the `help=COMPUTED_NOTE`
  tooltip from the "CAQI · computed" caption up to the ":material/speed: **Air
  quality**" title (`st.markdown(..., help=COMPUTED_NOTE)`). The caption now
  reads plain "CAQI · computed" with no tooltip; the (?) hint sits next to the
  box title at the top.

## 31. Remove the redundant PM2.5 tile from the hero box

> remove the pm2.5 box out of the "SENSORpi s01 · Minden — air quality: Good" box since its already below it and redundant

**Summary of changes:**

- **`app_pages/dashboard.py`** — removed the dominant-pollutant metric tile
  (PM2.5, formerly the hero's right-hand `hR` column) from the Zone-1 hero card.
  It duplicated the PM2.5 KPI tile in the strip directly below it. Dropped the
  `st.columns([0.62, 0.38])` split and the `dom_key` logic; the verdict
  (subheader + CAQI badge + advice + meta caption) now spans the full hero
  width. `metric_tile` is still imported/used by the KPI strip, so the import is
  unchanged.

## 32. Drop the redundant sensor/range echo chips from the filter bar

> also remove " Stationary · SENSORpi s01 · Minden 7 d" because its literally directly displayed in the selection obove these tags

**Summary of changes:**

- **`src/components/filter_bar.py`** — the active-filter echo row (`_render_chips`)
  printed the selected sensor label(s) as blue badges + the range preset as a
  gray badge + the resolved start→end span. The sensor and the range preset are
  already shown by the multiselect/selectbox and the segmented control directly
  above, so those chips were redundant. Renamed `_render_chips` →
  `_render_window`, which now emits only the concrete resolved time-window badge
  (`:material/date_range:` start→end) — the one piece the picker doesn't show
  (kept as Shneiderman #3 feedback). Updated the call site; no other references.
  Applies to every filter bar (Dashboard `ov`, Time Series `ts`, Compare `cmp`).

## 33. Slim hero verdict + red→green air-quality meter

> also this is redundant: "SENSORpi s01 · Minden — air quality: Good / CAQI: Very low   Air quality is good — particulate pollution is very low." Just make it "Air Quality: Good" with a tool tip for "CAQI from PM2.5/PM10 · 7 d average · through 2025-11-11 11:09". Below it put a bar coloured red→green with a dot showing where the current air quality is (red = very bad, green = very good); slim bar, rounded on both sides, block dot with white outline.

**Summary of changes:**

- **`app_pages/dashboard.py`** — collapsed the Zone-1 hero to a single verdict
  line `:{icon}: Air quality: {quality}` with the provenance/window string
  (`CAQI from PM2.5/PM10 · <avg> average · through <ts>`) moved into the
  heading's `help` tooltip. Removed the device name (already in the picker), the
  `:badge[CAQI: …]` line, and the advice sentence (all restated the verdict).
  Below the heading it now renders the new meter at a marker position derived
  from the continuous CAQI index. Dropped the now-unused `device_label` import,
  `device_name` var, and `_BAND_BADGE` map; swapped `COMPUTED_NOTE` import for
  `caqi_index`.
- **`src/utils/aqi.py`** — added `caqi_index(pm2_5, pm10)`: a continuous CiteAir
  CAQI index (0 cleanest .. 100 worst, worse-of-the-two via linear interpolation
  between the band breakpoints), the positioning companion to the stepped
  `caqi_band`. Plus `_subindex` + the `_PM25_GRID`/`_PM10_GRID` breakpoints.
- **`src/components/meter.py`** (new) — `air_quality_meter(position, dot_color)`:
  emits the meter markup (`st.html`, same escape hatch as `skeleton.py`). Only
  the marker's `left` offset and fill colour are inline; everything static is in
  app.py CSS. `position` is 0 (worst/red/left) .. 1 (best/green/right).
- **`app.py`** — added `.aq-meter` (slim 8px pill, `border-radius:999px`, fixed
  red→amber→green Okabe-Ito gradient) and `.aq-meter-dot` (16px round marker,
  3px white ring + soft shadow, centred on its `left` offset) to the documented
  `st.html(<style>)` block.
- **`src/components/skeleton.py`** — `hero()` skeleton reshaped to match: a
  heading bar above a slim full-width meter bar (was a two-column heading+tile).
- Colour is never the only channel: the verdict word + the marker's spatial
  position + the hue triple-encode the value. `uv run pytest` → 28 passed.

## 34. Fold "CAQI · computed" caption into the Air quality tile tooltip

> from the airquality box remove "CAQI · computed" and put it in the tooltip

**Summary of changes:**

- **`src/components/kpi.py`** (`aqi_tile`) — removed the `st.caption("CAQI ·
  computed")` line from the Air quality KPI tile and folded the text into the
  title's tooltip: the "Air quality" heading's `help` is now
  `f"CAQI · computed — {COMPUTED_NOTE}"`. The tile now shows just the title +
  the band badge, with the provenance available on hover.

## 35. Equal-height KPI strip (CAQI tile matches the metric tiles)

> make sure this box has the same height as the other on in its row anyways

**Summary of changes:**

- **`app.py`** — after removing the "CAQI · computed" caption, the Air quality
  (`box_aqi`) tile was shorter than the `st.metric` tiles in the KPI strip. The
  strip is a horizontal container with the default `vertical_alignment="top"`
  (`align-items:flex-start`), so tiles size to their own content. Added a
  `:has(.st-key-box_aqi)`-scoped rule to the documented `st.html(<style>)` block:
  sets the strip to `align-items:stretch`, stretches its flex children
  (`stElementContainer`), and gives `.st-key-box_aqi` + the `stMetric` cards
  `height:100%`, so the CAQI tile matches the metric tiles' height. Degrades
  gracefully (no `:has()` → the prior content-sized tiles).

## 36. Match the time-range selector height to the sensor selector

> make the time range selector the same height as the sensor selector

**Summary of changes:**

- **`app.py`** — the segmented Time-range control renders shorter than the
  sensor select beside it in the filter bar, so they didn't line up. Added a rule
  (scoped to the three filter-bar keys `.st-key-ov_bar` / `.st-key-ts_bar` /
  `.st-key-cmp_bar`) pinning the segmented-control pills
  (`[data-testid^="stBaseButton-segmented_control"]`, covers active + inactive)
  to `min-height: 2.5rem` — Streamlit's standard control height
  (`minElementHeight`), which the selectbox/multiselect already use. Same rem
  unit on the same root, so they match at any base font size. Documented
  `st.html(<style>)` exception; degrades gracefully to the prior shorter pills.

## 37. Style the strip trend caption as a grey badge

> make the text "24 h average · trend vs. previous 24 h with data (to Nov 06)" have the same styling as the text "2025-11-10 11:09 → 2025-11-11 11:09" (grey background)

**Summary of changes:**

- **`app_pages/dashboard.py`** — the KPI-strip trend label (avg window + "trend
  vs. …") was a plain `st.caption`; rendered it as a grey badge
  (`cap_ph.markdown(f":gray-badge[{strip_cap}]")`) so it matches the grey
  time-window badge under the filter bar (`_render_window`). The
  `:material/schedule:` icon stays inside the badge.

## 38. Match the graph↔map gap to the KPI tile gap

> make the vertical gap between the graph and map the same size as the horizontal gap to the kpis

Clarified via a question: the user wanted the graph↔map gap shrunk to match the
KPI tile spacing (rather than growing the vertical space above the bento).

**Summary of changes:**

- **`app_pages/dashboard.py`** — changed the Zone-3 bento row from
  `st.columns([2, 1], gap="medium", …)` to `gap="small"`, so the horizontal gap
  between the graph and map cards matches the gap between the KPI strip tiles
  (the strip's `st.container(horizontal=True)` uses the default `small` gap).

## 39. Remove the divider above the Compare/Correlation tabs

> remove the divider above the compare and correlation tabs

**Summary of changes:**

- **`app_pages/dashboard.py`** — removed the `st.divider()` that sat between the
  Zone-3 bento and the secondary tab strip (Compare / Correlation / Routes). The
  tabs now follow the bento directly. Updated the module docstring's layout
  description to drop the "one st.divider" mention.

## 40. Render the CAQI tile as a plain metric (match the strip tiles)

> in the box "Air quality / Very low" make the Text "Very low" match the other boxes in this row, remove the green and the smiley

**Summary of changes:**

- **`src/components/kpi.py`** (`aqi_tile`) — replaced the bordered container +
  coloured `:{color}-badge[{icon} {label}]` with a plain `st.metric(":material/
  speed: Air quality", band.label, help="CAQI · computed — …", border=True)`. The
  band word ("Very low") now renders in the same big value typography as the
  measurement tiles beside it; removed the green badge colour and the sentiment
  smiley. Dropped the now-unused `_BAND_BADGE` map. (The colour/position encoding
  of the band still lives on the hero meter, so it isn't lost overall.)
- **`app.py`** — removed the now-dead `:has(.st-key-box_aqi)` equal-height CSS:
  the CAQI tile is a `st.metric` like the others now, so the strip tiles are
  uniform height inherently (no `box_aqi` container exists anymore).
- `uv run pytest` → 28 passed.

## 41. Equal-height KPI strip again (CAQI metric has no delta row)

> again, the height has to match the other boxes in this row

**Summary of changes:**

- **`app_pages/dashboard.py`** — gave the KPI-strip horizontal container a
  `key="kpi_strip"` so it can be targeted in CSS.
- **`app.py`** — re-added an equal-height rule, now scoped to `.st-key-kpi_strip`:
  the measurement tiles carry a trend-delta arrow row but the CAQI `st.metric`
  has no delta, so it rendered shorter. The rule sets the strip to
  `align-items:stretch`, stretches its `stElementContainer` children, and gives
  the `stMetric` cards `height:100%`, so all tiles in the strip share one height.

## 42. Remove the CAQI tile from the KPI strip

> nevermind, just remove this box

**Summary of changes:**

- **`app_pages/dashboard.py`** — removed the `aqi_tile(band)` call from the KPI
  strip (the strip now shows only the HEADLINE_KPIS measurement tiles). Dropped
  the `aqi_tile` import and the `key="kpi_strip"` added for the equal-height
  attempt.
- **`app.py`** — removed the now-unneeded `.st-key-kpi_strip` equal-height CSS.
- `aqi_tile` itself is kept (still used by the Map page's details-on-demand CAQI
  tile); `band` is still used by the hero verdict + meter. `uv run pytest` → 28
  passed.

## 43. Move Compare and Correlation out of the Dashboard into their own pages

> remove the sections compare and correlation from the dashboard and move them into their own pages

**Summary of changes:**

- **`app_pages/compare.py`** (new) — thin top-level page: title + caption +
  `render_compare()` (the body still lives in `comparison.py` with its own `cmp`
  multi-sensor toolbar).
- **`app_pages/correlation.py`** (new) — standalone page carrying the verdict-first
  |r| correlation UI lifted from the Dashboard's old Correlation tab, now with its
  own single-sensor `corr` toolbar and bookmarkable URL state (`corr_sensors` /
  `corr_range` / `corr_measures`).
- **`app.py`** — registered both pages in the *Monitor & Analyse* nav group
  (Dashboard, Time Series, **Compare**, **Correlation**, Map) with
  `:material/compare_arrows:` / `:material/scatter_plot:` icons. Added
  `.st-key-corr_bar` to the two shared filter-bar CSS rules (card styling +
  segmented-control height) so the new toolbar matches the others.
- **`app_pages/dashboard.py`** — removed the secondary tab strip and both the
  Compare and Correlation tab bodies. The mobile-only **Routes** inspector, which
  previously shared that tab strip, now renders as a plain section (subheader, no
  tabs). Dropped the now-unused imports (`itertools`, `render_compare`,
  `build_comparison_frame`, `available_metrics`, the `correlate` helpers, `get`,
  `csv_split`); trimmed `seed_session_defaults`/`publish_query_params` to
  `ov_sensors`/`ov_range` (no more `ov_corr`); fixed the KPI skeleton count
  (`len(HEADLINE_KPIS)`, the CAQI tile is gone); updated the module docstring and
  the route-map tooltip ("Routes section" not "Routes tab").
- **`CLAUDE.md`** — updated the file-tree note, the Pages table (new Compare +
  Correlation rows; Dashboard row no longer lists tabs), the "no longer a page"
  paragraph, the navigation section/icon lists, and the skeleton-wiring note.
- `uv run pytest` → 28 passed.

## 44. Dashboard per-device entry list + clickable route detail page

> now in the dashboard, add a list of the corresponding points, with the most important information per point. for the mobile devices list the corresponding routes. the routes should be clickable and should open a new page that displays the most important information about this route: stats, then the route displayed on a map etc. the whole styling and layout should follow the dashboard

Clarified "points" via a question: it means the sensor's **data points / readings**
for the picked sensor + duration, most-recent-first, with lazy "load more".

**Summary of changes:**

- **`app_pages/dashboard.py`** — added a per-device entry list below the bento:
  - **Stationary** → a **Recent readings** card (`box_points`): `load_raw_readings`
    for the newest `ov_points_n` rows (default 25) in the picked range, sentinels
    blanked via `clean_frame`, a computed CAQI word per row, shown as a
    `st.dataframe` with metric-registry column config; a **Load more** button
    grows `ov_points_n` by 25 (lazy loading — only fetches what's shown; the
    button hides once a short page comes back).
  - **Mobile** → the **Routes** section is now one clickable `st.button` per trip
    (Route N · time span · points · duration · mean PM2.5). Click →
    `st.switch_page("app_pages/route.py", query_params=…)`. (Buttons, not a
    selectable dataframe, because a dataframe selection persists in session_state
    and would re-fire the page switch on every return.) Re-added the `get` /
    `load_raw_readings` / `clean_frame` imports.
- **`app_pages/route.py`** (new, hidden page) — the route drill-down, styled like
  the cockpit: reads `route_table`/`route_id`/`route_gap`/`route_start`/`route_end`
  from the URL, re-segments via `load_routes`, isolates the trip, then renders a
  verdict hero + red→green meter (CAQI from mean PM2.5) → a KPI strip (points,
  duration, **distance** via a haversine helper, mean/max PM2.5) → the route on a
  map → PM2.5 over time. Graceful messages + a "Back to Dashboard" link when the
  params are missing/stale.
- **`app.py`** — registered `route.py` with `visibility="hidden"` (navigable via
  `switch_page`, not shown in the rail).
- **`CLAUDE.md`** — documented the new list, the Route detail page, and the
  hidden-page mechanism.
- Smoke-tested both data paths against the live DB (stationary readings + CAQI
  words; mobile m01 → 28 routes, route 0 = 490 pts / 11.2 km / mean PM 2.3).
  `uv run pytest` → 28 passed.

## 45. Equal-width KPI strip tiles

> make the tiles [PM2.5 / PM10 / CO₂ / Temp / Humidity] … also have the same width

**Summary of changes:**

- **`app_pages/dashboard.py`** — the KPI strip used a horizontal container, which
  sized each tile to its own content (so tiles differed in width). Switched to
  `st.columns(len(strip_keys))` and rendered one `metric_tile` per column, so the
  row splits evenly and every KPI card is the same width.

## 46. Remove Time Series / Compare / Map pages; "Full map" → in-place overlay

> remove the time series, compare and map pages. when clicking "Full Map" i just want an overlay of the map with the corresponding point / Route drawn into it

**Summary of changes:**

- **`app.py`** — unregistered the Time Series, Compare and Map pages. Nav is now
  *Monitor & Analyse* (Dashboard, Correlation) + *Reference & Settings* (Devices,
  Settings), plus the hidden Route detail page.
- **Deleted** `app_pages/timeseries.py`, `app_pages/compare.py`,
  `app_pages/comparison.py` (orphaned once Compare went), `app_pages/map.py`.
- **`app_pages/dashboard.py`** — "Full map" no longer links to the Map page; it
  opens a modal **map overlay** via `@st.dialog(width="large")`:
  - stationary `box_locmap` → `_location_overlay(loc_one)` (the device's location
    point on a big interactive map);
  - mobile `box_routemap` → got a "Full map" button → `_routes_overlay(routes)`
    (the device's routes drawn in). Buttons capture the click into a local and the
    dialog is invoked *after* the cell's data has loaded (so the data is in scope),
    which also avoids any reopen-on-rerun loop.
- **`app_pages/settings.py`** — removed the now-broken `st.page_link` to Time
  Series and the entire **Saved views** expander (it could only be created/applied
  on the removed Time Series page); dropped the unused `load_saved_views` /
  `delete_view` imports and trimmed the docstring. Threshold add/delete stays.
- **`CLAUDE.md`** — updated the file tree, Pages table, navigation section + icon
  list, and skeleton-wiring note to drop the three removed pages and describe the
  Full-map overlay.
- Note: `src/utils/state.py::hand_off_to_timeseries` is now orphaned (its only
  caller was the Map page) — left in place, uncalled; flag for later cleanup.
- `uv run pytest` → 28 passed.

## 47. Make the mobile routes read as a list of cards, not stacked buttons

> the list of routes looks weird, because its not really a list. it looks like a bunch of buttons below each other

**Summary of changes:**

- **`app_pages/dashboard.py`** — replaced the full-width route buttons with one
  bordered **card per trip** (`box_route_<id>`, so it picks up the dashboard card
  styling): the trip facts on the left (Route N · time span + grey badges for
  points / hours / mean PM2.5) and a small right-aligned **Open** button that
  switches to the Route detail page. Reads as a list of cards rather than a stack
  of buttons.

## 48. Make routes clickable on the map too

> can you make it so that the route is clickable also on the map?

**Summary of changes:**

- **`src/components/charts.py`** (`route_map`) — added `route_id` as a second
  customdata column on the PM-point markers (`customdata[1]`), so a clicked map
  point can be resolved to its trip. The hovertemplate still uses
  `customdata[0]` (the PM value), unchanged.
- **`app_pages/dashboard.py`** — the Dashboard route map now renders with
  `on_select="rerun"`, `selection_mode="points"` and a key. Clicking a point
  reads `customdata[1]` → `route_id` and `st.switch_page`s to the Route detail
  page (same query params as the list cards). A signature guard
  (`ov_routemap_nav`) prevents the restored selection from re-firing the switch
  when you navigate back. Caption updated to "click a point to open that trip."
- `uv run pytest` → 28 passed; verified `route_map` builds with the 2-col
  customdata against live mobile data.

## 49. Fix route-map click (KeyError) + hover/cursor affordance

> when you click a route this happens [KeyError: 1 at int(cd[1])] ... i want it to link to the corresponding route page. also add some user feedback if you hover a route, and a pointer so the user knows it clickable

**Diagnosis:** the plotly selection `customdata` did not arrive as a plain list,
so `cd[1]` raised `KeyError: 1` (it came through keyed by index, i.e. a dict).

**Summary of changes:**

- **`app_pages/dashboard.py`** — made the click handler robust: if `customdata`
  is a dict, rebuild it into an index-ordered list; then read `route_id` at
  index 1; if that fails, **fall back** to matching the clicked point's
  `lat`/`lon` (or `x`/`y`) against the `routes` frame to find the trip. Only
  navigates when a `route_id` resolves (kept the signature guard against
  re-firing on navigate-back). This fixes the crash so a click opens the
  corresponding Route detail page.
- **`src/components/charts.py`** (`route_map`) — added a `clickable` flag; when
  set, the PM-point hover tooltip appends *"Click to open this trip →"* so
  hovering signals the action. Dashboard passes `clickable=True`; the Route
  detail map leaves it off.
- **`app.py`** — added a pointer-cursor rule scoped to the Dashboard route map
  (`.st-key-box_routemap .maplibregl-canvas-container.maplibregl-interactive`),
  so the map shows a pointer (MapLibre defaults to a grab cursor).
- **`app_pages/route.py`** — renamed the detail map container to
  `box_routedetailmap` so the pointer cursor + click affordance apply only to
  the clickable Dashboard map.
- `uv run pytest` → 28 passed.

## 50. Route map: pointer only on hover + highlight the hovered trip

> only add a pointer when you actually hover a route, not all the time in the map view. also when you hover close to a route make the whole route be highlighted if thats possible via openstreet map

**Summary of changes:**

- **`app.py`** — removed the always-on pointer-cursor CSS on the route map.
- **`app_pages/dashboard.py`** — added a 0-height same-origin `components.html`
  iframe (mobile only; same documented escape hatch as the sticky-bar watcher)
  that binds `plotly_hover` / `plotly_unhover` on the route map's graph div:
  - on hover of a trip (a PM point *or* its line — lines carry `hoverinfo="name"`,
    so hovering *close* to a route triggers it), set the map cursor to **pointer**;
    on unhover, revert. So the pointer shows only over a trip, not across the
    whole map.
  - on hover, **highlight the whole trip**: `Plotly.restyle` thickens that route's
    line (width 5, opacity 1) and dims the others (opacity 0.25); unhover restores
    width 1.6 / opacity 0.9. A `MutationObserver` re-binds across reruns.
  - Cursor toggling is self-contained; the line highlight is best-effort (needs
    the page's global `Plotly`) and degrades silently if unavailable.
- `uv run pytest` → 28 passed.

## 51. Route hover effect: reveal a polygon (convex hull) around the trip

> can you make the hovering effect for the routes that it creates a polygon as the area that encapsulates the route

**Summary of changes:**

- **`src/components/charts.py`** — added a scipy-free `_convex_hull` (Andrew's
  monotone chain). When `route_map(clickable=True)`, it now emits one **hidden**
  filled-polygon trace per trip — the convex hull of that trip's points — tagged
  `meta="hull<route_id>"` (subtle vermillion fill, `visible=False`).
- **`app_pages/dashboard.py`** — the hover watcher no longer thickens the route
  line; instead it **reveals the hovered trip's hull polygon** (`Plotly.restyle`
  the matching `hull<id>` trace to `visible=true`, all others false) and hides it
  again on unhover. Pointer-cursor-only-on-hover is unchanged. Hovering a PM point
  (customdata route_id) or near the route line (curve number) both resolve the
  trip; hull traces use `hoverinfo="skip"` so they don't interfere.
- Verified: hull drops interior points; `route_map(clickable=True)` builds 28
  hidden hull traces for the mobile device. `uv run pytest` → 28 passed.

## 52. Dashboard route map shows routes (paths), detail shows datapoints

> and make it so that on the dashboard the routes are actually routes and not datapoints. when clicking a route it shows the more detailed version of the route with all datapoints

**Summary of changes:**

- **`src/components/charts.py`** (`route_map`) — added `show_points: bool = True`.
  - `show_points=False` (Dashboard): each trip renders as a **path**
    (`lines+markers`, small same-colour nodes) and the **PM-coloured Viridis
    datapoint scatter is omitted**. Each route trace carries `route_id` as the
    last `customdata` field for click/hover resolution; clickable adds the hover
    hint.
  - `show_points=True` (Route detail, default): unchanged — the full PM-coloured
    datapoint markers are drawn.
- **`app_pages/dashboard.py`** — the Dashboard route map and the "Full map"
  overlay now call `route_map(..., show_points=False)`; the detail page
  (`route.py`) keeps the default, so clicking a route opens the detailed version
  with all datapoints. Click handler now reads the **last** customdata field
  (route node = `[route_id]`, PM marker = `[pm, route_id]`) and falls back to the
  point's curve number (== route_id) then its coordinate. Caption → "click a
  route to open it."
- Verified: Dashboard map = 0 datapoint scatter traces, 28 route paths
  (`lines+markers`, with customdata); detail map keeps the 1 PM-scatter trace.
  `uv run pytest` → 28 passed.

## 53. Route as one continuous line + fix hull-on-hover not showing

> nah its still single points connected by lines instead of an actual route. i want it to be one object. also the hull is not visible

**Diagnoses:**
- The dashboard route used `mode="lines+markers"`, so it read as dots joined by
  lines. → switched to **`mode="lines"`** (one continuous object).
- The hull never showed because the hover JS captured `window.parent.Plotly`
  **once** at iframe load — but Streamlit assigns `window.Plotly` only when the
  chart's (lazy) chunk loads, which can be *after* the iframe runs, so it stayed
  `undefined`. Also confirmed Streamlit drives selection via **`plotly_click`**,
  which fires on line traces — so a markerless line is still clickable.

**Summary of changes:**

- **`src/components/charts.py`** (`route_map`, `show_points=False`) — the trip is
  now a single `mode="lines"` trace (no nodes), a touch thicker (width 2.6) for
  easy hover/click; every vertex still carries `route_id` as the last customdata
  field. `fill="toself"` confirmed supported on `go.Scattermap` (plotly 6.7).
- **`app_pages/dashboard.py`** — the hover watcher now reads Plotly **fresh** in
  each handler (`P()` helper) instead of caching it, so the hull-polygon
  `restyle` works once the chunk is available. Cursor + click unchanged.
- Verified: dashboard map traces are all `mode='lines'`; 28 route lines (with
  customdata) + 28 hidden hull polygons. `uv run pytest` → 28 passed.

## 54. Stable hull-on-hover (no flicker) + centroid tooltip

> the hull is a bit weird, it lags a bit. also it refreshes every time you skip from one datapoint to the next on one single route. just dont make it like that. forget the hovering over single points. if you hover inside the hull make it visible and show the tooltip in the center of it -> dont re render the hull every single time you move your cursor inside the hull

**Diagnosis:** the watcher restyled the hull on *every* `plotly_hover` event, so
moving point-to-point along one trip re-rendered it (the lag/flicker). Also
checked: `go.Scattermap` (MapLibre) does **not** support `hoveron`, so a polygon
*interior* cannot be a hover target — only the route line/points fire hover.

**Summary of changes:**

- **`src/components/charts.py`** (`route_map`, dashboard mode) — the per-trip hull
  is now **always present but fully transparent** (`fillcolor` alpha 0,
  `visible=True`, no outline) instead of a hidden trace; added a per-trip
  **centroid text label** (`meta="label<id>"`, hidden) as the centre tooltip. The
  route line carries `hoverinfo="none"` (no per-point tooltip).
- **`app_pages/dashboard.py`** — rewrote the hover watcher so it restyles **only
  when the hovered route changes** (`rid === lastRid` → no-op), tinting that
  trip's hull (`fillcolor`) and showing its centroid label; un-hover is
  **debounced 150 ms** so brushing across a gap doesn't flicker. Moving along one
  trip no longer re-renders anything. Pointer cursor on hover unchanged.
- Verified: 28 transparent hull traces + 28 hidden centroid labels; the hull
  tint/label toggle is driven purely by route change. `uv run pytest` → 28 passed.

## 55. Route map performance: collapse traces (86 → 3)

> still lagging hard. is it possible to improve the performance?

**Diagnosis:** the dashboard route map carried ~86 MapLibre traces (one line +
one always-rendered transparent hull fill + one hidden label *per trip*, ×28).
MapLibre re-renders every layer on any restyle and hit-tests every trace per
mousemove, so both hovering and the per-hover `restyle` of 56 traces were slow.

**Summary of changes:**

- **`src/components/charts.py`** —
  - `route_map` (dashboard mode, many trips): the per-trip lines are collapsed
    into **one** grey poly-line (`None`-separated segments) with `route_id` as
    per-vertex customdata. ≤8 trips keep distinct coloured lines.
  - The 28 hull + 28 label traces are replaced by **two reusable overlay traces**
    (`meta="activehull"` / `"activelabel"`), empty until hovered.
  - Added `route_hulls(routes)` → `{route_id: {lat, lon, clat, clon, text}}`.
- **`app_pages/dashboard.py`** — the hover watcher injects `route_hulls` as JSON
  and, on a *route change* only, **repoints the single active hull + label** to
  the hovered trip (2 one-trace restyles) instead of restyling 56 traces. Cursor
  + debounced clear unchanged.
- Result: the dashboard route map for a 28-trip device went from **~86 traces to
  3**; hover does 2 one-trace restyles. `uv run pytest` → 28 passed.

## 56. Real (styled) tooltip for the route hover

> also the tooltip that is displayed should actually look like a tooltip and not just blank text

**Diagnosis:** the centroid label was a Scattermap `mode="text"` trace — drawn on
the MapLibre *canvas*, so it was bare text with no box (and not CSS-stylable).

**Summary of changes:**

- **`src/components/charts.py`** — removed the `activelabel` text trace; the
  dashboard route map now adds only the `activehull` overlay (so it's 2 traces).
- **`app_pages/dashboard.py`** — the hover watcher now creates a **styled HTML
  tooltip div** (dark rounded box, shadow, white text, `pointer-events:none`)
  appended over the map. On a route change it positions the tooltip at the trip
  **centroid** via MapLibre's `map.project([lon, lat])` (fallback: map centre),
  fills it with the trip label + a "Click to open" hint, and fades it in; it
  fades out on un-hover. Still one `restyle` of the single hull trace per route
  change — no perf regression.
- Verified: dashboard route map is now **2 traces**. `uv run pytest` → 28 passed.

## 57. Fix route-click routing to the wrong page

> when i click a route it doesnt correcly route me to the right page

**Diagnosis:** after collapsing the trips into one combined poly-line, the click
handler's **curve-number fallback** broke — every trip now lives in trace index 0,
and 0 is a valid route_id, so any click resolved to route 0. The 1-column
customdata could also come back as a bare scalar the parser didn't handle, so it
fell through to that fallback.

**Summary of changes:**

- **`src/components/charts.py`** — the dashboard route lines (combined poly-line
  and the ≤8 coloured lines) now carry **2-column** customdata `[route_id,
  route_id]`, so a clicked point's customdata is reliably a list (route_id last),
  never a bare scalar.
- **`app_pages/dashboard.py`** — the click handler now: parses customdata as
  list / dict / scalar; **removed the curve-number fallback** (meaningless with a
  shared trace); falls back to a **tolerant** coordinate match (`abs diff < 1e-4`);
  and only navigates when the resolved `rid` is an actual route_id.
- Verified the combined line's customdata is `(N, 2)` with distinct route_ids 0–27.
  `uv run pytest` → 28 passed.

## 58. Fix route-map click navigation (for real) + distinct colours + hardcode gap

> no it still doesnt work [route click] ... also for the second mobile sensor, the routes all have the same color. also remove the "Start a new trip when the gap exceeds" thing and hardcode it with 1 hour

**Real diagnosis (via Playwright, installed as a dev dep):**
1. Streamlit's plotly **selection only fires for marker/point clicks, never line
   clicks** — captured `selection.points == []` on a line click. So a
   markerless route can't be opened via `on_select`.
2. The JS-navigation fallback I'd tried throws `SecurityError` — Streamlit's
   `components.html` iframe is **sandboxed without top-navigation**, so it can
   restyle the parent (hover works) but cannot set `window.parent.location`.
3. The combined grey poly-line (perf change) also made every trip share trace
   index 0, so colours collapsed to grey and clicks resolved to route 0.

**Summary of changes:**

- **`src/components/charts.py`** (`route_map`, dashboard mode) — reverted to **one
  trace per trip** with **distinct cycling colours** (fixes the all-grey 2nd
  sensor). Each trip is `lines+markers` with **same-colour markers** sitting on a
  thick line, so it still reads as one continuous route but is *clickable*
  (markers are what Streamlit's selection needs). 2-column `customdata`
  (`[route_id, route_id]`). The `activehull` overlay is added **first** so it sits
  *under* the lines (a tinted hull on top was swallowing the click).
- **`app_pages/dashboard.py`** — click handling is back to **`on_select` →
  `st.switch_page`** (server-side, no iframe limit); resolves route_id from the
  marker's customdata with a signature guard. Removed the dead JS click-nav +
  `ROUTE_BASE`. **Removed the gap select-slider; gap is hardcoded to 1 h.** Kept
  the JS hover hull + HTML tooltip.
- **Verified with Playwright:** clicking a route marker now opens the Route detail
  page (3/3). `uv run pytest` → 28 passed.

**Known limitation:** when a device's trips overlap on the same roads, their
markers stack, so a click resolves to the topmost trip there (not necessarily the
one visually intended) — inherent to overlapping GPS tracks.

## 59. Fix route hover breaking after a time-range change

> sometimes when changing the time duration the routes do not hover anymore

**Diagnosis:** the hover watcher set `gd.__routeHover = true` and skipped if
already set. On a rerun Streamlit often **reuses the same plotly graph div** (just
updates its data), so the new run's watcher saw the flag, skipped re-binding, and
the *old* hover listeners kept closing over **stale hull data** from the previous
routes → hover stopped working (intermittently, depending on whether the div was
reused).

**Summary of changes:**

- **`app_pages/dashboard.py`** — the watcher now tracks the bound graph div in a
  per-run local (`boundGd`) instead of a persistent flag, and on (re)bind it
  **removes its previous `plotly_hover`/`plotly_unhover` listeners**
  (`gd.removeAllListeners`) before re-attaching with the fresh `HULLS`. Safe
  because Streamlit drives selection via `plotly_click`, not hover.
- **Verified with Playwright:** hover tooltip works on load *and* still works
  after switching the time range (All → 30 d). `uv run pytest` → 28 passed.

## 60. Route detail: pick which measures to plot

> on the route detail page i would like to be able to pick more values to show in the graph other than pm2.5

**Summary of changes:**

- **`app_pages/route.py`** — the trip chart is no longer hardcoded to PM2.5. Added
  a **Measures** multiselect (options from `available_metrics(table)`, default
  PM2.5) and load the device's time series over the trip's window
  (`load_timeseries(table, chosen, t_start, t_end+1s, clean=True)`). Selected
  measures are **grouped by unit**, and each unit gets its own `line_chart`
  (honest data — different units never share a misleading y-axis); a hidden-
  sentinel disclosure shows if any were cleaned. New imports: `available_metrics`,
  `load_timeseries`, `get`, `hidden_notice`, `timedelta`.
- **Verified with Playwright:** the route page shows the multiselect; adding a
  different-unit measure adds a second chart (2 → 3 plotly charts). `uv run
  pytest` → 28 passed.

## 61. Correlation page: adopt the Dashboard's tile-card design

> improve the design of the correlation page by adopting design choices from the main page. also the correlation should be inside a tile box like on the dashboard

**Summary of changes:**

- **`app_pages/correlation.py`** — reskinned the page to mirror the Dashboard
  cockpit's visual language while keeping the same data flow:
  - The verdict and the chart now each live in a **bordered `box_*` tile card**
    (`box_corr_verdict` / `box_corr_chart`), so they pick up the hub's white-card
    styling (`[class*="st-key-box_"]` in `app.py`) on the off-white canvas — the
    "correlation inside a tile box like on the dashboard" ask.
  - **Verdict hero** (mirrors the hub's hero): an icon+title header
    (`:material/compare_arrows: Relationship`, hint in a tooltip) over a
    `st.subheader` stating the strongest relationship in plain language, with
    `r`/`n` as gray badges. For 3+ measures the **strongest |r| pair becomes the
    focal hero** and the remaining pairs are listed beneath it (Mental Models:
    single focal point), instead of a flat equal-rank list.
  - **Chart tile** (mirrors a bento cell): icon+title header with the operating
    hint in a tooltip, and the **Scatter/Overlay** toggle moved to the top-right
    of the card (same placement as the hub's "Full map" action). Heatmap path for
    3+ measures gets its own `:material/grid_on: Correlation matrix` header.
  - **Skeleton-swap load**: both cards are painted as content-shaped skeletons
    (`box_corr_*_skel`) before the paired-readings query, then swapped in — the
    hub's no-layout-jump pattern. Standing prose trimmed to one orienting caption;
    hints live in tooltips.
- **`CLAUDE.md`** — noted the Correlation page now uses the hub's tile-card layout.
- **Verified with Playwright** (app running locally): 2-measure view renders the
  verdict tile ("No / weak link") + chart tile with the scatter; 3-measure view
  elevates the strongest pair ("↑ Strong positive", PM2.5↔PM10 r=+0.82) and shows
  the heatmap in its tile. `uv run pytest` → 28 passed; page compiles clean.

## 62. Dashboard: "Correlate" link from the PM-trend graph

> on the dashboard i want a button top right of the graph to link to the correlation page for the selected sensor on the dashboard

**Summary of changes:**

- **`app_pages/dashboard.py`** — the stationary **Particulate matter over time**
  card (`box_pmtrend`) now has a two-column header (title left, action right),
  with a **"Correlate"** button (`:material/scatter_plot:`, `key="ov_corr_link"`)
  top-right — same placement/pattern as the "Full map" button on the Location
  card beside it.
- Clicking it hands off to the **Correlation page focused on the current sensor +
  time window**: it sets `st.session_state["corr_sensors"]`/`["corr_range"]`
  directly, then `st.switch_page("app_pages/correlation.py", query_params={…})`.
  Setting the session keys is required because the Correlation picker only
  *seeds* from the URL when its key is unset — a return visitor would otherwise
  keep their old sensor (this is the established `hand_off_to_*` pattern). The
  query_params mirror keeps the URL a correct shareable link. The hand-off is
  checked before the (cached) time-series load so we don't fetch then navigate.
- Scoped to the **stationary** branch only (the mobile branch shows a route map,
  not a PM-over-time graph).
- **`CLAUDE.md`** — noted the PM-trend card's Correlate hand-off.
- **Verified with Playwright** (3 scenarios): (1) button present, click →
  `/correlation?corr_sensors=<B>&corr_range=…`; (2) **return-visitor override** —
  seeded Correlation with sensor A, then Correlate from the dashboard on sensor B
  switched to B (selectbox shows "SENSORpi s01"), proving the session-state set is
  necessary and works; (3) mobile sensor shows no Correlate button. `uv run
  pytest` → 28 passed.

## 63. Dashboard: "Load more" grows the readings table onto the page

> also the lazy loading for the data points is a bit weird because it just scrolls inside its box. i want the button load more to load them directly onto the page if you know what i mean

**Summary of changes:**

- **`app_pages/dashboard.py`** — the **Recent readings** `st.dataframe` (stationary
  view) now gets an explicit `height` sized to fit every loaded row
  (`(len(disp) + 1) * 35 + 3` — 35px/row + header), instead of Streamlit's
  default auto-height that caps at ~10 rows and then **scrolls inside a
  fixed-height box**. So "Load more" now extends the table (and the page itself)
  downward — the rows render directly onto the page, scrolled with the browser,
  not an inner scrollbar.
- **Verified with Playwright** (stationary sensor, range All): after one "Load
  more" the dataframe height grew by **exactly 875px** (= 25 rows × 35px), the
  page `scrollHeight` grew ~859px, and the grid's inner scroller reported **no
  internal scroll** before or after. `uv run pytest` → 28 passed; compiles clean.

## 64. Dashboard: subtle CAQI thresholds on the AQ meter + PM graph

> also, on the dashboard page the airquality thresholds should somehow be displayed in the "Air Quality: Good " bar and aswell in the graph, without overloading it. use very subtle neutral colors for this, maybe grey

**Summary of changes:**

- **`src/utils/aqi.py`** — new `caqi_pm_thresholds(pollutant)` returning the
  finite CAQI band-boundary concentrations paired with the band entered above
  each, e.g. PM2.5 → `[(15,"Low"),(30,"Medium"),(55,"High"),(110,"Very high")]`
  (the stepped form of the grid the band classifier already uses).
- **Meter (`src/components/meter.py` + `app.py` CSS)** — `air_quality_meter` now
  draws subtle neutral **`.aq-meter-tick`** marks at the band boundaries (default
  `ticks=(0.25, 0.5, 0.75)` — the three interior CAQI cut-offs / the bar's quarter
  points), so the red→green bar shows *where* Good/Fair/Moderate/Poor sit, not
  just the current dot. Quiet grey, theme-independent (the gradient is too); the
  dot still paints on top. Applies on the Dashboard and Route-detail heroes.
- **Graph (`src/components/charts.py`)** — `line_chart` gained a `band_guides`
  param: faint grey dotted `add_hline` reference lines drawn *under* the series,
  **filtered to the visible range** (guides ≤ data max, plus the nearest one
  above unless it'd squash the series) so a far band never stretches the axis.
  No on-chart labels (they clip in the 8px right margin and clutter) — the bands
  are disclosed in the chart-title tooltip instead.
- **`app_pages/dashboard.py`** — the stationary PM-trend chart passes
  `band_guides=caqi_pm_thresholds("pm2_5")`; the card tooltip (`_PM_HELP`) now
  states "Grey dotted lines mark the PM2.5 air-quality bands (CAQI): Low ≥15,
  Medium ≥30, High ≥55, Very high ≥110 µg/m³."
- **`tests/test_smoke.py`** — added `test_caqi_pm_thresholds_match_the_bands`
  (asserts the guide breakpoints equal the classifier's bands).
- **`CLAUDE.md`** — noted the meter ticks + PM band guides.
- **Verified with Playwright**: meter shows **3 ticks**; the PM chart draws **4
  band lines at 30 d** (peaks ~274) and **3 at 24 h** (the far "Very high" 110 is
  correctly filtered out, axis caps ~55) — range-adaptive, no axis blow-up.
  `uv run pytest` → 29 passed.

## 65. Threshold labels: zone words on the meter + per-pollutant chart bands

> they should also have a short description / title. in the bar above the thresholds it could be a little word like "Bad, Medium, Good" or whatever the threshold represents and for the graph we need the thresholds with a describtion to distinguish between pm2.5 and pm10 thresholds

**Summary of changes:**

- **Meter zone words** — `src/utils/aqi.py` adds `caqi_meter_zones()` →
  `[(centre, word)]` for the four visible zones (Good · Fair · Moderate · Poor,
  the CAQI quality words, matching the hero verdict; "Very poor" is off the 0-100
  scale). `air_quality_meter` (`src/components/meter.py`) gained a `zone_labels`
  param that prints them in small muted grey **above** the bar (new
  `.aq-meter-labels`/`.aq-meter-zone` CSS in `app.py`, theme-aware since they sit
  on the card, not the gradient). Wired on the Dashboard and Route-detail heroes.
- **Per-pollutant chart bands** — `line_chart`'s `band_guides` is now a list of
  `{"y", "label", "color", "dash"}` dicts. The Dashboard passes **both** PM2.5
  and PM10 CAQI bands (`_PM_BAND_GUIDES`), distinguished three ways so it's never
  colour-alone (colour-blind-safe): **colour** (PM2.5 orange / PM10 blue, matching
  each series), **dash** (PM2.5 dotted / PM10 dashed), and a **label**
  ("PM2.5 · High", "PM10 · Medium", …). Labels are **collision-avoided** (skipped
  when too close to the previous one; the line still draws) and the whole set is
  range-filtered (≤ data max + each pollutant's nearest band above), so wide
  ranges show more and short ranges stay clean. `_PM_HELP` tooltip updated.
- **`tests/test_smoke.py`** — `test_caqi_meter_zones_label_each_quarter`.
- **`CLAUDE.md`** — updated the meter + band-guide notes.
- **Verified with Playwright**: meter shows zone words **Good/Fair/Moderate/Poor**;
  the PM chart shows **8 labelled band lines at 30 d** (both pollutants, 6 labels
  after collision-avoidance) and **5 at 7 d**, colour+dash coded. `uv run pytest`
  → 30 passed.

## 66. Change the app font to Google Sans (Google Fonts API)

> Change the used font in this app to Google Sans using the google font api

**Summary of changes:**

- **`.streamlit/config.toml`** — set the base UI font to **Google Sans** the
  config-native way (no HTML injection, per CLAUDE.md):
  - `font = "Google Sans, sans-serif"` in `[theme]`.
  - Two `[[theme.fontFaces]]` tables loading Google Sans from the **Google Fonts
    API** (`fonts.gstatic.com/s/googlesans/v69/…`). Google Sans ships as one
    *variable* woff2 per Unicode subset (weight axis), so one face per subset
    (latin + latin-ext) with `weight = "400 700"` covers regular/medium/the 600
    heading weight. `unicodeRange`s copied from the official css2 output — latin
    covers µ/°/–/↑↓, latin-ext covers ń (e.g. "Gdańsk"); the ↔ arrow falls back
    to system sans-serif.
- **`CLAUDE.md`** — documented the Google Sans font + how to change it.
- **Note on the earlier typography inventory:** it claimed "Google Sans" was not
  on the public Google Fonts API — that was **wrong**. `css2?family=Google+Sans`
  returns 200 with a real variable font (family `'Google Sans'`, weights
  400/500/700, gstatic v69). Verified by fetching the API directly.
- **Verified with Playwright** (Streamlit restarted; config parsed with no
  fontFaces warnings): `document.fonts` registers **`Google Sans @400 700`**, and
  `document.fonts.check` is **true at 400, 600 and 700** (true weights, no faux-
  bold); computed `font-family` on body / title / hero / KPI value all start with
  **`"Google Sans"`**. Screenshot confirms the new letterforms; all glyphs
  (µg/m³, °C) render. `uv run pytest` → 30 passed.

## 67. Redesign the Devices & Data Quality page like the dashboard

> do a redesign of the devices and data quality page like you did before in
> reference to the styling of the dashboard page

**Summary of changes:**

- **`app_pages/devices.py`** — rebuilt the page to mirror the Dashboard cockpit
  (the same tile-card language used in the Correlation redesign), replacing the
  flat *4 metrics → divider → subheader → divider → …* stack:
  - **Verdict hero** (`box_dev_hero`): an `st.subheader` "the dataset at a
    glance" — total readings + active sensors — over coverage/span badges
    (`{span} · {n} of {N} registered logging`). The badges deliberately carry
    what the KPI strip does *not* (span + a coverage framing), not the raw
    per-category counts, so it reads as an executive summary, not a repeat.
  - **KPI strip**: the existing four counts (registered · with-data · no-table ·
    external) kept as bordered `st.metric` tiles, lifted directly under the hero.
  - **Content tile cards** (all bordered `box_*`, no more `st.divider()`s):
    `box_coverage` (data-availability timeline), `box_catalog` (the device
    dataframe), `box_quality` (saturation-sentinel table + the six known-issue
    expanders), `box_edit` (the metadata form). Each has an
    **`**:material/icon: Title**`** header with the operating hint moved into a
    **tooltip**; only honest-data disclosures ("counted, never silently dropped")
    stay on screen.
  - **Skeleton-swap loading** (the hub's pattern): hero + strip are whole-swapped
    from a content-shaped skeleton; the coverage/catalog/quality cards render
    their box+title immediately and skeleton only the data area until the loader
    resolves. The slow saturation-sentinel scan (`load_comparison` over every
    air-quality table) now shows a skeleton instead of the old `st.spinner`.
  - The edit **form is borderless** (`st.form(border=False)`) inside `box_edit`
    so the card isn't doubled; the device picker stays *outside* the form (so a
    new selection reloads the fields). All write-back logic is unchanged.
- **`CLAUDE.md`** — updated the Devices & Data Quality row in the Pages table to
  describe the cockpit-mirroring tile layout (`box_dev_hero` / `box_coverage` /
  `box_catalog` / `box_quality` / `box_edit`).
- **Verified with Playwright** (light + dark): no exceptions; all five `box_*`
  cards present; hero reads "548,450 readings from 9 active sensors · May 2023 –
  Dec 2025 · 6 of 40 registered logging"; the borderless edit form nests cleanly
  (no double card); cards get the elevated dark surface via the existing
  `light-dark()` CSS. `uv run pytest` → 30 passed.

## 68. Remove the data-quality audit and edit sections from Devices

> remove the  Known data-quality issues and  Edit device metadata section from
> this page

**Summary of changes:**

- **`app_pages/devices.py`** — deleted the two trailing tile cards:
  - **`box_quality`** ("Known data-quality issues" — the saturation-sentinel
    table + the six known-issue expanders).
  - **`box_edit`** ("Edit device metadata" — the device picker + write-back form).
  - Removed everything they alone used: the `_ISSUES` constant, the
    `from datetime import datetime` / `load_comparison` / `update_object` imports.
    The page now stops after the Device catalog card (hero → KPI strip →
    `box_coverage` → `box_catalog`).
  - Refreshed the module docstring + page caption (no more "honest data audit" /
    "quirks" framing) to match the slimmer catalog + coverage page.
- The `update_object` write API and the saturation-sentinel loaders are **left in
  `src/`** (unused by any page now), consistent with how the feature-flag helpers
  were kept after the IA consolidation.
- **`CLAUDE.md`** — updated the Devices row in the Pages table (cards now just
  `box_coverage` + `box_catalog`; write-back column → "—") and the Deployment
  write-back note (Settings is now the only page with a live edit surface).
- **Verified with Playwright**: no exceptions; `box_quality` and `box_edit` are
  gone; hero + KPI strip + coverage + catalog remain (4 metric tiles).
  `uv run pytest` → 30 passed.

## 69. Hidden Theme & Design System showcase page

> i need a subpage that is not reachable from the user interface that just
> basically visualizes the whole theme of the UI. can you create that

**Summary of changes:**

- **`app_pages/theme.py`** (new) — a hidden **Theme & Design System** page that
  visualises the live UI theme in bordered `box_theme_*` cards: base tokens
  (light + dark), the Okabe-Ito categorical palette + the config colorway,
  Viridis sequential, the CAQI band colours + the live air-quality meter +
  a thresholds table, the metric-registry colours, the full type scale + badges,
  and live components (KPI tiles via `metric_tile`/`aqi_tile`, buttons/segmented/
  select/slider/toggle, skeleton loaders, and a demo `line_chart` with area
  gradient + CAQI band guides). Everything is read **live** from the real
  sources, so it can't drift from what ships.
- **`app.py`** — registered the page in the `PAGES` dict with
  `visibility="hidden"` and icon `:material/palette:`, so it is **not in the nav
  rail** and is reachable only by URL at **`/theme`** (same mechanism as the
  hidden Route-detail page).
- **`src/utils/theme.py`** (new) — `theme_config()`, a pure read of the live
  `[theme]` block of `.streamlit/config.toml` (incl. `[theme.dark]`), so the page
  documents the actual tokens and stays I/O-free.
- **`src/components/charts.py`** — added `palette_swatches()` (a Plotly swatch
  grid: filled rectangles + hex labels) and `_text_on()` (WCAG-luminance pick of
  black/white label ink). Colour swatches go through the **chart layer**, not
  ad-hoc CSS — respecting the project's styling rule; the hex is always printed,
  so colour is never the only channel.
- **`CLAUDE.md`** — documented the new hidden page (file tree, Navigation note,
  Pages table), `theme_config()` in the utils list, and `palette_swatches` in the
  charts builder list.
- **Verified with Playwright** (light + dark): no exceptions; all 10
  `box_theme_*` cards render; 7 swatch grids + the demo chart draw; KPI tiles +
  themed controls + meter + thresholds table all correct; auto-contrast ink works
  (black on yellow, white on dark purple); **the page is absent from the nav rail**
  (`inNav: false`) yet loads at `/theme`. `uv run pytest` → 30 passed.
