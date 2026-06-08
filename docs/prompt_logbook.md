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
