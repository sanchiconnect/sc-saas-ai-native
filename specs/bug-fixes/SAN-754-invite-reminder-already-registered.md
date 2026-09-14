---
id: SAN-754
title: Already-registered stakeholders can still receive invite/reminder emails
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-754/backend-already-registered-stakeholders-can-still-receive
owner: aman.k@sanchiconnect.com
repo: backend
severity: High
created: 2026-09-11
closed: 2026-09-14
---

# Already-registered stakeholders can still receive invite/reminder emails

## Problem
A user who already registered could still be sent a brand-new invite email, and would then keep receiving the daily "Reminder: ..." invite email — even though they already had an account. Found live via `sc-saas-backend`'s `ses_email_queue` table for an investor (`sunil.ks@sanchiconnect.com`, i-Hub Uttar Pradesh), but the underlying flow (`InviteUsersDto.userType`) is shared by every stakeholder type — startup, investor, corporate, mentor, service_provider, partner, program_office, individual — so it was never investor-specific.

## Evidence
- `ses_email_queue` id 101 (invite sent 2026-09-05) and id 154 (invite sent 2026-09-07) both correctly flipped to `is_registered=1` at `2026-09-07 10:20:45` when the user registered, via the bulk update in `AuthService.registerUser()` (`src/modules/auth/auth.service.ts:772-779`).
- `ses_email_queue` id 178 — a new invite created 2026-09-08 11:15, a full day *after* registration, via one of the two "instant" invite paths (`AdminActionsService.adminInviteUsersInstant()` / `PartnerService.inviteInstantUser()`), whose existing-user guard should have blocked it but didn't.
- Row 178 stayed `is_registered=0`, so the `INVITATION_REMINDER` cron matched it on 2026-09-11 08:00 IST and sent a reminder to an already-registered user.

## Root cause
1. **Invite-time guard gap** — the instant-invite existing-user check (`admin-actions.service.ts:3301`/`:3339`) matched emails via `In(emailAddresses)` against the raw `users.email` column, which depends on that column's DB collation for case matching. A casing difference between the stored account and the new invite request could silently produce zero matches.
2. **Reminder-time blind spot** — `is_registered` on `ses_email_queue` is only ever set once, at the exact moment of registration, against rows that exist *at that time*. Any invite row created afterward (for any reason) starts `is_registered=false` and is never reconciled against the fact that a user for that email already exists.

## Fix
- `src/modules/user/repositories/user.repository.ts` — `getUsersByEmailAddresses()` now matches case-insensitively via `LOWER()` at the SQL level instead of depending on column collation. Used by all three invite call sites in `admin-actions.service.ts` (`inviteUsers`, `adminInviteUsersInstant`, `inviteInstantUser`).
- `src/core/services/ses-email.service.ts` — `createInvitationEmailsInEmailQueue()` re-checks the live users table before converting a scheduled invite into a queue row; skips anyone already registered.
- `src/modules/cron/invitation-reminder.service.ts` — `sendInvitationReminderEmail()` re-checks the live users table before sending each reminder; skips and self-heals (`isRegistered=true`) any row whose email already has an account, instead of trusting only the cached flag.

Applies uniformly across all stakeholder types — none of this logic branches on `userType`, matching the platform rule that one email maps to exactly one account regardless of type (`AuthService.checkUserAlreadyExist()`, `auth.service.ts:1664-1686`).

## Verification
- `npx tsc --noEmit` — clean.
- `eslint` on every changed/new file — clean (pre-existing CRLF line-ending noise in `ses-email.service.ts` confirmed against git HEAD, left untouched to avoid an unrelated multi-thousand-line diff).
- `npm test` (full suite) — 349 tests / 25 suites: 347 pass, 2 fail (pre-existing, unrelated `global-onboarding-design.spec.ts` field drift). `admin-actions.service.spec.ts` and `admin-actions-partner-broadcast.service.spec.ts` (which exercise the changed guard) both pass.
- `npm run build` — `nest build` compiles clean; the `copy-assets` post-step's Unix-`cp` failure is a pre-existing, environment-specific (Windows) limitation, unrelated.
- Added first-ever spec coverage for all three touched units: `user.repository.spec.ts`, `ses-email.service.spec.ts`, `invitation-reminder.service.spec.ts` (14 new tests, all passing).

## Commit
`c6d1a4eb` on `ai_native_setup_aman`, pushed to `origin/ai_native_setup_aman`.

## Out of scope (flagged, not fixed here)
- `console.log(inviteUsersDto)` in `admin-actions.controller.ts:503` logs invitee PII in plaintext.
- `adminMd5` passed as a URL path segment (pre-existing, workspace-wide pattern in `admin-actions.controller.ts`, not introduced by this fix).
