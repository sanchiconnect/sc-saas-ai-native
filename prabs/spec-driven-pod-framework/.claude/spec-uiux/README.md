# spec-uiux

Creates, reviews, and updates the UI/UX design specification (`specs/ui-ux.md`). The single source of truth for visual and interaction consistency — created once and shared across all features and pods. Defines the component library, design tokens, interaction patterns, and accessibility standards.

---

## When to Use

Activate when updating the UI spec, defining the design system, setting up components, choosing colors and fonts, defining buttons and inputs, or making any decision about visual design, component behavior, typography, color palette, spacing, iconography, motion, or accessibility.

---

## Inputs

| Input | Required |
|---|---|
| `specs/program.md` | Mandatory |
| `specs/design.md` | Optional |
| `specs/ui-ux.md` | Optional (Review Mode) |

## Outputs

- `specs/ui-ux.md` — complete UI/UX specification with design tokens, component library, motion system, layout system, accessibility standards, iconography, and copy guidelines

---

## Framework Position

| Runs After | Runs Before |
|---|---|
| spec-design | spec-generation |
| | design-setup |
