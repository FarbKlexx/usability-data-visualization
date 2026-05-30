# Project Context for Coding Agent

## Usability — Definition & Goals (ISO 9241-11)

- **Usability =** the extent to which specified users achieve specified goals with **effectiveness, efficiency, and satisfaction** in a specified **context of use** (ISO 9241-11).
  - **Effectiveness** — can the user reach the goal at all (accuracy & completeness)?
  - **Efficiency** — does the user reach it with minimal effort/resources?
  - **Satisfaction** — does the user reach it comfortably, without frustration?
- **Context of use** = users + goals + tasks + resources + environment. Design for *our* users and *their* context — know who they are before deciding what to show.
- **useful = utility + usability** (Nielsen). Utility = does it have the features the user needs; usability = how easy/pleasant those features are to use. A feature that exists but is unusable is worthless; an easy UI for the wrong feature is equally worthless.
- **Usability ≠ UX.** Usability is effectiveness/efficiency/satisfaction *during* a task. **User Experience (UX)** is the whole perception **before, during, and after** use — emotions, trust, aesthetics, brand. Good usability is necessary but not sufficient for good UX.
- **Nielsen's 5 quality components:** Learnability, Efficiency, Memorability, Errors (few, recoverable), Satisfaction.

## User-Centered Design (Process)

- Base design on an explicit understanding of **users, tasks, and environments**; involve users throughout; refine via user-centered evaluation; iterate.
- **Iterate:** design → test → revise, at every step. Test early — deferring tests to the end makes structural problems unfixable.
- **~5 users** per test round typically surfaces the most important problems; many small tests beat one big study.
- **You are not the user.** Consistent problems are the system's fault, not the user's — but users aren't designers either, so observe behavior rather than only asking.
- **User testing ≠ focus groups.** Testing observes whether something *works*; focus groups only reveal what people *say* they want.

## Cognitive Foundations

- **Miller's Law (7±2):** Working memory is limited. Don't display more than ~7 KPIs/widgets at the same time. Logical chunking (grouping related metrics) is mandatory.
- **Cognitive Load Theory:** Minimize extraneous load (design noise) — remove anything that doesn't contribute to data analysis. No chart junk, no decorative 3D effects.
- **Split-Attention Effect:** Keep related information spatially together. Place legends directly on/in the chart, not in a separate column. Tooltips instead of distant tables.

## Perception & Color

- **~8% of men have a color vision deficiency** — never use color as the only carrier of information. Additionally employ shape, pattern, label, or position.
- **Sensitivity to blue is the lowest** — don't use blue for fine details or small text.
- **Negative contrast** (light text on dark) can be more readable on screens — offer dark mode as an option.
- Use colors sparingly per chart; categorical palettes ≠ sequential ≠ diverging.

## Shneiderman's 8 Golden Rules (for every interaction)

1. Consistency (same actions → same reactions, uniform terms/icons)
2. Universal usability (novices and power users; keyboard shortcuts)
3. Informative feedback (every filter, every click must visibly take effect)
4. Closure (actions have a clear beginning/end — "Filter applied ✓")
5. Error prevention (validation, sensible defaults, range limits)
6. Easy reversal of actions (undo, "Reset filter", bookmarks)
7. User in control (no auto-reload in the middle of an analysis)
8. Reduce short-term memory load (show active filters visibly, don't require them to be remembered)

## Nielsen's 10 Usability Heuristics

Companion to Shneiderman's 8 above — broader rules of thumb; several overlap (mapping noted where useful).

1. **Visibility of system status** — show state clearly and quickly (≈ Shneiderman #3).
2. **Match the real world** — users' language and familiar concepts.
3. **User control & freedom** — undo, redo, cancel; clearly marked exits (≈ #6).
4. **Consistency & standards** — follow conventions, stay uniform (≈ #1).
5. **Error prevention** — stop problems before they happen (≈ #5).
6. **Recognition over recall** — make options visible; don't force memory (≈ #8).
7. **Flexibility & efficiency** — shortcuts and customization for power users (≈ #2).
8. **Aesthetic & minimalist design** — show only what's necessary.
9. **Help users recognize, diagnose, recover from errors** — plain-language message + a concrete solution.
10. **Help & documentation** — easy to find, concise, task-focused.

## ISO 9241-110 Interaction Principles

Seven dialogue principles that underpin usable interaction:

- **Task appropriateness** (Aufgabenangemessenheit) — supports the task without unnecessary steps.
- **Self-descriptiveness** (Selbstbeschreibungsfähigkeit) — at each point it is clear what is happening and what to do next.
- **Conformity with expectations** (Erwartungskonformität) — consistent with conventions and the user's mental model.
- **Learnability** (Erlernbarkeit) — easy to learn and to re-learn after a break.
- **Controllability** (Steuerbarkeit) — user can start, pause, reverse, and direct the interaction.
- **Robustness against use errors** (Robustheit gegen Benutzungsfehler) — tolerant; helps avoid and recover from mistakes.
- **User engagement** (Benutzerbindung) — motivating, trustworthy, pleasant to use.

## The 5Es of Usability (Quesenbery)

- The five dimensions: **Effective, Efficient, Engaging, Error-tolerant, Easy to learn.**
- **Weight them by audience:** occasional/lay users prize *easy to learn, error-tolerant, engaging*; expert/frequent users prize *effective, efficient*. For a lay-facing dashboard, lean toward easy-to-learn and error tolerance without sacrificing effectiveness.

## Direct Manipulation

- Data objects directly manipulable (drag on axis to zoom, click on legend to hide, brushing between linked charts).
- Immediate, incremental, reversible feedback on every interaction.

## Fitts' Law (Size & Position)

- Click targets large enough — minimum **44×44 px** for touch (finger width 10–14 mm).
- Place frequent actions close to where the cursor is expected.
- Use screen edges as "infinite targets" (e.g., global toolbar at top/side).
- Sufficient padding between buttons — no crowding.

## Hick's Law (Decision Time)

- Few, well-grouped options per level. Prefer progressive disclosure over 20 filters at once.
- Make filters visible only when relevant (Google pattern: search first, then filter).

## Mental Models & Metaphors

- Use established conventions: top-left corner = most important/first piece of information; time = X-axis from left to right; red = negative, green = positive (but see color blindness).
- Avoid the Gulf of Execution: it must be clearly recognizable how to reach the goal (visible affordances, no hidden gestures).
- Avoid the Gulf of Evaluation: always communicate system state (loading, filter active, error) unambiguously.

## Modern Ergonomics

- **Responsive / Mobile First:** Layout must work on phone, tablet, and desktop.
- **Sweet Spot:** Core content centered, secondary actions at the edges.
- **Microinteractions:** Hover states, smooth transitions when filtering (understandable feedback, no jumping).
- No purely gesture-based interactions without a visible alternative.

## Aesthetics & Emotion

- **Aesthetic-Usability Effect:** Clean, calm design increases perceived usability — but never at the cost of function.
- **White space is function**, not waste.

## Ethics (Avoid Dark Patterns)

- No hidden defaults that manipulate data (e.g., truncated Y-axes that exaggerate trends).
- Filter reset must be easily reachable (no "Roach Motel").
- Represent data honestly — no misleading scales or axis breaks without a notice.

## Accessibility — WCAG 2.2 (POUR) & Legal Requirements

- **POUR — the four WCAG 2.2 principles:**
  - **Perceivable** — content must be graspable by the senses; text alternatives for non-text content; don't rely on a single sense (pairs with "color is never the only channel").
  - **Operable** — everything reachable by keyboard; enough time; no interaction that is impossible for some users.
  - **Understandable** — plain language; predictable behavior; helpful error messages.
  - **Robust** — standards-compliant markup that works with current and future assistive tech (screen readers).
- **Curb-cut effect** — accessible design improves usability for *everyone* (captions in noisy rooms, high contrast in sunlight). Accessibility is not an add-on bolted on at the end.
- **Legal mandate (DE/EU):** EU directives 2016/2102 and 2019/882 (European Accessibility Act) → national **BITV 2.0** (public bodies) and **BFSG** (products/services on the German market must be accessible). **EN 301 549** is the technical conformance checklist; meeting it gives presumption of conformity. Non-compliance can mean fines up to a sales ban.
- **Bottom line:** good usability *begins* with accessibility — without it there is no good usability.

### Accessibility Checklist (WCAG 2.2)

1. Full keyboard operability with a visible focus indicator.
2. Text alternatives / ARIA labels for every non-text control and every chart.
3. Sufficient color contrast; never color-only signaling (also pattern/label/text/position).
4. Predictable, consistent navigation and behavior across all pages.
5. Plain-language labels and error messages that include a suggested fix.
6. Standards-compliant markup that screen readers can parse.

## Practical Checklist for the Coding Agent

1. Consistent component library (same buttons, inputs, cards everywhere)
2. Colorblind-safe color palette (e.g., Viridis, Okabe-Ito) + patterns/labels as backup
3. Min. 44×44 px touch targets, sufficient padding
4. Loading / empty / error states for every widget
5. Filters visible, reset easy, default state defined
6. Tooltips for all data points, axes clearly labeled, units named
7. Responsive grid, mobile-first testing
8. Keyboard navigation and ARIA labels (accessibility)
9. At most ~7 main modules per view, rest in drill-down/tabs
10. Every action gives feedback in <100 ms
