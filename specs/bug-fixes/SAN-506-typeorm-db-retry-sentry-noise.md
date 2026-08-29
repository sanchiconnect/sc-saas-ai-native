---
id: SAN-506
title: TypeORM DB connection retry noise from local dev — Sentry noise
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-506
sentry:
  - SC-SAAS-BACKEND-22
repos: [backend]
commit: 899ed2d2 (branch ai_native_setup_aman)
created: 2026-08-25
updated: 2026-08-25
---

# SAN-506 — TypeORM DB retry message flooding Sentry from local

## Root cause
TypeORM logs `Unable to connect to the database. Retrying (N)...` at `error` level during startup
when MySQL isn't ready yet. `CaptureConsole({ levels: ['warn', 'error'] })` in `instrument.ts`
forwards any error-level console message to Sentry.

This is a `default`-type Sentry event (message field, not exception). The existing
`isBusboyClientAbort()` filter only checks `event.exception.values` and does not match message-type
events — so TypeORM retry messages slipped through.

All 4 events came from a local developer machine (x64 Intel i5-12400F, Docker container, no cloud
resource) — not production.

## Fix
Added `isTypeOrmDbRetry()` in `instrument.ts` that checks `event.message.startsWith('Unable to
connect to the database')` and returns null (drop) in `scrubEvent()`. Follows the same pattern as
the busboy client-abort filter (SAN-450).

## Blast radius
None — filter is drop-only for a specific startup-time message. Real DB errors (query failures,
connection pool exhaustion) have different messages and are unaffected.

## Verification
`tsc --noEmit --skipLibCheck` clean. No commit/push until Aman confirms.
