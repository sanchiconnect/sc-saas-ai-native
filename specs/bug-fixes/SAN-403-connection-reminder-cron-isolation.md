---
id: SAN-403
title: sendBulkPendingConnectionReminderEmail / connectionRemainder() cron can abort mid-batch
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-403
sentry:
  - SC-SAAS-BACKEND-10
repos: [backend]
commit: sc-saas-backend@d9ec7f0a (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-20
---

# SAN-403 — connectionRemainder() cron mid-batch abort

## Root cause
`ses-email.service.ts`'s `sendBulkPendingConnectionReminderEmail` already had a per-recipient try/catch around template rendering from a prior fix, so its log line is expected, handled noise. The actual bug was one level up: `connection-remainder-2.service.ts`'s `connectionRemainder()` per-connection loop (building `userConnectionData`) had **no try/catch at all** — a single connection's S3 signing failure (`getSignedUrlWithCustomExpiration`) or URL-service error aborted the reminder cron for every other investor in that run, and could prevent the final `sendBulkPendingConnectionReminderEmail()` call from ever executing that pass. `raising_funds`/`startup_elevator_pitch` also read nested fields with no null fallback.

## Fix
- Wrapped the per-connection processing block in try/catch, logging and skipping just that connection instead of aborting the whole run.
- Added `?? ''` fallbacks for `raising_funds` and `elevatorPitch`.

## Blast radius
None — cron-only, no API contract change. `raising_funds` stayed typed `string` per `ses-email.type.ts`.

## Verification
`tsc --noEmit` clean; `npm run build` clean; lint shows only pre-existing unrelated warnings. No automated test coverage exists for this cron path; a manual dry-run against a startup with incomplete financials was not performed in this session.
