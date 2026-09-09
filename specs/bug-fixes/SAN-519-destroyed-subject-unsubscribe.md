---
id: SAN-519
title: destroyed$ Subject.unsubscribe() causes ObjectUnsubscribedError (8 components)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-519
sentry:
  - SC-SAAS-FRONTEND-AG
repos: [frontend]
commit: sc-saas-frontend@1e172e3a (branch ai_native_setup_vishali)
created: 2026-08-26
updated: 2026-08-26
---

# SAN-519 — ObjectUnsubscribedError on startup financial-details save

## Root cause
Not a bug in `FinancialsDetailsComponent` itself — Sentry tags an error with whatever route is active in the tab at the moment it throws, not with whichever leaked subscription is actually firing. The real cause is a recurring anti-pattern already fixed once before under SAN-513 / SC-SAAS-FRONTEND-3S (see the explanatory comment in `community-feed-stats-count.component.ts`), reintroduced in 8 components:

```ts
ngOnDestroy(): void {
  this.destroyed$.complete();
  this.destroyed$.unsubscribe(); // <- bug: closes the Subject permanently
}
```

`.complete()` alone is correct and sufficient for the `takeUntil(this.destroyed$)` idiom used throughout this codebase. Calling `.unsubscribe()` directly on the Subject (not on a `Subscription`) permanently marks it `closed`; any later/nested `takeUntil(destroyed$)` subscribe attempt against that same instance then throws `ObjectUnsubscribedError` instead of completing harmlessly — matching this Sentry stack exactly (`Store.subscribe → Subject.subscribe → _trySubscribe → _throwIfClosed`). Because an Angular SPA doesn't reload the JS runtime on navigation, this can surface on whatever route the user happens to be on when the leaked callback fires — in this report, `/startups/edit/financial-details`, even though that page's own component is clean.

Found via grep for `destroyed$.unsubscribe()` — 8 instances, all with the same anti-pattern:
1. `src/app/modules/corporate/pages/corporate-dashboard/corporate-dashboard.component.ts`
2. `src/app/modules/mentors/pages/mentors-dashboard/mentors-dashboard.component.ts`
3. `src/app/modules/service-provider/pages/service-provider-dashboard/service-provider-dashboard.component.ts`
4. `src/app/modules/program-office/program-office-dashboard/program-office-dashboard.component.ts`
5. `src/app/modules/partners-details/partners-details.component.ts`
6. `src/app/shared/common-components/startup-investor-dashboard-common-calender/dashboard-common-calender.component.ts`
7. `src/app/modules/community-feed/community-feed-post/community-feed-post.component.ts`
8. `src/app/modules/partners/partners.component.ts`

## Fix
Deleted the `this.destroyed$.unsubscribe();` line in all 8 files, keeping only `this.destroyed$.complete();` — identical to the already-validated SAN-513 fix.

## Blast radius
None — `.complete()` alone fully tears down every `takeUntil(this.destroyed$)` subscriber in these components. The only effect of removing `.unsubscribe()` is that the Subject no longer stays permanently `closed`, so a later/nested subscribe attempt completes harmlessly instead of throwing. Diff is exactly 8 one-line deletions.

## Verification
`tsc --noEmit` clean. No test suite configured for this repo; type-check was the strongest verification available.
