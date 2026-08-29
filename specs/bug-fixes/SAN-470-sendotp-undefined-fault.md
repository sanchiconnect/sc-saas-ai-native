---
id: SAN-470
title: sendOTPFault(undefined) on program-apply OTP send
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-470
sentry:
  - SC-SAAS-FRONTEND-6S
repos: [frontend]
commit: uncommitted (working tree only, awaiting review)
created: 2026-08-20
updated: 2026-08-20
---

# SAN-470 — sendOTPFault(undefined) on program-apply OTP send

## Root cause
`ProgramPublicApplyModalComponent.sendOtpRequest()` calls `SignUpService.sendOTP()`. On failure, `sendOTP()`'s `catchError` did `console.warn(\`sendOTPFault( ${fault.error.message} )\`)` with no null-safety on `fault.error`. When the OTP-send backend/gateway returned an error body without a `.message` field (flaky Edge Mobile connection, India), that evaluated to `undefined`, producing the captured `sendOTPFault( undefined )` warning. The modal's own error handler had the identical gap and would have shown the applicant a raw "undefined" toast instead of a real message.

## Fix
- `sign-up.service.ts` — `fault.error.message` → `fault?.error?.message` in `sendOTP()`'s catchError log.
- `program-public-apply-modal.component.ts` — `err.error.message` → `err?.error?.message || 'Unable to send OTP. Please try again.'` in `sendOtpRequest()`'s error handler.

Both match the safe-access + fallback pattern already used elsewhere in the same files/service (`verifyOTP()`, `auth.service.ts`'s deactivate-account handler).

## Blast radius
None — purely additive null-safety on error handling for this one call chain. No controller/DTO/flag/tenant-scoping change.

## Verification
`npx tsc -p tsconfig.app.json --noEmit` clean. No automated test exists for this flow (workspace-wide guardrail — `guardian` skill not yet available); verification is static/type-check only.

## Related
See `sc-saas-frontend/src/app/modules/programs/module.spec.md` and `sc-saas-frontend/src/app/modules/auth/module.spec.md` ("Watch out for") for the documented fix. Superseded/extended by SAN-475 (same call chain, different fault message).
