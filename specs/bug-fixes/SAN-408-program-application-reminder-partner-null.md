---
id: SAN-408
title: sendProgramManagementPendingApplicationEmail crashes whole batch on a partner-less program
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-408
sentry:
  - SC-SAAS-BACKEND-1R
repos: [backend]
commit: sc-saas-backend@d9ec7f0a (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-20
---

# SAN-408 — partner-less program crashes the pending-application reminder batch

## Root cause
`ses-email.service.ts`'s `sendProgramManagementPendingApplicationEmail` `forEach` callback read `emailDetail.partner.name` without optional chaining — inconsistent with the guarded `.logo` access two lines above, and with a near-duplicate function elsewhere in the same file that already guards `.name`. The caller (`pending-program-application-reminder.service.ts`) only sets `partner` when `program.partnerId` is truthy, so a platform-run program (no partner) throws here. Unlike its sibling `sendBulkPendingConnectionReminderEmail`, this `forEach` had no try/catch, so one partner-less pending application aborted the reminder for every other applicant in that batch.

## Fix
Added `?.` to `emailDetail.partner.name` (matching the established convention elsewhere in this file), and wrapped the `forEach` body in a per-recipient try/catch matching the pattern already used in `sendBulkPendingConnectionReminderEmail`.

## Blast radius
None — purely additive null-safety + isolation; no contract change.

## Verification
`tsc --noEmit` clean; `npm run build` clean; lint shows only pre-existing unrelated warnings. A manual run with a partner-less pending program was not performed in this session.
