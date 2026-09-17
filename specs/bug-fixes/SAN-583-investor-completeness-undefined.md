---
id: SAN-583
title: "getIndividualInvestorCompleteness(undefined) — likely same diagnostics-logging bug"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-583
sentry:
  - SC-SAAS-FRONTEND-80
repos: [frontend]
commit: sc-saas-frontend@dc35f0a6 (branch ai_native_setup_vishali, not pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-583 — getIndividualInvestorCompleteness(undefined) diagnostics gap

## Root cause
`investor-dashboard.service.ts`'s `getIndividualInvestorCompleteness()` (line 125) logged `` console.warn(`getIndividualInvestorCompleteness( ${fault.error.message} )`) `` — same `(undefined)` diagnostics-gap class as SAN-581/SAN-582.

The literal warn string "getIndividualInvestorCompleteness" is also copy-pasted (stale) into 5 unrelated services (`service-provider.service.ts:105`, `program-office.service.ts:106`, `mentors.service.ts:107`, `individual-profile.service.ts:108`, `corporate.service.ts:105`) — `investor-dashboard.service.ts` is the only file where a method actually named `getIndividualInvestorCompleteness()` exists, confirmed as the truthful match rather than a mislabeled copy. Left the other 5 stale-labeled sites untouched — they belong to different completeness endpoints and weren't named in this ticket.

## Fix
Wired in the existing `httpFaultMessage()` helper: `` fault.error.message `` → `` httpFaultMessage(fault) ``. Toast/redirect logic untouched.

## Blast radius
None — diagnostic string only.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean.

## Related
SAN-471, SAN-581, SAN-582 (same fix pattern/helper). The 5 sibling stale-labeled sites noted above may warrant their own follow-up ticket if/when those endpoints show the same `(undefined)` symptom.
