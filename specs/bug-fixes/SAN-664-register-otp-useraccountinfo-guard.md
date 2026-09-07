---
id: SAN-664
title: "Uncaught (in promise): Cannot read 'countryCode' — verifyEmailOTP/verifyMobileOTP missing userAccountInfo guard"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-664
sentry:
  - SC-SAAS-FRONTEND-8Q
repos: [frontend]
commit: sc-saas-frontend@2d45af6a (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-664 — register.component verifyEmailOTP/verifyMobileOTP missing guard

## Root cause
`verifyEmailOTP()` and `verifyMobileOTP()` read `this.userAccountInfo.countryCode/.mobileNumber/.emailAddress` with no guard. SAN-521 already added `if (!this.userAccountInfo) return;` to `prepareDataAndSendOtp()` for the identical crash, but these two methods were never given the same guard.

## Fix
Added the same `if (!this.userAccountInfo) return;` guard at the top of both `verifyEmailOTP()` and `verifyMobileOTP()`.

## Blast radius
None — in the normal flow `userAccountInfo` is always set before OTP verification runs; the guard only short-circuits an already-broken call path.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.
