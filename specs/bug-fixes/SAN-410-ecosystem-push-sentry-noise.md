---
id: SAN-410
title: ECOSYSTEM_PUSH_FAILED_ON_APPROVE flooding Sentry for an already-handled, best-effort sync
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-410
sentry:
  - SC-SAAS-BACKEND-1W
  - SC-SAAS-BACKEND-Y
  - SC-SAAS-BACKEND-18
repos: [backend]
commit: sc-saas-backend@d9ec7f0a (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-20
---

# SAN-410 — ecosystem-push failures flooding Sentry

## Root cause
`admin-actions.service.ts` has one independent try/catch per stakeholder-type approval branch (partner, startup, mentor, investor, etc. — 8 occurrences), each calling the ecosystem directory push as a deliberately best-effort sync: the profile is already approved in the DB by that point, so a push failure must not fail the approval, and it doesn't — every branch already catches and logs via `logger.warn`. The 500 in the message is the upstream cockpit API's response, already fully absorbed; nothing here is actually broken. `instrument.ts`'s `CaptureConsole({ levels: ['warn', 'error'] })` forwarded every one of these to Sentry on every transient upstream hiccup, across every approval, for every stakeholder type — noise, not a defect.

## Fix
Downgraded all 8 `ECOSYSTEM_PUSH_FAILED_ON_APPROVE` log calls from `.warn` to `.debug`. `CaptureConsole` only forwards warn/error by design, so this stops the Sentry noise while the log remains available locally if debug logging is enabled.

## Blast radius
None — approval flow behavior is unchanged (already non-blocking); this only affects what reaches Sentry.

## Trade-off
A genuinely sustained ecosystem-push outage (not just transient 500s) would no longer surface in Sentry either. Alerting on repeated failures specifically would need a dedicated low-volume metric — a follow-up enhancement, not part of this fix.

## Verification
`tsc --noEmit` clean; `npm run build` clean; lint shows only pre-existing unrelated warnings. Logging-level change only — no automated test coverage applicable.
