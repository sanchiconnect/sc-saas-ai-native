---
id: SAN-479
title: CORS domains upsert warn log — cockpit URL not configured (Sentry noise)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-479
sentry:
  - SC-SAAS-BACKEND-20
repos: [backend]
commit: pending (branch ai_native_setup_aman)
created: 2026-08-21
updated: 2026-08-21
---

# SAN-479 — CORS domains upsert warn log from local env

## Root cause
`partner-cors-domain-push.service.ts` (added SAN-387) logs `logger.warn()` at line 103 when `COCKPIT_API_URL`/`SANCHI_CONNECT_API_BASE_URL` or the internal API key is not set. This is the expected code path in local development environments where the cockpit isn't reachable. `CaptureConsole({ levels: ['warn', 'error'] })` in `instrument.ts` forwarded this warn to Sentry as event SC-SAAS-BACKEND-20.

## Fix
Downgraded `logger.warn` → `logger.debug` at `partner-cors-domain-push.service.ts:103`. The skip behavior (return early without calling the cockpit) is unchanged and intentional — the service is best-effort by design. The catch-block `logger.error` at line 132 is NOT downgraded — that fires when the cockpit was actually called and failed, which is a real failure worth capturing.

## Blast radius
None — logging change only; best-effort skip behavior unchanged.

## Verification
`tsc --noEmit --skipLibCheck` clean. No commit/push until Aman confirms.
