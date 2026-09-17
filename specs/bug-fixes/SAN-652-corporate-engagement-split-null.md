---
id: SAN-652
title: "TypeError: Cannot read properties of null (reading 'split') in corporate-engagement.component"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-652
sentry:
  - SC-SAAS-FRONTEND-B9
repos: [frontend]
commit: sc-saas-frontend@d613a0e1 (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-652 — corporate-engagement.component split() on null connectionRequirements

## Root cause
`getCorporateInfo()` destructures `connectionRequirements` straight off `response.data` and calls `.split(',')` with no null guard. Throws when a corporate hasn't set connection requirements yet (field is `null`).

## Fix
Changed to `(connectionRequirements || '').split(',').filter(...)`.

## Blast radius
None — a `null` value now produces an empty selected-reasons list instead of crashing; identical behavior to submitting no requirements.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.
