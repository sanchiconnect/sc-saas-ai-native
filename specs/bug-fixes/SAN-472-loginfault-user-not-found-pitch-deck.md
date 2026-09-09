---
id: SAN-472
title: "loginFault: User not found on pitch-deck fetch — mislabeled, expected-condition logging"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-472
sentry:
  - SC-SAAS-FRONTEND-7K
repos: [frontend]
commit: none (no code change)
created: 2026-08-20
updated: 2026-08-20
---

# SAN-472 — loginFault: User not found on pitch-deck fetch

## Root cause
Not a bug. `loginFault( User not found. Please check your input )` fired from `PitchDeckService.getPitchInfo()`/`getStartupPitchByUUID()` (`pitch-deck-record.service.ts`) on the pitch-deck edit page — `loginFault` is a copy-pasted `console.warn` label reused across ~20 unrelated service files, same mislabeling class as the `Jobs(` prefix documented in SAN-448. The handler's `getErrorMessage()` already correctly extracts the real backend message and shows it via toast — the app behaved correctly. Single occurrence, no recurrence in 6 days.

## Fix
None applied. This matches the already-documented pattern in SAN-471 (already-handled/already-toasted errors re-logged via `console.warn`, which `main.ts` deliberately forwards to Sentry as the app's only production logging pillar).

## Decision
No code change — closing as verified-expected, consistent with the same conclusion reached for SAN-211/215/217 (near-identical `loginFault(...)`/`startupinfoFault(...)`/`verifyOTPFault(...)` "verify if expected-condition logging" tickets). The `loginFault(` mislabeling itself is real but shared across ~30 call sites in ~20 files — not fixed piecemeal here (same non-scalable trap SAN-471 explicitly warns against); tracked at the class level via SAN-448/SAN-471.

## Blast radius
None — no code touched.

## Verification
Read-through of `pitch-deck-record.service.ts`'s `getErrorMessage()` confirms correct message extraction for the standard NestJS error body shape (`{statusCode, message, error}`).

## Related
See `sc-saas-frontend/src/app/modules/startups/module.spec.md` ("Watch out for") for the documented finding.
