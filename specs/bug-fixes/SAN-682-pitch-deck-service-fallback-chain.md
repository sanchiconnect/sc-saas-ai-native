---
id: SAN-682
title: "update PitchFile Info( undefined ) — missing fallback chain in pitch-deck.service"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-682
sentry:
  - SC-SAAS-FRONTEND-5X
repos: [frontend]
commit: sc-saas-frontend@eeefb49b (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-682 — pitch-deck.service diagnostic message missing fallback chain

## Root cause
`uploadPitchFile()`'s `fault?.error?.message` was already null-safe but had no `|| fault.message || fault.status` fallback, logging "undefined" for an empty/non-JSON error body.

## Fix
Added `|| fault.message || fault.status`.

## Blast radius
None — diagnostic string only.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.

## Related
Same missing-fallback pattern as SAN-673 and SAN-683.
