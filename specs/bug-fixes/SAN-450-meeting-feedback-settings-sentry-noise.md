---
id: SAN-450
title: Meeting feedback settings warn log flooding Sentry (6128 events)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-450
sentry:
  - SC-SAAS-BACKEND-E
repos: [backend]
commit: already in codebase (meeting-reminder.service.ts:233 — logger.warn → logger.debug)
created: 2026-08-20
updated: 2026-08-21
---

# SAN-450 — Meeting feedback settings warn log flooding Sentry

## Root cause
`meeting-reminder.service.ts:233` used `logger.warn()` when a tenant hasn't configured meeting-feedback settings. This cron runs for every tenant on a fixed schedule — tenants without meeting-feedback configured always hit this branch, so every run produced a Sentry event via `CaptureConsole({ levels: ['warn', 'error'] })`.

## Fix
Already in the TypeScript codebase: `logger.warn()` was downgraded to `logger.debug()` with an inline comment. Old compiled JS in production was still running the `warn` version, causing the 6,128 events. Events stopped 2026-08-07 after a prior deploy.

## Blast radius
None — cron-only, no API contract change.

## Verification
No code change required. Fix rides with next production deploy of `ai_native_setup`. Sentry issue SC-SAAS-BACKEND-E resolved.
