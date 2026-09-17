---
id: SAN-734
title: service-provider-dashboard — ngOnDestroy never emits destroyed$, so all eight takeUntil subscriptions leak
type: bug-fix
status: in-review
linear: https://linear.app/sanchiconnect/issue/SAN-734
sentry:
  - SC-SAAS-FRONTEND-6C
repos: [frontend]
commit: none — working tree only, branch ai_native_setup_sandeep (commit withheld per explicit instruction)
created: 2026-09-09
updated: 2026-09-09
---

# SAN-734 — service-provider dashboard subscription teardown

## Root cause

Three distinct defects in `service-provider-dashboard.component.ts`, all read directly from source:

1. **`ngOnDestroy()` called `destroyed$.complete()` without `destroyed$.next()`.** `takeUntil(notifier)` unsubscribes only when the notifier *emits*; `complete()` alone emits nothing. So **none** of the eight `takeUntil(this.destroyed$)` subscriptions was ever torn down — all leaked past component destruction, and a later store emission would write into a destroyed component (`this.trendingStartupsList = …`). The already-corrected sibling `community-feed-stats.component.ts:294-297` (SAN-428) does `next()` then `complete()`.

2. **`getInvestorDashboard()` both dispatched and subscribed.** It is invoked from *inside* the `getProfileData$` handler, so every profile emission dispatched the action **and** opened another `getServiceProviderDashboard` subscription. Combined with defect 1, subscriptions accumulated for the whole SPA session, and each duplicate re-ran the same five assignments per emission.

3. **The `getBrandDetails` subscription had no `takeUntil` at all** — the only one of eight without it, leaked unconditionally regardless of defect 1.

## What this fix does NOT explain — and why that matters

The Sentry group that prompted this, `SC-SAAS-FRONTEND-6C` (`ObjectUnsubscribedError: object unsubscribed`, culprit `getInvestorDashboard`), is **not** accounted for by any of the three defects above. Established by reading the installed dependencies rather than assuming:

- In **RxJS 7.5.7** (`node_modules/rxjs/dist/cjs/internal/Subject.js:52-56`), `ObjectUnsubscribedError` is thrown from exactly one place — `_throwIfClosed()`, guarded on `this.closed`. `closed` is set **only** by `Subject.unsubscribe()`. `complete()` sets `isStopped`, never `closed`, so subscribing to or completing a merely-completed Subject cannot produce this error.
- **No Subject anywhere in `src/app` is ever `unsubscribe()`d** — swept for it; every `.unsubscribe()` call in the codebase targets a `Subscription`, including the ones in `investors/pages/dashboard` (`investorDashboardSubscription`, `requestApprovalSuccess$`, `requestApprovalFail$`, all declared `Subscription`).
- **@ngrx/store 13.2.0** only ever `complete()`s its subjects: `ActionsSubject.ngOnDestroy` → `super.complete()`, `State.ngOnDestroy` → `stateSubscription.unsubscribe(); this.complete()`. The single `unsubscribe()` in the package targets an internal `Subscription`, not a Subject. So neither `store.dispatch()` nor `select()` can raise it.

So the throw most likely originates in a third-party Subject reached synchronously through `store.dispatch` → effect, **or** the culprit frame is simply misattributed. The latter is a live possibility: **SAN-221** ("Sentry source maps not uploaded for sc-saas-frontend — minified stack traces unreadable", still Backlog) means frame attribution in this project is not trustworthy.

**Consequence for process:** `SC-SAAS-FRONTEND-6C` was deliberately **not** resolved in Sentry on the back of this fix. Resolving it would have recorded a causal claim the evidence does not support. It needs either working source maps or a live repro (repeatedly navigating into and out of the service-provider dashboard).

## Fix

One file, **+27 / −11**.

- `ngOnDestroy()` now emits `destroyed$.next()` before `complete()`.
- The `getBrandDetails` subscription gained `takeUntil(this.destroyed$)`.
- The `getServiceProviderDashboard` subscription was hoisted out of `getInvestorDashboard()` into `ngOnInit`, placed **deliberately before** the `getProfileData$` subscription: that selector is BehaviorSubject-backed and emits synchronously on subscribe, which calls `getInvestorDashboard()` and therefore dispatches immediately — so the handler has to be live already or the resulting state emission would be missed on first load.
- `getInvestorDashboard()` now only dispatches, so re-invoking it on each profile change still refetches.

## Blast radius

Contained to one component in `sc-saas-frontend`. No feature flag, no controller/DTO, no data access — `/trace-flag`, `/audit-contract`, `/check-isolation` all genuinely n/a.

- Emitting `next()` makes teardown behave the way all eight subscriptions already assumed. Nothing in the component depends on a subscription outliving it — that dependency *was* the bug.
- `getBrandDetails` feeds only `this.brandDetails`, read by the template and the `isLimitedAccess` getter; both die with the component, so tearing it down changes nothing observable.
- Hoisting the selector subscription is behaviour-preserving: previously N duplicate subscriptions each ran the same five idempotent assignments per emission, so collapsing to one produces identical state. The refetch-on-profile-change path is preserved because the dispatch stayed in `getInvestorDashboard()`.
- `getInvestorDashboard()` has no other caller — not in the template, not elsewhere in TypeScript. (Four sibling dashboards define their own same-named method; they are separate components, untouched.)

## Trade-off

Nothing given up functionally. The one judgement call is subscription *order* in `ngOnInit`: putting the dashboard-selector subscription first is what guarantees no missed first-load emission, and that ordering is now load-bearing. It is commented in the code so a future reorder does not silently break first load.

Scope was deliberately **not** widened. A sweep found the same defects in all four sibling dashboards — `mentors-dashboard`, `program-office-dashboard`, `corporate-dashboard` (all three with the identical bare `destroyed$.complete()` plus a leaked `getBrandDetails`), and `investors/pages/dashboard` (uses explicit `Subscription` fields correctly, so only the leaked `getBrandDetails`). They are copy-paste variants of this component and want their own issue rather than being smuggled into a single-component ticket.

## Verification

- `npx tsc -p tsconfig.app.json --noEmit` → exit 0.
- `npx ng build --configuration development` → exit 0 (AOT + `strictTemplates`).
- Sibling sweep performed and reported, per the issue's own acceptance criterion.
- **No automated test coverage added.** Consistent with the rest of this repo; the component has no usable spec harness.
- **Not reproduced in a browser**, and by design this fix cannot be confirmed against `SC-SAAS-FRONTEND-6C` — see the section above.

## Not deployed

`origin/main` tip is `15b195fe2` (2026-08-14), **187 commits / 26 days** behind `origin/ai_native_setup` — SAN-589. This change is not even committed yet, so there are three gates between it and users: commit, merge, deploy.
