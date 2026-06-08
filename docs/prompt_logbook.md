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
