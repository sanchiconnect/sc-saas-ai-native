---
id: SAN-683
title: "foundersFault( undefined ) — missing fallback chain in founders.service"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-683
sentry:
  - SC-SAAS-FRONTEND-7E
repos: [frontend]
commit: sc-saas-frontend@01597391 (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-683 — founders.service diagnostic message missing fallback chain

## Root cause
`getFounders()`'s `fault?.error?.message` was already null-safe (no crash) but had no `|| fault.message || fault.status` fallback, so a network-level failure with no parseable error body logged the useless literal "undefined" instead of a real diagnostic.

## Fix
Added `|| fault.message || fault.status`, matching the pattern already used in sibling services (e.g. `startup.service.ts`).

## Blast radius
None — diagnostic string only.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.

## Related
SC-SAAS-FRONTEND-9Y (SAN-673) and SC-SAAS-FRONTEND-5X (SAN-682) — same missing-fallback pattern in different files.
