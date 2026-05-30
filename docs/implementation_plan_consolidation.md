# Implementation Plan — Consolidation & Dashboard-as-Hub (Cleanup Phase)

> **Companion to** the baseline, interactivity, and correlation-graph plans, all
> of which are implemented and deployed. The dashboard has grown organically:
> each new feature tended to land on its own subpage, so functionality is
> scattered and the entry view says little. This phase reverses that. Goal: a
> **single dashboard that works as the central point** of the whole app, is
> immediately understandable to a non-expert, and pulls the important signals up
> from the subpages. Scope is structural and functional; visual polish comes
> after.

### Locked decisions

- **Consolidation depth:** moderate — **keep the subpages**, add the dashboard as a hub layered on top of them (no aggressive collapse).
- **Pull up first:** **KPIs (current values)**, **correlation**, and the **headline trend** (time series).
- **Lay-audience correlation verdict:** simple **strength banding by |r|** (weak / moderate / strong), no p-values.

---

## 0. Guiding idea

Two shifts:

1. **From scattered pages to a hub.** The dashboard stops being just an
   "Overview" among equals and becomes the place that answers the app's core
   question at a glance, surfacing the key values that currently hide on
   subpages.
2. **From scientific to plain-language.** Every element should tell a non-expert
   *what they are looking at and what it means* before it shows them detail.
   Worded results and color-coded verdicts come first; the chart supports them,
   not the other way around.

The phase runs in two stages on purpose: an **audit that only proposes** (no code
changes), which the user approves, then the **implementation** of the approved
subset. This keeps deletion and restructuring decisions with the user.

**`CONTEXT.md` is the standard for this whole phase.** Before auditing or
changing anything, the agent re-reads `CONTEXT.md` (the full usability context
from the lecture) and treats it as the explicit checklist for every decision —
not just a final glance, but the lens through which each page is judged: what
belongs on a page, how things are grouped, where each element is placed, and
whether a view stays within a glanceable number of modules.

---

## A. Stage 1 — Audit & consolidation proposal (no code changes yet)

The agent inventories the current app and produces a written proposal. Concretely
it should:

0. **Re-read `CONTEXT.md` first** and restate the concrete usability criteria it
   will judge against (grouping, placement, module count per view, color +
   label, reset reachability, honest data, etc.). This list is the rubric for
   everything below.
1. **List every page** and, per page, every widget/feature it currently holds,
   plus which data loader feeds it.
2. **Audit every page against `CONTEXT.md`** — go through the dashboard *and
   each subpage* individually and check, per page: are related things grouped
   together? Is each element placed where the principles say it should be (most
   important top-left, time on the X-axis, etc.)? Does the view stay within a
   glanceable number of modules? Is color paired with a label/shape? Is reset
   reachable? Note concrete deviations per page.
3. **Classify each feature** as one of:
   - *core* — needed for the app's main purpose,
   - *supporting* — useful but secondary,
   - *redundant* — duplicated elsewhere or low value.
4. **Map duplication and sprawl:** where do two pages do nearly the same thing?
   Which pages exist only to host a single small feature?
5. **Propose a target structure:** since the subpages are kept (moderate
   consolidation), the proposal focuses on the **dashboard as a hub layered on
   top** — which features stay where they are, which get *summarized* on the
   dashboard with a link through, and which genuinely redundant bits can be
   dropped or merged. Pages are not collapsed wholesale. Every placement and
   grouping choice in the proposal is justified by reference to `CONTEXT.md`.
6. **For each proposed removal/merge, state the trade-off** in one line (what is
   lost, why it is acceptable).

Output is a short written proposal (a markdown file or a section the user
reviews). No files are edited in this stage. The user picks which proposals to
apply before Stage 2.

> Guardrail: the agent does not delete or rewrite pages in Stage 1. It reads,
> classifies, and proposes. Removal happens only after approval.

---

## B. Stage 2 — The dashboard as central hub

Once the structure is approved, rebuild the dashboard so it answers the core
question first and carries the most important values from the subpages.

### B1. Top: plain-language status
The first thing visible is a worded summary, not a chart. For example, per
active sensor: the current air-quality state in words ("air quality: good") plus
the EU-CAQI category, derived via the existing `aqi.py`. A non-expert should
understand the situation without reading an axis.

### B2. Key values pulled up from subpages
The dashboard surfaces the signals that currently require visiting a subpage.
Pull up these three first: the **latest KPIs** (current values), the **headline
trend** (time series), and the **correlation** feature (see B3). Each pulled-up
value links through to its full subpage for detail — the hub summarizes, the
subpage expands. The subpages themselves stay in place (moderate consolidation).

### B3. Correlation lives on the dashboard, plain-language first
Fold the correlation feature into the dashboard instead of a standalone page,
and re-order it so the answer precedes the chart:

1. The user picks **two or more measures** to compare (e.g. PM2.5 and
   temperature).
2. Immediately below the picker, a **color-coded verdict** per pair, based on a
   simple **strength banding of the correlation coefficient |r|**: e.g.
   *no/weak* (|r| < 0.3), *moderate* (0.3–0.7), *strong* (> 0.7), with the sign
   indicating positive vs. negative. Each band is shown with both a color **and**
   a word/label so the meaning is clear without relying on color alone. No
   p-values — the banding is the lay-friendly reading. (Cutoffs are a starting
   point; adjust if needed.)
3. **Only then** the supporting chart (scatter or overlay from the existing
   correlation plan). The chart is the evidence under the verdict, not the
   headline.

This reuses `compute_correlation`, `build_comparison_frame`, and the rendering
modes already built; the change is ordering (verdict first) and placement
(dashboard, not its own page).

### B4. Replace-in-place behavior
The correlation chart on the dashboard occupies one slot and swaps its content
based on the user's measure selection — it replaces what is shown rather than
adding more charts. The dashboard's module count stays small.

---

## C. Plain-language principles to apply throughout

- Lead with a worded result or status; put the chart underneath as support.
- Color-coded verdicts always carry a word/label too, so the meaning survives
  for color-blind readers and for anyone skimming.
- Prefer one clear value or sentence over a dense panel of numbers.
- Keep the dashboard's modules few enough to take in at a glance.

---

## D. Build order

1. **Stage 1 audit** → re-read `CONTEXT.md`, audit the dashboard and every
   subpage against it (grouping, placement, module count, color+label, reset),
   then produce the written proposal (feature classification, target structure,
   trade-offs). User approves a subset.
2. **Hub status (B1)** → plain-language state + CAQI category at the top of the
   dashboard.
3. **Pull-up values (B2)** → surface subpage KPIs/trends on the dashboard, each
   linking through.
4. **Correlation inline (B3, B4)** → move correlation onto the dashboard,
   verdict-first, replace-in-place.
5. **Apply approved removals/merges** → collapse or drop the pages the user
   signed off on; update `app.py`'s `PAGES` list accordingly.
6. **Pass over the result** for the plain-language principles in §C.

Each step is a self-contained, documentable prompt, matching the structured
workflow used so far.

---

## E. Settled

All three open questions are now decided (see "Locked decisions" at the top):
moderate consolidation (subpages kept, dashboard as hub on top); pull up KPIs,
correlation, and the headline trend first; and a lay-friendly correlation
verdict via |r| strength banding (weak / moderate / strong), no p-values. The
only thing left to tune during implementation is the exact |r| cutoffs, which
the agent can surface for a quick confirmation if the defaults in B3 feel off.
