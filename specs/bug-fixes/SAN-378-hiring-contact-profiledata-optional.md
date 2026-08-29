---
id: SAN-378
title: hiring-contact forms read profileData.name/email/mobileNumber before profile stream resolves
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-378
sentry:
  - SC-SAAS-FRONTEND-79
repos: [frontend]
commit: sc-saas-frontend@c0638d20 (branch ai_native_setup_aman)
created: 2026-08-19
updated: 2026-08-19
---

# SAN-378 — hiring-contact form profileData TypeError

## Root cause
Form builders read `this.profileData.name`/`.email`/`.mobileNumber` inside a `getStartUpInfo` subscription, but `profileData` is populated by a separate `getProfileData$` subscription. When `startupInfo` resolves first (e.g. reached mid-program-application flow before the shell finishes loading), `profileData` is undefined. The same copy-pasted bug existed in 3 files, only 1 reported to Sentry:
1. `hiring-manager-contact.component.ts` (the reported one)
2. `hire-info-edit-page.component.ts` (same bug, not yet reported)
3. `step-hiring-contact.component.ts` `handleUseSameDetailsChange` (click-triggered variant, not yet reported)

## Fix
Added `?.` to `name`, `email`, and `mobileNumber` in both the constructor's `FormControl` initializers and `handleUseSameDetailsChange()`, across all 3 files.

**Correction during independent verification:** the first pass of this fix only guarded `mobileNumber` in files 1 and 2, leaving `name`/`email` unguarded on the same statement — since each field is an independent ternary (`res.x ? res.x : this.profileData.x`), the crash could still fire on `name`/`email` in the exact same race. Also missed `handleUseSameDetailsChange()` in files 1 and 2 entirely. Fixed properly in a follow-up edit — all three fields guarded in both the constructor and `handleUseSameDetailsChange()`, in all 3 files.

## Blast radius
None — these are independent copy-pasted duplicates, not shared code; fixing one doesn't affect the others.

## Verification
`tsc --noEmit` clean on all 3 files, both before and after the correction.
