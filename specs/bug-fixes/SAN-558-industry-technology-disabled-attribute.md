---
id: SAN-558
title: "disabled" attribute used with reactive form directive — industry-technology edit step
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-558
sentry:
  - SC-SAAS-FRONTEND-Z
repos: [frontend]
commit: sc-saas-frontend@31fa01bf (branch ai_native_setup_vishali, not pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-558 — disabled attribute with reactive form directive (industries)

## Root cause
`industry-technology.component.html`'s industries checkbox block had a hardcoded `[disabled]="true"` template binding alongside `[formControlName]="industry.id"`. The sibling `technologiesForm` checkbox block in the same file had already been fixed for the same class of warning (comment referencing this exact Sentry ID), but the parallel industries block was missed.

`industrySelectionChange()` in the component already calls `.disable()`/`.enable()` on `industriesForm` controls (~lines 189-193) — the disable logic already exists correctly at the FormControl level, the template binding was just redundant and is what Angular warns about.

## Fix
Removed the `[disabled]="true"` template binding on the industries checkbox; added the same explanatory comment already present on the `technologiesForm` block. No `.ts` change needed — the existing `.disable()`/`.enable()` calls already drive the real disabled state.

## Blast radius
None — purely removes a redundant, conflicting template binding. Enable/disable behavior unchanged (already handled correctly in the component).

## Verification
`npx tsc -p tsconfig.json --noEmit` clean (no new errors introduced across the repo).
