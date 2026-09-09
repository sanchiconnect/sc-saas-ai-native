---
id: SAN-521
title: RegisterComponent OTP send crash on undefined userAccountInfo
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-521
sentry:
  - SC-SAAS-FRONTEND-AQ
repos: [frontend]
commit: sc-saas-frontend@0c10e02b (branch ai_native_setup_vishali)
created: 2026-08-26
updated: 2026-08-26
---

# SAN-521 — undefined userAccountInfo crash sending OTP during registration

## Root cause
`RegisterComponent.prepareDataAndSendOtp()` builds the OTP payload from `this.userAccountInfo.countryCode` / `.mobileNumber` / `.emailAddress` with no null check. `userAccountInfo` has no initial value and is only populated when the child `app-account-information` form emits, so it can be `undefined` at call time. The crash happened inside a plain `setTimeout(() => this.sendOTP('email'), 1000)` that isn't tied to the component lifecycle, so state can change in that 1-second window before it fires.

Notably, the codebase already had the correct guard on one call path — `sendOTPFromVerificationPage()` checks `if (this.userAccountInfo)` before calling `prepareDataAndSendOtp()` — but the path that actually crashed (`sendOTP()` → `prepareDataAndSendOtp()`) had no such guard.

## Fix
Added the same `if (!this.userAccountInfo) return;` guard directly inside `prepareDataAndSendOtp()`, so both call sites are protected consistently instead of relying on each caller to remember to check.

## Blast radius
None — no behavior change for the working case; the OTP payload and dispatch are unaffected once `userAccountInfo` is populated. The only effect is a silent no-op instead of a crash when it isn't.

## Verification
`tsc --noEmit` clean; diff is 3 lines. No test suite configured for this repo; type-check + code-review against the existing `sendOTPFromVerificationPage` precedent was the strongest verification available.
