---
id: SAN-594
title: Cannot assign to read only property 'revenue_stages' — frozen NgRx-dispatched object re-mutated on repeat settings emission
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-594
sentry:
  - SC-SAAS-FRONTEND-BW
repos: [frontend]
commit: sc-saas-frontend@2769263d (branch ai_native_setup_vishali, pushed)
created: 2026-09-04
updated: 2026-09-04
---

# SAN-594 — advanced-filter-wrapper revenue_stages frozen object

## Root cause
`fetchStartupFilterOptions()` (`advanced-filter-wrapper.component.ts:225-248`, before fix) fetched `res` from an HTTP call, then subscribed to `getGlobalSettings` **without `take(1)`** — a live, ongoing subscription. On each emission it mutated `res.revenue_stages = ...` directly and dispatched the same `res` object into the store via `FilterActions.SetStartupFilterOptions(res)`. `@ngrx/store`'s default dev-mode runtime immutability checks `Object.freeze()` anything dispatched. Once `res` was dispatched the first time, it became frozen; a second `getGlobalSettings` emission tried to mutate the same now-frozen object and threw.

The sibling `SERVICE_PROVIDER` handler in the same file (lines 212-220) already guards against this exact class of bug with `res = { ...res }` before use.

## Fix
Build a fresh object per settings emission instead of mutating the shared reference at all:
```ts
const updatedRes = {
  ...res,
  revenue_stages: settings.RevenueStage.map((e) => ({ ...e, id: e.value }))
};
this.store.dispatch(new FilterActions.SetStartupFilterOptions(updatedRes));
```
Stronger than a single upfront `{...res}` copy (which would still break on a third emission) — the original `res` is never mutated, so every emission, however many, builds its own safely-dispatchable object.

## Blast radius
None on the happy path — identical dispatched payload shape, just built immutably.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean on the changed file. No automated test suite exists for this repo.

## Related
`fetchInvestorFilterOptions()` in the same file has the same `res.ticket_size = ...` mutate-then-dispatch pattern but isn't in a live/repeating subscription, so it's lower-risk and left untouched — flag if it starts showing similar Sentry events. Same anti-pattern class as SAN-595.
