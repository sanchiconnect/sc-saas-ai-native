---
id: SAN-673
title: "sign-up.service.ts diagnostic-message hardening (3 sites: verifyOTP, registerUser/registerOtherUser, sendOTP)"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-673
sentry:
  - SC-SAAS-FRONTEND-9Y
  - SC-SAAS-FRONTEND-B4
  - SC-SAAS-FRONTEND-BC
repos: [frontend]
commit: sc-saas-frontend@145e8699 (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-673 / SAN-688 / SAN-692 — sign-up.service.ts diagnostic-message hardening

Three distinct Linear tickets share one commit because all three fixes land in the same file and were found together while auditing it.

## Root cause
- **SAN-673** (`verifyOTP()`): `fault.error?.message` was null-safe but had no `|| fault.message || fault.status` fallback — logged "undefined" for a network-level failure.
- **SAN-688** (`registerUser()`/`registerOtherUser()`): both did unguarded `fault.error.message` (no `?.` after `.error`) — the same crash class fixed elsewhere today (SAN-610/620/661/691). Didn't crash in the reported event only because `fault.error` happened to be non-null that time; remained a latent crash risk.
- **SAN-692** (`sendOTP()`): `` fault?.error?.error?.[0] || fault?.error?.message `` indexed `[0]` without checking `Array.isArray()` first. NestJS's default HTTP-exception `error` field is normally a plain string exception name (e.g. "Bad Request"), not an array — indexing `[0]` on a string returns just its first character, producing garbled 1-letter diagnostic messages (e.g. `sendOTPFault( c )`). Confirmed against the sibling `http-fault.util.ts`'s `httpFaultMessage()`, which correctly checks `Array.isArray()` before indexing. Log-only — the actual user-facing toast already goes through `sign-up.effect.ts` → `httpFaultMessage()`, which was already correct.

## Fix
- `verifyOTP()`: added `|| fault.message || fault.status` fallback.
- `registerUser()`/`registerOtherUser()`: changed to `fault?.error?.message || fault?.message || fault?.status`.
- `sendOTP()`: changed to `` Array.isArray(fault?.error?.error) ? fault.error.error[0] : fault?.error?.message ``.

## Blast radius
None — all three are diagnostic-string-only changes; no user-facing toast or business logic affected.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.
