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
