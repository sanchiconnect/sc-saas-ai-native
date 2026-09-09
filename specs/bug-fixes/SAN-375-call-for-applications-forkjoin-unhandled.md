---
id: SAN-375
title: call-for-applications forkJoin throws unhandled on a single flaky network call
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-375
sentry:
  - SC-SAAS-FRONTEND-1
repos: [frontend]
commit: sc-saas-frontend@c0638d20 (branch ai_native_setup_aman)
created: 2026-08-19
updated: 2026-08-19
---

# SAN-375 — call-for-applications forkJoin unhandled error

## Root cause
Actual error (via Sentry deep-dive): `HttpErrorResponse` — `POST .../check_application_status_multiple → status 0 "Unknown Error"`, a client-side network failure (CORS/offline/timeout), not a server response. `getAppliedPrograms()` does `forkJoin(apiCalls).subscribe((values) => {...})` with no error handler — any single failed call in the forkJoin throws unhandled to the global ErrorHandler/Sentry and aborts the whole computation.

## Fix
Added an `error: () => {}` handler to the `forkJoin(apiCalls).subscribe({...})` call.

## Blast radius
None — `appliedPrograms` stays at its previous/initial value (`[]`) if the call fails silently; other read sites (`hasAppliedPrograms()`, etc.) already tolerate a stale/empty array.

## Verification
`tsc --noEmit` clean.
