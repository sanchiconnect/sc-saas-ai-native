---
id: SAN-599
title: "verifyOTPFault(Invalid OTP) re-thrown to Sentry — 71 users, 79 events"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-599
sentry:
  - SC-SAAS-FRONTEND-2Q
repos: [frontend]
commit: sc-saas-frontend@4e4bd3cb (branch ai_native_setup_vishali, pushed)
created: 2026-09-04
updated: 2026-09-04
---

# SAN-599 — verifyOTPFault(Invalid OTP) re-thrown to Sentry

## Investigation — not a code defect
`SignUpService.verifyOTP()`'s `catchError` block already `console.warn`s and `this.toastService.showToast(...)`s this exact fault, and the calling component (`register.component.ts`) has its own `verifyOtpError` subscription that toasts `OTP verified fail. ${res}` on top of that — the error is fully caught and surfaced to the user end-to-end. The `console.warn` line is what Sentry's `captureConsoleIntegration({ levels: ['warn'] })` in `main.ts` was picking up and reporting as a second, redundant event. Same class as the SAN-504 (401/403 mentorship-hours) fix already landed in this repo.

## Fix
Extended the `HANDLED_HTTP_FAULT` regex in `main.ts:109` (the same allowlist SAN-504 added `Invalid access token`/`Forbidden resource` to) with this fault's exact message text, so Sentry's `beforeSend` hook now drops it as a known-handled warning instead of reporting it.

## Blast radius
None on functionality — the toast/console.warn/error-callback path is completely unchanged. Only effect is fewer duplicate Sentry events for an error users already see a proper message for.

## Verification
`npx tsc --noEmit` clean. Grepped `auth.service.ts`/`register.component.ts` to confirm the fault is genuinely caught before assuming this was over-logging rather than a real bug.

## Related
SC-SAAS-FRONTEND-3H (SAN-601), SC-SAAS-FRONTEND-34 (SAN-608), SC-SAAS-FRONTEND-4K (SAN-600) — same fault-class fix, same commit.
