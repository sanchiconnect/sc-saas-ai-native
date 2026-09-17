---
id: SAN-691
title: "investorDashboard( undefined ) — 4 unguarded fault.error.message sites"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-691
sentry:
  - SC-SAAS-FRONTEND-BM
repos: [frontend]
commit: sc-saas-frontend@25c98e52 (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-691 — investor-dashboard.service.ts 4 unguarded fault.error.message sites

## Root cause
`getInvestorDashboard()`, `sendApprovalRequest()`, `providingFunds()`, and `getInvestorCompleteness()` all did unguarded `fault.error.message` (no `?.` after `.error`) — the same crash class fixed earlier today in `mentorship.service.ts`/`search.service.ts` (SAN-610/620). The reported event logged "undefined" (fault.error was truthy but lacked `.message`, so it didn't crash this time), but the unguarded expression will throw a TypeError the moment `fault.error` is genuinely `null` (a real network-level/status-0 failure).

## Fix
Switched all 4 sites to the already-imported `httpFaultMessage(fault)` helper (already used correctly in this same file's `getIndividualInvestorCompleteness()`), for consistency and safety.

## Blast radius
None — diagnostic string only; toast/business logic in each method untouched.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.

## Related
SC-SAAS-FRONTEND-B4 (SAN-688) — same unguarded-pattern family, `sign-up.service.ts`.
