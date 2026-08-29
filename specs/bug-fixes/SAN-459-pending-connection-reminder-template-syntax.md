---
id: SAN-459
title: Email template parse error — Handlebars space in {{#each}} in PENDING_CONNECTION_REMINDER (7 events)
type: bug-fix
status: in-progress
linear: https://linear.app/sanchiconnect/issue/SAN-459
sentry:
  - SC-SAAS-BACKEND-N
repos: [backend]
commit: already in codebase (ses-email.service.ts — compile+render wrapped in try/catch)
created: 2026-08-20
updated: 2026-08-21
---

# SAN-459 — Handlebars template syntax error (space in `{{ #each`)

## Root cause
The `PENDING_CONNECTION_REMINDER` email template stored in the DB has `{{ #each connections` (space between `{{` and `#each`) on line 23 — invalid Handlebars syntax. Old production JS had no try/catch around `handlebars.compile()`, causing an unhandled rejection that crashed the whole cron batch.

## Fix — two parts

**Code side (already in TypeScript source, no new commit):**
`ses-email.service.ts` lines 2374–2419 now wrap both `handlebars.compile()` and the per-recipient render in try/catch with error logging.

**Data side — action required by Aman via admin panel:**
Find the `PENDING_CONNECTION_REMINDER` template in the email templates admin UI and change `{{ #each connections` → `{{#each connections` (remove the space).

## Blast radius
None until data fix — connection reminder emails are silently failing for all recipients.

## Verification
Code fix: `tsc` clean. Data fix: pending admin panel action.
