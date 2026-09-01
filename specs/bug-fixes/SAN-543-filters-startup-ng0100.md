---
id: SAN-543
title: NG0100 ExpressionChangedAfterItHasBeenCheckedError in FiltersStartupComponent
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-543
sentry:
  - SC-SAAS-FRONTEND-BX
repos: [frontend]
commit: not committed (uncommitted local change on ai_native_setup working tree — verified by user)
created: 2026-09-01
updated: 2026-09-01
---

# SAN-543 — NG0100 in FiltersStartupComponent (search/startups)

## Root cause
`filters-startup.component.html` binds several filter-count badges directly to `counts['<key>']?.length` (e.g. `businessModelIds`), and separately binds `*ngIf="isFilterApplied"` on the "clear filters" button.

`isFilterApplied` is a getter, and it called `mapFilters()` — which has a side effect: it mutates `this.counts[controlName]` while computing the filters payload. Angular re-evaluates template getters on every change-detection pass, so simply rendering the template mutated `counts` mid-render. `counts['businessModelIds']` was `undefined` on the first CD pass (badge's `*ngIf` sees `null`), then became `[]` after the getter ran later in the same pass — the dev-mode `checkNoChanges` pass caught the mismatch (`null` → `0`) and threw NG0100.

Classification: **CODE_ERROR** — state mutation inside a getter read from the template.

## Fix
Extracted a pure `computeFilters()` helper (`filters-startup.component.ts`) returning `{ filters, counts }` with no side effects on instance state. `this.counts` is now only mutated inside `mapFilters()`, which is invoked exclusively from real user actions (`handleSearch`, `clearAllFilter`, `patchFilters`, `handleApplyFilters`, `handleSelectSavedFilter`) — never from a getter read during change detection. `isFilterApplied` now calls `computeFilters()` directly instead of `mapFilters()`.

No change to filter behavior or displayed badge counts — purely removes the side-effect-during-render anti-pattern.

## Blast radius
Single-repo, single-component: `sc-saas-frontend` — `src/app/modules/search/components/advanced-filters-modal/filters-startup/filters-startup.component.ts`. No API contract, flag, or tenant-scoping impact.

## Verification
`tsc --noEmit` clean for the touched file (workspace-wide run surfaces pre-existing, unrelated `*.spec.ts` Jasmine-typings errors when run outside Angular's Karma config — not caused by this change). No regression test was added — declined by the user for this fix; documenting the gap per process instead. User has verified the fix locally. Not yet committed or pushed to git.
