---
id: SAN-620
title: "searchStartUp Fault(undefined) — null error object reaching fault handler"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-620
sentry:
  - SC-SAAS-FRONTEND-BZ
repos: [frontend]
commit: sc-saas-frontend@79d94bd2 (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-620 — search.service.ts fault.error.message null crash, 15 occurrences

## Root cause
Same anti-pattern as SAN-610: `catchError` handlers logged `` fault.error.message `` without optional chaining. Turned out to be copy-pasted across **15 methods** in `search.service.ts`, not just the one reported (`searchStartUp`): `searchStartUp`, `searchStartUpByName`, `searchInvestor` (×2), `searchCorporates`/`searchCorporate`, `searchMentor` (×4), `searchPartners`, `searchPartnerByName`, `searchServiceProviderByName` (×2), `searchLiveDeals`.

## Fix
Replaced all 15 occurrences of `fault.error.message` with `fault?.error?.message` in one sweep — identical trivial change throughout the file. No change to happy-path search behavior.

## Blast radius
None — diagnostic string only, same class of fix as SAN-610.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — same regression-test proposal as SAN-610 (mock `HttpErrorResponse` with `error: null`) applies here, pending go-ahead.

## Related
SAN-610 (same anti-pattern and fix, `mentorship.service.ts`).
