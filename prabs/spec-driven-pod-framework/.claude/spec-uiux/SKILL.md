---
name: spec-uiux
description: "Create, review, and update the UI/UX design specification (specs/ui-ux.md) for a program. Activate whenever the user says 'update UI spec', 'define design system', 'set up components', 'choose colors and fonts', 'define buttons and inputs', 'update ui-ux spec', 'review UI components', 'define transitions', 'set up the design language', or"
---

**name:** spec-uiux

**description:** Create, review, and update the UI/UX design specification (specs/ui-ux.md) for a program. Activate whenever the user says "update UI spec", "define design system", "set up components", "choose colors and fonts", "define buttons and inputs", "update ui-ux spec", "review UI components", "define transitions", "set up the design language", or makes any decision about visual design, component behavior, typography, color palette, spacing, iconography, motion, or accessibility standards. This spec is created once and reused across all features — it is the single source of truth for visual and interaction consistency. Always read specs/program.md and specs/design.md first.


# Spec: UI/UX

## Purpose

Define and maintain the **UI/UX design specification** — the component library, design tokens, interaction patterns, and accessibility standards that govern every user-facing surface in the program. This spec is **created once and shared across all features and pods**; it prevents visual inconsistency and redundant design decisions.

`specs/ui-ux.md` is consumed by:
- Frontend pod coding sessions
- All feature brief sessions (for acceptance criteria on UI behavior)
- `spec-api` skill (to align response shapes with UI component needs)

---

## Pre-flight

### Step 0 — Client UX Reference

Check `context/` for any file named `ux-reference.*` (accepts `.md`, `.css`, `.pdf`, `.png`, `.jpg`, or any image format).

**If found:** Read or interpret it — extract design tokens (colors, typography, spacing), component styles, and interaction patterns. Present a summary to the user:

```
## UX Reference Detected — context/ux-reference.[ext]

Colors:       [inferred primaries, neutrals, semantic colors or "not specified"]
Typography:   [inferred font families, scale or "not specified"]
Spacing:      [inferred base unit or "not specified"]
Components:   [inferred button/input/nav styles or "not specified"]
Other:        [any other inferred design decisions]

Confirm these or tell me what to change before I proceed.
```

Wait for confirmation. Skip elicitation questions for any group already answered. Only ask about gaps.

**If not found:** Ask once — *"Would you like to provide a UX reference file in `context/` before we proceed? This can be a document, CSS file, Tailwind config, or design image. (Yes / No)"*
- **Yes** → wait for the user to drop the file or paste content, then process it as above.
- **No** → proceed with full elicitation questions below.

---

### Steps 1–3

1. Read `specs/program.md` — extract target users, devices, accessibility NFRs, design highlights
2. Read `specs/design.md` if it exists — extract frontend framework, styling library, component approach
3. Check if `specs/ui-ux.md` exists — if yes, **Review Mode**; if no, **Initialize Mode**

---

## Initialize Mode

Elicit in five groups:

### Group 1 — Design Language & Tokens
- Is there an existing brand guide or design system to inherit from? (Figma link, Storybook, Tailwind config?)
- **Color palette:** Primary, secondary, neutral, semantic (success/warning/error/info) colors?
- **Typography:** Font family (heading, body, mono)? Scale (xs → 4xl)? Line height defaults?
- **Spacing system:** Base unit (4px, 8px)? T-shirt sizes or numeric scale?
- **Border radius:** Sharp, slightly rounded, or pill-style components?
- **Elevation / shadows:** How many levels? When used?

### Group 2 — Core Components
For each of the following, capture variant list, states, and sizing:
- **Buttons:** Primary, secondary, ghost, destructive? Sizes? Loading/disabled states?
- **Inputs & Forms:** Text input, textarea, select, checkbox, radio, toggle? Error/focus/disabled states?
- **Navigation:** Tab bar, bottom nav, top nav, drawer, breadcrumbs?
- **Feedback:** Toast/snackbar, modal/dialog, loading spinner, skeleton screens, empty states?
- **Data display:** Tables, cards, badges, tags, avatars?

### Group 3 — Motion & Transitions
- **Transition philosophy:** Subtle and functional vs expressive and branded?
- **Duration scale:** Fast (100ms), normal (200ms), slow (400ms)?
- **Easing:** Standard curves (ease-in-out, spring)?
- **Page transitions:** Slide, fade, none?
- **Micro-interactions:** Button press feedback, input focus, list item tap?

### Group 4 — Layout & Responsive Behavior
- **Grid system:** Columns (4/8/12), gutters, margins?
- **Breakpoints:** Mobile / tablet / desktop thresholds?
- **Touch targets:** Minimum size (48×48px recommended)?
- **Safe areas:** iOS notch / Android nav bar handling?

### Group 5 — Accessibility & Internationalization
- **WCAG level:** AA (default) or AAA?
- **Focus management:** Visible focus rings, focus trap in modals?
- **Screen reader:** ARIA labels, roles, live regions strategy?
- **RTL support:** Required now or future?
- **Language/locale:** Date formats, number formats, currency display?

---

## Review Mode

1. Load current `specs/ui-ux.md`
2. Scan for: missing component states, outdated color values, accessibility gaps, new component types needed
3. Ask: "Any new UI patterns or component types introduced since last update?"
4. Make surgical edits; append `## Changelog` entry

---

## Output: specs/ui-ux.md

See `references/uiux-template.md` for the full canonical structure.

### Section Summary
| Section | Content |
|---------|---------|
| Design Tokens | Colors, typography scale, spacing scale, elevation |
| Component Library | Each component: variants, states, sizing, usage rules |
| Motion System | Duration scale, easing curves, standard transitions |
| Layout System | Grid, breakpoints, touch targets |
| Accessibility Standards | WCAG compliance rules, ARIA patterns, focus management |
| Iconography | Icon set, sizing rules, usage guidelines |
| Copy & Tone | Voice, label patterns, error message format |
| Changelog | Date-stamped change history |

---

## Execution Steps

1. Read prerequisite specs
2. Detect Initialize vs Review mode
3. Run elicitation or gap review
4. Confirm design decisions (flag conflicts with NFRs — e.g., contrast ratio vs brand color)
5. Write or update `specs/ui-ux.md`
6. Flag if frontend framework or styling library in `specs/design.md` needs updating to match

---

## Reference Files
- `references/uiux-template.md` — Canonical template
- `sample_output/ui-ux.md` — Example for mobile checkout program
