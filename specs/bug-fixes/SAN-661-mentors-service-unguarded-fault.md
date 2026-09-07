---
id: SAN-661
title: "TypeError: Cannot read properties of null (reading 'message') in mentors.service.ts — 4 unguarded sites"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-661
sentry:
  - SC-SAAS-FRONTEND-4M
repos: [frontend]
commit: sc-saas-frontend@0f9acb43 (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-661 — mentors.service.ts 4 unguarded fault.error.message sites

## Root cause
`getMentorProfileCompleteness()`, `sendApprovalRequest()`, `getMentorPublicProfileData()`, and `getMentorDashboard()` all did unguarded `fault.error.message` — the same crash class fixed earlier today in `mentorship.service.ts`/`search.service.ts` (SAN-610/620). This file was never touched by those fixes (confirmed via `git log`).

## Fix
Guarded all 4 sites with `fault?.error?.message`.

## Blast radius
None — diagnostic string only.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.
