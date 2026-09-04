---
id: SAN-608
title: "verifyOTPFault(OTP expired) re-thrown to Sentry — 6 users, 7 events"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-608
sentry:
  - SC-SAAS-FRONTEND-34
repos: [frontend]
commit: sc-saas-frontend@4e4bd3cb (branch ai_native_setup_vishali, pushed)
created: 2026-09-04
updated: 2026-09-04
---

# SAN-608 — verifyOTPFault(OTP expired) re-thrown to Sentry

## Investigation — not a code defect
Same `SignUpService.verifyOTP()` catch path as SAN-599, just a different message ("OTP expired" vs "Invalid OTP") from the same already-handled fault class.

## Fix
Same `main.ts:109` `HANDLED_HTTP_FAULT` regex extension as SAN-599/600/601.

## Blast radius
None.

## Verification
`npx tsc --noEmit` clean.

## Related
SC-SAAS-FRONTEND-2Q (SAN-599), SC-SAAS-FRONTEND-4K (SAN-600), SC-SAAS-FRONTEND-3H (SAN-601) — same fix, same commit.
