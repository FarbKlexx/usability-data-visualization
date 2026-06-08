# Informationsarchitektur-Neuordnung — Vorschlag (2. Konsolidierungsrunde)

> **Rolle:** Product-/UX-Architektur. **Auftrag:** keine Funktion erfinden
> oder streichen, sondern die *bestehende* Funktionalität so neu ordnen,
> dass das „all over the place"-Problem verschwindet.
> **Status:** reiner Vorschlag — es wurde **kein** Seitencode geändert.
> Umsetzung erst nach Freigabe (Stage-2), wie in der vorigen Runde.
> **Maßstab:** ausschließlich [`CONTEXT.md`](../CONTEXT.md). Jede
> Entscheidung unten ist namentlich auf ein dort genanntes Prinzip
> zurückgeführt.

---

## 0. Abgrenzung zur vorigen Runde

Die heutigen **6 Seiten** (Dashboard · Time Series · Map · Comparison ·
Devices & Data Quality · Manage) sind bereits das **Ergebnis** einer ersten
Konsolidierung (siehe [`consolidation_audit.md`](consolidation_audit.md)):
Overview + Correlation wurden in den Dashboard-Hub gefaltet (7 → 6 Seiten).

Dieser Vorschlag wiederholt jene Runde **nicht**. Er adressiert die
**Streuung, die danach übrig geblieben ist** — vor allem auf drei Ebenen,
die die erste Runde bewusst offen ließ:

1. die **Navigations-Taxonomie** (wonach sind die Top-Level-Seiten benannt/sortiert?),
2. die **verstreuten Schreib-/Konfigurationsflächen** (3 Seiten, 3 Muster),
3. die **Doppelung Hub ↔ Time Series** (der Hub baut die Unterseite teilweise nach).

---

## 1. Rubrik — die für *Anordnung* relevanten Prinzipien aus CONTEXT.md

Nur die Prinzipien, die über **Gruppierung, Auffindbarkeit und Konsistenz**
entscheiden (die per-Element-Rubrik der ersten Runde wird nicht wiederholt):

| Kürzel | Prinzip (CONTEXT.md) | Konkreter Test für die IA |
|--------|----------------------|----------------------------|
| **K1** | Shneiderman #1 *Konsistenz* / Nielsen #4 *Consistency & standards* | Gleiche Aufgabe → gleicher Ort, gleiches Bedienmuster, gleiche Begriffe/Icons |
| **K2** | Nielsen #6 *Recognition over recall* / Shneiderman #8 *Memory load* | Nutzer findet eine Funktion, ohne sich zu merken, „auf welcher Seite sie war" |
| **K3** | ISO 9241-110 *Erwartungskonformität* + *Mental Models* (Gulf of Execution) | Ort/Beschriftung passt zum mentalen Modell; klar erkennbar, wie man ans Ziel kommt |
| **K4** | *Split-Attention-Effekt* | Zusammengehörige Information räumlich zusammen, nicht über Seiten verteilt |
| **K5** | *Miller's Law (7±2)* | ≤ ~7 erfassbare Module pro Ansicht; Rest in Tabs/Drill-down |
| **K6** | *Hick's Law* / progressive disclosure | Wenige, **gruppierte** Optionen pro Ebene — auch im Navigationsmenü |
| **K7** | *Cognitive Load* / Nielsen #8 *minimalist* | Keine doppelte Pflege/Darstellung derselben Sache |
| **K8** | *Mental Models* (oben-links = Wichtigstes) / 5Es *Effective* | Die Kern-Antwort steht im Primärbereich, nicht hinter einem Tab |
| **K9** | ISO 9241-110 *Aufgabenangemessenheit* | Eine Seite dient *einer* Aufgabe; Lese- und Schreib-/Admin-Belange nicht vermischen |
| **K10** | 5Es *audience-weighting* / ISO 9241-11 *Kontext der Nutzung* | Laien-Monitoring zuerst; Experten-/Admin-Funktionen sekundär anordnen |

---

## 2. Analyse der Ist-Situation

### 2.1 Inventar (was es gibt, wo es liegt, Nutzungshäufigkeit)

| Seite | Funktionen / Informationselemente | Nutzung |
|-------|-----------------------------------|---------|
| **Dashboard** (Hub, Landing) | Geräte-Picker (typ-gruppiert) · Zeitbereich (`filter_bar`) · Klartext-CAQI-Status · **ein** Headline-Visual (PM-Trend + Mini-Standortkarte *oder* Routenkarte mobil) · Tab *Measures & data* (KPI-Reihe, Measures-Multiselect, raw/clean-Toggle, Linien-Charts je Einheit, CSV, „Open in Time Series") · Tab *Correlation* (verdict-first) · Tab *Routes* (nur mobil) · URL-State | **hoch** |
| **Time Series** | `filter_bar` · Measures-Multiselect · Aggregations-Bucket · Rolling-Average · raw/clean-Toggle · Linien-Charts je Einheit · Referenz-Thresholds · CSV · „Save view" · Annotations* · Raw-Inspector + Flags* · Particle-Drilldown* · URL-State | hoch (Tiefenanalyse) |
| **Map** | Layer-`pills` (stationär/mobil) · Vollkarte (CAQI-Marker + Tracks) · Details-on-demand (Selectbox **+ KPI-Reihe** + „Explore in Time Series") · **Standort bearbeiten** (Formular + Live-Vorschau) | mittel |
| **Comparison** | `filter_bar` (multi) · Measure-Selectbox (nur gemeinsame) · Tabs Averages/Distribution · CSV · „Show the numbers" | mittel |
| **Devices & Data Quality** | 4 Summary-Metriken · Coverage-Timeline · Geräte-Katalog (Tabelle) · Datenqualitäts-Audit (Sentinel-Tabelle + Prosa) · **Gerätemetadaten bearbeiten** (Formular) | niedrig–mittel |
| **Manage** | Feature-Flags (+ „other flags") · gespeicherte Thresholds (Liste + Formular) · gespeicherte Views (Apply/Delete) | niedrig (Admin) |

\* = feature-gated.

### 2.2 Problemkatalog (jeweils → verletztes Prinzip)

| # | Problem (die übrig gebliebene Streuung) | Verletzt |
|---|------------------------------------------|----------|
| **P1** | **Die Nav mischt drei Ordnungslogiken.** „Dashboard" = Ort, „Time Series"/„Map" = Diagrammtyp, „Comparison" = Aufgabe, „Devices & Data Quality" = Objekt+Anliegen, „Manage" = Verb. Der Nutzer kann nicht vorhersagen, wo eine Funktion liegt — die Wurzel des „all over the place". | **K1, K2, K3, K6** |
| **P2** | **Bearbeiten/Admin ist über 3 Seiten mit 3 Mustern verstreut.** Standort-Edit = Formular unten auf *Map*; Geräte-Edit = `st.form` unten auf *Devices*; Flags/Thresholds/Views = eigene *Manage*-Seite. „Ähnliches ist unterschiedlich gelöst" — wörtlich. | **K1, K2, K3, K9** |
| **P3** | **Die Aufgabe „eine Sensor-Messreihe ansehen" ist auf Dashboard *und* Time Series doppelt gebaut.** Der Dashboard-Tab *Measures & data* repliziert Measures-Auswahl + raw/clean + Linien-Charts je Einheit + CSV der Time-Series-Seite — leicht abweichend. Der Hub baut die Unterseite teilweise nach (entgegen der eigenen Hub-Leitidee „der Hub fasst zusammen, die Unterseite vertieft"). | **K7, K1, K5** |
| **P4** | **Der KPI-Snapshot wird an zwei Orten gerendert** (Dashboard-Tab + Map-Details), aus demselben Loader. Zwei „Heimaten" für dieselbe Antwort. | **K7, K4, K1** |
| **P5** | **Räumliche Info ist gespalten:** Einzelgerät-Standort/-Route im Dashboard; Flotten-Karte auf *Map*; mobile Tracks an **beiden** Orten gerendert. | **K4, K1** |
| **P6** | **Scoping (Sensor + Zeit) ist pro Seite anders gelöst.** `filter_bar` auf Dashboard/TS/Comparison; *Map* nutzt `pills` + separate Detail-Selectbox **und hat gar keinen Zeitbereich**; *Devices* hat kein Scoping. Das mentale Modell „wie wähle ich, was ich sehe" wird auf jeder Seite neu gelernt. | **K1, K3, K2** |
| **P7** | **Zwei parallele „Ansicht merken"-Mechanismen.** URL-Bookmarks (Dashboard, TS) **vs.** benannte DB-„Saved views" (in TS erzeugt, in Manage gelistet, Apply nur → TS). Gleiches Nutzerziel, zwei Systeme, keines deckt Map/Comparison. | **K1, K3** |
| **P8** | **„Devices & Data Quality" bündelt drei Aufgaben** — Referenz-Katalog (lesen), Vertrauens-/Ehrlichkeits-Audit (bewerten), Metadaten-Edit (schreiben) — nur weil alle das Wort „Gerät" teilen. Lese- und Schreibbelang vermischt. | **K9, K4** |
| **P9** | **Thresholds liegen weit weg von ihrer Wirkung.** Default-Thresholds werden in *Manage* gepflegt, wirken aber nur als Referenzlinien in *Time Series* (wo man zusätzlich Ad-hoc-Thresholds setzt). Die Beziehung „gespeichert (Manage) ↔ Referenzlinie (TS)" ist nicht selbsterklärend. | **K4** (Split-Attention), **K3** |
| **P10** | **Die wichtigsten Zahlen stehen hinter einem Tab.** Auf dem Monitoring-Hub liegt die KPI-Reihe im Tab *Measures & data*, nicht im Primärbereich. Ein Monitoring-Nutzer muss für „die aktuellen Werte" erst einen Tab öffnen. | **K8, K2** |

---

## 3. Neue Informationsarchitektur

### 3.1 Leitidee

> **Eine einzige Ordnungslogik: nach Nutzer-Aufgabe, nicht nach Diagrammtyp.**
> Konsistentes Scoping-Modell überall. **Genau eine** Heimat pro Antwort.
> Konfiguration/Edit nach **einer** durchgängigen Regel.

Daraus folgen drei Strukturmaßnahmen — alle **ohne** eine Seite zu löschen
oder Funktion auszulagern (Leitplanke „kein pauschales Auslagern"):

### 3.2 Maßnahme A — Navigation gruppieren & nach Aufgabe benennen *(löst P1)*

Statt einer flachen 6er-Liste mit gemischter Logik: **zwei beschriftete
Cluster** im Top-Nav (Streamlit `st.navigation` unterstützt benannte
Sektionen via Dict). Reihenfolge nach Häufigkeit/Wichtigkeit (**K10**:
Laien-Monitoring zuerst, Admin zuletzt):

```
 Air-Quality-Dashboard
 ── Beobachten & Analysieren ───────────────   (K6: gruppierte Optionen pro Ebene)
    • Dashboard        (Home, default)         ← „Wie ist die Luft gerade?"
    • Time Series                              ← „Verlauf, eine Station tief"
    • Map                                      ← „Wo stehen/fuhren die Sensoren?"
    • Compare                                  ← „Stationen/Messwerte vergleichen"
 ── Referenz & Einstellungen ──────────────────
    • Devices & Data Quality                   ← „Welche Geräte? Sind die Daten vertrauenswürdig?"
    • Settings   (vorher „Manage")             ← „App konfigurieren"
```

- Kein Seitenzu-/-abgang. Reine **Gruppierung + sprechende Reihenfolge** —
  der Nutzer sieht zwei Sinn-Cluster statt sechs gleichrangiger Begriffe
  (**K6 Hick**, **K2 Recognition**).
- **„Manage" → „Settings"** umbenannt: ein erwartungskonformes Wort für
  „App-Konfiguration" (**K3 Erwartungskonformität**).

### 3.3 Maßnahme B — Eine Regel für *alle* Schreib-/Konfig-Flächen *(löst P2, P9)*

Statt „3 Seiten, 3 Muster" eine **durchgängige, lernbare Regel**:

| Was | Wo | Begründung |
|-----|----|-----------|
| **Objekt bearbeiten, das man gerade sieht** (Standort auf Map, Gerätemetadaten im Katalog) | **bleibt im Kontext** — aber als **eine** einheitliche „Edit"-Affordanz (gleiches Popover/Expander, gleiche Wortwahl, gleiches ✓-Feedback) | *Direct Manipulation* + *Mental Models* („dort bearbeiten, wo man es sieht") — und **K1** durch Vereinheitlichung des Musters |
| **Objekt-unabhängige Konfiguration** (Feature-Flags, Default-Thresholds, Saved Views) | **eine Heimat: Settings** | **K9** (Lese-/Schreibtrennung), **K2** (ein erwartbarer Ort für „Einstellungen") |

Daraus die **eine Faustregel**, die der Nutzer einmal lernt
(**K3 Erwartungskonformität**, **Erlernbarkeit**):
*„Dieses Ding ändern → Edit am Ding. App-Defaults ändern → Settings."*

- **P9** mitgelöst: Auf der Threshold-Liste in Settings ein Satz +
  Verlinkung „wirkt als Referenzlinie in Time Series", und auf der
  TS-Threshold-Box ein Hinweis „Defaults in Settings" — die beiden
  Enden derselben Funktion werden sichtbar verbunden (**K4**).

> Hinweis Leitplanke: Es wird **nichts** vom Dashboard „weggeräumt".
> Standort-/Geräte-Edit lagen schon im Kontext und bleiben dort — nur ihr
> *Bedienmuster* wird angeglichen.

### 3.4 Maßnahme C — Doppelungen auflösen: eine Heimat pro Antwort *(löst P3, P4, P10)*

1. **KPI-Reihe in den Primärbereich des Dashboards heben** (raus aus dem
   Tab). Die aktuellen Werte sind die meistgescannte Antwort eines
   Monitoring-Hubs → gehören oben, nicht hinter einen Tab-Klick
   (**K8** oben-links/Primär, **K2**). *(P10)*
2. **Den Dashboard-Tab *Measures & data* zur echten Zusammenfassung
   zurückbauen:** KPI-Reihe (jetzt oben) + Headline-Visual + CSV des
   Gezeigten **behalten**; das *vollständige* Measures-Multiselect-/raw-
   /Mehr-Einheiten-Charting **entfällt auf dem Hub** und wird durch einen
   prominenten **„Open in Time Series →"** ersetzt — denn genau das macht
   Time Series bereits, besser. Das ist **Konsolidierung, kein Streichen**:
   jede Fähigkeit bleibt erreichbar (**K7**, Nielsen #8, **K5**). *(P3)*
3. **Map: KPI-Reihe der Details-on-demand auf einen CAQI-Badge + Link
   eindampfen.** Map beantwortet *„wo"*, nicht *„welche Zahl"*; die
   kanonischen Zahlen wohnen im Dashboard/Time Series (**K4, K7**). *(P4)*

### 3.5 Maßnahme D — Konsistentes Scoping & „Ansicht merken" *(löst P6, P7, P5)*

- **`filter_bar` überall, wo eine Ansicht eingegrenzt wird — inkl. Map**
  (mindestens Zeitbereich für Tracks; die Bar-Auswahl treibt die
  Details-on-demand). Ein einziges Scoping-Modell für die ganze App
  (**K1, K3, K2**). *(P6)*
- **Ein „Saved-view"-Mechanismus statt zwei.** Die DB-Saved-views (params
  als JSONB) um ein `page`-Feld erweitern, sodass auch Dashboard-/
  Comparison-/Map-Ansichten round-trippen; „Save view" von *jeder*
  Analyse-Fläche aus erreichbar, Apply routet zur richtigen Seite
  (**K1, K3**). *(P7)* — *mittlerer Aufwand, optional (siehe §6).*
- **Räumliche Info entzerren** *(P5)*: Die Mini-Standortkarte im Dashboard
  bleibt (Split-Attention: Kontext beim Gerät, **K4**), zeigt aber
  ausdrücklich nur das *gewählte* Gerät und verlinkt „Volle Karte →";
  die Flotten-/Tracks-Darstellung bleibt allein auf Map. Mobile Tracks
  werden damit nicht mehr in zwei Voll-Karten parallel gepflegt.

### 3.6 Wireframe — Dashboard (stationäres Gerät), neu

```
┌──────────────────────────────────────────────────────────────────┐
│ Air Quality · Dashboard                                            │ Titel
│ [ Device ▾ (typ-gruppiert) ]  [24h|7d|30d|All]        [↺ Reset]    │ ← filter_bar (K1, Fitts: Top-Edge)
│ 🟦 s01 · Minden   🕓 7 d   📅 2025-… → 2025-…                       │ ← aktive Filter als Chips (K2 Memory-Relief)
├──────────────────────────────────────────────────────────────────┤
│ PRIMÄR  (auf einen Blick · oben-links = die Antwort, K8)           │
│ ┌────────────────────────────────────────────────────────────┐    │
│ │ 🟢 Luftqualität: Gut   [CAQI: niedrig]  PM klar im grünen … │    │ ← Klartext-Status (Match real world)
│ └────────────────────────────────────────────────────────────┘    │
│ ┌──────────── ein Headline-Visual ───────────┐  ┌──────────────┐  │
│ │ PM2.5 / PM10 im Verlauf  (drag-zoom)        │  │ Standort 🗺️   │  │ ← Trend + Mini-Karte (K4)
│ └─────────────────────────────────────────────┘  │ „Volle Karte→"│ │
│ [ PM2.5 ][ PM10 ][ CO₂ ][ Temp ][ Hum ][ CAQI ]  └──────────────┘  │ ← EINE kanonische KPI-Reihe (≤7, K5)
├──────────────────────────────────────────────────────────────────┤
│ SEKUNDÄR  (progressive disclosure · Tabs, K6)                      │
│ [ Correlation ]  [ Routes* ]                  [ Open in Time Series→]│ *Routes nur mobil
│  … verdict-first Correlation (Wort + Farbe + Vorzeichen) …          │ ← „Compare sensors →" Querverweis
└──────────────────────────────────────────────────────────────────┘
```

Primärbereich = **4 erfassbare Module** (Status · Headline-Visual · Mini-Karte ·
KPI-Reihe) → **K5 (7±2) erfüllt**. Die meistgebrauchte Antwort (Status + Zahlen)
steht jetzt *vor* den Tabs (**K8**).

### 3.7 Wireframe — Settings (vorher „Manage")

```
Settings
 ── App-Module ──────  Feature-Flags (einheitliche Toggles; „other flags" im Expander)
 ── Defaults ────────  Gespeicherte Thresholds  ·  Hinweis+Link: „wirkt in Time Series"   (löst P9)
 ── Gespeicherte Ansichten ──  Liste · Apply (routet zur jeweiligen Seite) · Delete        (P7)
```

Kontext-Edits (Standort/Map, Gerät/Devices) bleiben an ihrem Objekt, je mit
Mini-Hinweis „App-Defaults in Settings".

---

## 4. Entscheidungslog

| # | Was ändert sich | Warum (CONTEXT.md-Prinzip) | Gelöstes Problem | Trade-off |
|---|-----------------|----------------------------|------------------|-----------|
| D1 | Nav in 2 benannte Cluster gruppieren, nach Häufigkeit sortieren | **K6** Hick, **K10** audience-weighting, **K2** Recognition | P1 | Minimal: leichte Mehrhöhe im Menü |
| D2 | „Manage" → **„Settings"** | **K3** Erwartungskonformität | P1 | Einmalige Umgewöhnung des Namens |
| D3 | **Eine Edit-Regel**: Objekt-Edit im Kontext (einheitlich), App-Config in Settings | **K9** Lese/Schreib-Trennung, **K1** Konsistenz, *Direct Manipulation* | P2, P9 | Kontext-Edits müssen auf **ein** gemeinsames Affordanz-Muster vereinheitlicht werden (Implementierungsarbeit) |
| D4 | KPI-Reihe in den **Primärbereich** des Dashboards | **K8** oben-links, **K2** | P10 | Primärbereich +1 Modul (bleibt ≤7) |
| D5 | Dashboard-Tab *Measures & data* auf **Zusammenfassung + „Open in TS"** zurückbauen (volles Multi-Measure-Charting nur noch in TS) | **K7** Cognitive Load, Nielsen #8, **K5** | P3 | Ad-hoc-Mehr-Measure-Chart auf dem Hub kostet 1 Klick mehr (→ TS). *Konservative Alternative:* Tab behalten, aber Bedienung 1:1 an TS angleichen |
| D6 | Map-Details: KPI-Reihe → **CAQI-Badge + Link** | **K4, K7** | P4 | Volle Zahlen auf Map = 1 Klick entfernt (Map = „wo") |
| D7 | **`filter_bar` auch auf Map**; ein Scoping-Modell | **K1, K3** | P6 | Map bekommt ein bisher fehlendes Zeit-Control (eher Gewinn) |
| D8 | **Ein** Saved-view-System (page-aware), von überall, Apply routet korrekt | **K1, K3** | P7 | Mittlerer Aufwand (Schema-Feld + Routing) — optional |
| D9 | Querverweise statt Verschmelzung: Correlation-Tab ↔ Compare-Seite verlinken | **K2** Recognition, Leitplanke „nicht über-kollabieren" | (P1-Begleitend) | Zwei Geschwister-Aufgaben bleiben getrennt, aber sichtbar verbunden |

---

## 5. Begründung der Verteilung (Dashboard vs. Unterseiten)

Leitplanke: **kein pauschales Auslagern.** Prüfung — was bleibt direkt auf
dem Dashboard, was bleibt Unterseite, *und warum ist das keine Ausräum-Aktion*:

**Bleibt direkt auf dem Dashboard** (die Monitoring-Antwort + die zwei
häufigsten Drill-downs inline): Klartext-Status, Headline-Visual,
Mini-Standortkarte, **KPI-Reihe** (neu im Primärbereich), Correlation-Tab,
Routes-Tab (mobil). Das Dashboard bleibt ein **echtes, bedienbares
Dashboard** — die wichtigen Dinge sind sicht- und bedienbar (Leitplanke).

**Bleibt Unterseite** — jede gegen die Leitplanke geprüft (Unterseite nur
gerechtfertigt bei *selten/sekundär/zu umfangreich*):

| Unterseite | Warum eigenständig (nicht „weggeräumt") |
|------------|------------------------------------------|
| **Time Series** | *Zu umfangreich* für den Hub (Aggregation, Rolling-Avg, Thresholds, Annotations, Flags, Particle-Drilldown). Distinkte Tiefenaufgabe — **K9, K5**. War nie auf dem Hub. |
| **Map** | *Distinkte Aufgabe* „Flotte im Raum". Voll-Karte + Tracks sprengen den Hub-Platz — **K5**. |
| **Compare** | *Distinkte Aufgabe* (multi-Sensor, ein Maß). Eigener Multi-Select-Flow — **K9**. |
| **Devices & Data Quality** | *Referenz + Vertrauens-Audit*, selten im Monitoring-Alltag — **K10**. (Intern in *Katalog* / *Datenqualität* zonen, Edit als Kontext-Affordanz — **K9**.) |
| **Settings** | *Selten/Admin*, objekt-unabhängige Konfiguration — gehört bewusst **nicht** in den Laien-Blick (**K10**). |

**Wichtig:** Dieser Vorschlag **schiebt nichts Neues** auf Unterseiten, um
den Hub aufzuräumen. Bewegt wird nur: (a) ein **Duplikat** (Hub-Charting →
existiert schon in TS, D5), (b) eine **Doppel-Heimat** (Map-KPIs → eine
Heimat, D6), (c) ein **Bedienmuster** (Edits vereinheitlicht, D3). Das sind
*Konsolidierungen*, keine Auslagerungen.

---

## 6. Offene Fragen / Annahmen / CONTEXT.md-Lücken

**Annahmen** (explizit, statt still getroffen):
- **A1 — Primärpublikum = Laie/Öffentlichkeit (Monitoring), sekundär
  Betreiber/Admin.** Stützt sich auf CLAUDE.md („lay-facing dashboard") und
  den Klartext-Status. Per **5Es / ISO 9241-11 (Kontext der Nutzung)**
  bestimmt diese Gewichtung die ganze Reihenfolge (K10). *Falls falsch
  (z. B. Experten-/Betreiber-Tool zuerst), ändert sich die Cluster-/
  Reihenfolge — bitte bestätigen.*

**Lücken in CONTEXT.md** (laut Auftrag benannt, nicht überspielt):
- **L1 — CONTEXT.md regelt die *globale Navigationstaxonomie* nicht
  explizit.** Es nennt Miller (≤7 Module **pro Ansicht**) und Hick
  (gruppierte Optionen **pro Ebene**), aber keine Regel für *Anzahl/Benennung
  der Top-Level-Ziele*. Maßnahme A (Nav-Gruppierung) **überträgt** Miller/Hick
  per Analogie auf die Menü-Ebene — eine begründete Erweiterung über den
  wörtlichen Text hinaus, hiermit offengelegt.
- **L2 — „Edit im Kontext vs. zentral" ist in CONTEXT.md nicht entschieden.**
  *Direct Manipulation* spricht für Kontext-Edit, *Konsistenz/K9* für eine
  Heimat. Maßnahme B löst das per Hybrid-Regel; das ist eine Abwägung, kein
  Zitat.

**Entscheidungs-Fragen an dich:**
- **F1 — Liefergegenstand:** nur dieser Vorschlag (wie Stage-1 zuvor), oder
  soll ich nach Freigabe die Umsetzung bauen (Stage-2)?
- **F2 — Frühere „locked decisions" revidieren?** D5 (Hub-Charting) und D6
  (Map-KPI-Reihe, vorher bewusst als *C2* behalten) kehren frühere
  Entscheidungen um. OK?
- **F3 — Umfang von D8** (vereinheitlichte Saved-views, mittlerer Aufwand)
  in dieser Runde, oder zurückstellen?
