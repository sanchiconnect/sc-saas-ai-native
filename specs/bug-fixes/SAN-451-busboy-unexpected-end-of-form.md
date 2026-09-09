---
id: SAN-451
title: Unexpected end of form — multipart upload surfacing as Sentry error (157 events)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-451
sentry:
  - SC-SAAS-BACKEND-Q
repos: [backend]
commit: already in codebase (global-exception.filter.ts + instrument.ts)
created: 2026-08-20
updated: 2026-08-21
---

# SAN-451 — Busboy "Unexpected end of form" flooding Sentry

## Root cause
Client-abort mid-upload causes busboy to emit "Unexpected end of form" / "Unexpected end of multipart data". Old production JS had no guard, surfacing this expected network condition as a Sentry error.

## Fix
Two-layer fix already in the TypeScript codebase:
1. `global-exception.filter.ts:40-44` — catches these strings and reclassifies as HTTP 400 (never reaches Sentry as a server error).
2. `instrument.ts:82-95` — Sentry `beforeSend` hook drops these events entirely even when they bypass the NestJS filter as Node-level uncaught exceptions.

Old production JS was still running without these guards.

## Blast radius
None — exception-filter-only change, no API contract change.

## Verification
No code change required. Fix rides with next production deploy of `ai_native_setup`.
