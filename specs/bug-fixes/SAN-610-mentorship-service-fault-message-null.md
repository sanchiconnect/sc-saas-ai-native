---
id: SAN-610
title: "TypeError: Cannot read properties of null (reading 'message') in mentorship.service.ts"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-610
sentry:
  - SC-SAAS-FRONTEND-CH
repos: [frontend]
commit: sc-saas-frontend@80f292df (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-610 — mentorship.service.ts fault.error.message null crash

## Root cause
`catchError` handlers in `mentorship.service.ts` logged `` console.warn(`Jobs( ${fault.error.message} )`) `` without optional chaining, in **4 methods** — not just the one reported at line 74. The adjacent toast-message line in each method already used the safe `fault?.error?.message` form. When `fault.error` is null (e.g. a network/CORS error with no JSON body), the unguarded `console.warn` line threw before the safe line ever ran.

## Fix
Replaced all 4 occurrences of `fault.error.message` with `fault?.error?.message` to match the adjacent toast line. No behavior change on the normal error path.

## Blast radius
None — diagnostic string only, same pattern as SAN-582/SAN-581/SAN-583.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — proposed a regression test (mock `HttpErrorResponse` with `error: null`) pending go-ahead; not yet written.

## Related
SAN-620 (same anti-pattern, 15 occurrences in `search.service.ts`), SAN-582/SAN-581/SAN-583 (same fix pattern in other services).
