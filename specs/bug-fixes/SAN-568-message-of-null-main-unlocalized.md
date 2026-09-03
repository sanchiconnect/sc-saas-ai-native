---
id: SAN-568
title: Cannot read 'message' of null — crash in main error path (unresolved culprit)
type: bug-fix
status: in-progress
linear: https://linear.app/sanchiconnect/issue/SAN-568
sentry:
  - SC-SAAS-FRONTEND-6W
repos: [frontend]
commit: n/a — could not confidently localize
created: 2026-09-03
updated: 2026-09-03
---

# SAN-568 — message-of-null crash, unresolved culprit

## Finding
Sentry's culprit resolves only to `main` (minified — source maps not uploaded, see SAN-221). Searched for a custom Angular `ErrorHandler` implementation in `src/app` (`grep "implements ErrorHandler"`) — none exists. `app.module.ts:91` only registers `Sentry.createErrorHandler({ showDialog: false })`, a third-party class from `@sentry/angular` — not source this repo can patch.

The crash most likely lives inside that vendor bundle or some other main-chunk code, not a bespoke handler here. Per instructions, did not blind-guard an unrelated file speculatively.

## Re-investigated 2026-09-03
Re-confirmed no custom `ErrorHandler` exists in this repo (only the third-party `Sentry.createErrorHandler()` registration in `app.module.ts`). Without a readable stack frame there is no code to point a fix at. Conclusion stands — genuinely blocked, not skipped.

## Action required
Re-triage once `SAN-221` (Sentry source maps) lands and the real frame becomes readable.

## Blast radius
None — no change made.

## Verification
N/A — no code change made.
