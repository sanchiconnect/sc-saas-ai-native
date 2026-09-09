---
id: SAN-468
title: InternalServerError — No recipients defined in SESEmailService (1 event)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-468
sentry:
  - SC-SAAS-BACKEND-11
repos: [backend]
commit: sc-saas-backend@2e01d244 (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-21
---

# SAN-468 — No recipients defined causing 500 in SESEmailService

## Root cause
`sendEmail()` in `ses-email.service.ts` had no guard for an empty `to` field. When admin account is created with no email, the call proceeded to the third-party gateway which rejected with "No recipients defined" — rethrown as `InternalServerErrorException`. The original Linear description suggested returning `null`, but the safety review identified a secondary risk: returning `null` caused `mailStatus: 'sent'` to be set incorrectly in `payment-management.service.ts`, marking invoices as sent without actually sending.

## Fix
Two changes in `ses-email.service.ts`:
1. Changed empty-`to` guard to `throw new BadRequestException(...)` (not return null) — preserves exception propagation so downstream callers cannot silently treat "no email sent" as success.
2. Added `if (reqBody.icalEvent == null) { delete reqBody.icalEvent; }` before the axios POST to the third-party gateway — prevents `"icalEvent": null` propagating as a JSON field to the gateway.

## Blast radius
Callers that previously sent a 500 on empty recipient now get a 400. `payment-management.service.ts` now correctly does not set `mailStatus: 'sent'` when email sending fails.

## Verification
`tsc --noEmit --skipLibCheck` clean. Safety review completed. Committed `2e01d244`.
