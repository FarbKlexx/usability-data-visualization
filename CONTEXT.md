# Project Context for Coding Agent
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