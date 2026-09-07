---
id: SAN-670
title: "Unhandled 500 on profile-views/increment — missing catchError guard"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-670
sentry:
  - SC-SAAS-FRONTEND-Y
repos: [frontend]
commit: sc-saas-frontend@b087076b (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-670 — profile-views/increment unhandled 500, fires on every public profile view

## Root cause
`public-api.service.ts`'s `incrementProfileViews()` has a `catchError` that shows a toast and rethrows (`return throwError(() => fault)`). Every call site — `checkAndIncrementProfileView()` in 7 different public-profile components (corporate, individual, startup, investor, mentor, program-office, service-provider) — calls `.subscribe()` with no error callback. Since nothing downstream handles the rethrown error, RxJS surfaces it as an unhandled rejection outside the Angular zone, on a public, unauthenticated, non-critical "increment view count" call. Highest-impact issue found in this triage pass: 10 users / 24 events over ~5 weeks.

## Fix
Changed the `catchError` to `return of(null)` instead of rethrowing — the toast still shows, but the failure no longer propagates as an unhandled rejection. Single-point fix covers all 7 call sites without touching any of them.

## Blast radius
None — this call's result was never consumed for control flow at any call site; only side effect was the toast, which is preserved.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.

## Related
SC-SAAS-FRONTEND-BB (SAN-655) is a sibling crash in the same `checkAndIncrementProfileView()` call chain, left open pending investigation — worth revisiting now that this fix lands.
