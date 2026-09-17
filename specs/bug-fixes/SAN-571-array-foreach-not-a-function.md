---
id: SAN-571
title: "Uncaught TypeError: Ne.forEach is not a function"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-571
sentry:
  - SC-SAAS-FRONTEND-71
repos: [frontend]
commit: sc-saas-frontend@be2582c5 (branch ai_native_setup_vishali, not pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-571 — forEach on a non-array value

## Root cause
Culprit is minified (`Array.forEach(<anonymous>)`) — could not pin the exact single call site that produced this specific incident (6 users, 16 events, 13 days ago, no repeat since; no source maps available, see SAN-221). Searched for the described recurring anti-pattern (`.forEach()` on an HTTP-response-derived value with no `Array.isArray` check) and found it duplicated verbatim at 3 concrete, verified call sites sharing the same vulnerable shape (`map(response => response?.data)`, no error callback on subscribe):
- `growth-matrics-form.component.ts:91-96` (`MetricsService.getMetricsTypes()`)
- `hire.component.ts:314-323` (`JobsService.getInterviews()`)
- `applied-jobs.component.ts:208-217` (same `getInterviews()` call, duplicated)

## Fix
Added a minimal `Array.isArray(...)` guard at each of the 3 sites before the `.forEach()` call. Normal-case behavior (a proper array response) is unchanged; a malformed response shape now no-ops instead of throwing.

## Confidence note
**Speculative on which site (if any) caused this specific Sentry incident** — all 3 are genuine, verified instances of the anti-pattern, not guesses, but I could not confirm which one (or whether a 4th, unfound site) produced this exact event. Safe change regardless (defensive-only), but flag for extra scrutiny before considering this ticket fully closed.

## Blast radius
None — additive guard only; a genuinely array-shaped response behaves identically.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean.
