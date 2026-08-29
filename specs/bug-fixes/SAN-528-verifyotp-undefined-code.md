---
id: SAN-528
title: SignUpService.verifyOTP crash on undefined code before md5 hashing
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-528
sentry:
  - SC-SAAS-FRONTEND-7Q
repos: [frontend]
commit: sc-saas-frontend@943385c9 (branch ai_native_setup_vishali, pushed to origin, not yet on ai_native_setup/main)
created: 2026-08-26
updated: 2026-08-26
---

# SAN-528 — verifyOTP crash on undefined code

## Root cause
`SignUpService.verifyOTP()` (`sign-up.service.ts:39-47`) builds the request payload with `code: md5(signupCredentials.code.toString())` with no null check on `code`. This is dispatched via an NgRx effect (`sign-up.effect.ts:33`) using `code: this.otpCode` from `RegisterComponent` — `otpCode` is only populated by the OTP input's own change event, so it can still be `undefined` when a verify action fires. Same race-condition shape as the already-fixed SAN-521 (`userAccountInfo`) in the same registration flow. Because this throws synchronously inside the observable pipeline rather than through the method's own `catchError`, the user gets a hard crash instead of the existing error toast this method already shows for genuine server-side failures.

## Fix
Added a guard at the top of `verifyOTP()`: if `code` is missing, return a synthetic `throwError()` shaped like the `HttpErrorResponse` the existing `catchError` already expects (`{ error: { message: '...' } }`), so it flows through the same toast/error path already used for real API failures instead of crashing.

## Blast radius
None — no behavior change for the valid-input case; a missing code now surfaces as a clear "Please enter the OTP code" toast instead of a crash. Diff is 3 lines.

## Verification
`tsc --noEmit` clean. No test suite configured for this repo; type-check + code-review against the existing `catchError` error-shape convention in the same file was the strongest verification available. Committed (`943385c9`) and confirmed pushed to `origin/ai_native_setup_vishali`. Not yet on the shared `ai_native_setup` branch or `main`.
