---
id: SAN-407
title: getAdminConsoleUrl fails outright on a transient cockpit 502 instead of using cached settings
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-407
sentry:
  - SC-SAAS-BACKEND-1H
repos: [backend]
commit: sc-saas-backend@d9ec7f0a (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-20
---

# SAN-407 — getAdminConsoleUrl hard-fails on transient cockpit 502

## Root cause
`partner.service.ts`'s `getAdminConsoleUrl` (the partner-facing "open admin console" action) called `globalService.getSAASSettings(false)` synchronously on every request to refresh tenant settings from the cockpit. `sanchiconnect.service.ts` has no retry/timeout handling — any upstream failure (including a transient 502) was rethrown as `InternalServerErrorException`, failing the entire action even though `saasSettings` (a shared module-level object, `enum.ts`) already held usable, last-successfully-fetched values.

## Fix
Wrapped the settings refresh in try/catch; on failure, logs a warning and falls through to the already-populated `saasSettings` values instead of failing the request.

## Blast radius
Low — only affects this one per-request refresh call; `getSAASSettings` is still called normally at bootstrap and by cron, where failures still surface loudly since no cache exists yet at true first boot.

## Verification
`tsc --noEmit` clean; `npm run build` clean; lint shows only pre-existing unrelated warnings. Manually forcing a cockpit-unreachable scenario was not performed in this session.
