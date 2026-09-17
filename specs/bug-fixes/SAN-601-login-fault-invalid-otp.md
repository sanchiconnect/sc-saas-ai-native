---
id: SAN-601
title: "loginFault(Invalid OTP) re-thrown to Sentry — 20 users, 23 events"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-601
sentry:
  - SC-SAAS-FRONTEND-3H
repos: [frontend]
commit: sc-saas-frontend@4e4bd3cb (branch ai_native_setup_vishali, pushed)
created: 2026-09-04
updated: 2026-09-04
---

# SAN-601 — loginFault(Invalid OTP) re-thrown to Sentry

## Investigation — not a code defect
`AuthService.verifyOtp()`'s `catchError` block `console.warn`s this fault and already calls `this.toastService.showToast(this.globalService.getErrorMessage(fault, 'Error verifying the OTP!'), 'error')` — fully handled. Same over-logging pattern as SAN-599 (program-apply OTP step) in the login flow's OTP step specifically.

## Fix
Same `main.ts:109` `HANDLED_HTTP_FAULT` regex extension as SAN-599/600/608.

## Blast radius
None — login OTP verification and its toast/error-callback path are unchanged.

## Verification
`npx tsc --noEmit` clean.

## Related
SC-SAAS-FRONTEND-2Q (SAN-599), SC-SAAS-FRONTEND-4K (SAN-600), SC-SAAS-FRONTEND-34 (SAN-608) — same fix, same commit.
