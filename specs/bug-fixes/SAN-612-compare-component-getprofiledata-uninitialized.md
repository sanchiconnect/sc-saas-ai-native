---
id: SAN-612
title: "TypeError: Cannot read properties of undefined (reading 'pipe') in compare.component.ts"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-612
sentry:
  - SC-SAAS-FRONTEND-CF
repos: [frontend]
commit: sc-saas-frontend@e518d6bd (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-612 — compare.component.ts getProfileData$ never assigned

## Root cause
`CompareComponent.getProfileData$` was declared (`public getProfileData$: Observable<IProfileDetails>;`) but never assigned anywhere in the file. `ngOnInit`'s `queryParams` subscription calls `getCompareData()` → `setProfileData()`, which unconditionally called `.pipe()` on it — always undefined, not just a rare race. The file already imported the `getProfileData` selector from `core/state/profile` but never used it.

## Fix
Assigned `this.getProfileData$ = this.store.pipe(select(getProfileData));` in the constructor, so it's populated before the queryParams subscription can ever call `setProfileData()`. Confirmed `getProfileData` returns `state.profileData` (typed `IProfileDetails`) and that the template consumes `profileData?.uuid` to highlight the logged-in investor's own card in the comparison — the correct selector for this use.

## Blast radius
None — purely additive initialization; no existing behavior depended on `getProfileData$` being unassigned.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. Proposed a regression test (assert `getProfileData$` is defined post-construction, `setProfileData()` doesn't throw pre-`ngOnInit`) pending go-ahead; not yet written.
