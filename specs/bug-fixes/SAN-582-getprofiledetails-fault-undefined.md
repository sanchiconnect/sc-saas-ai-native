---
id: SAN-582
title: "getProfileDetails Fault(undefined) — real diagnostics bug per SAN-471"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-582
sentry:
  - SC-SAAS-FRONTEND-6Y
repos: [frontend]
commit: sc-saas-frontend@9d186afc (branch ai_native_setup_vishali, not pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-582 — getProfileDetails Fault(undefined) diagnostics gap

## Root cause
`profile.service.ts`'s `getProfileDetails()` (line 95) logged `` console.warn(`getProfileDetails Fault( ${fault.error?.message} )`) `` — same class as SAN-581/SAN-583, explicitly named in SAN-471 (Done) as a real diagnostics bug, not noise.

## Fix
Wired in the existing `httpFaultMessage()` helper: `` fault.error?.message `` → `` httpFaultMessage(fault) ``. This is the only method in the file whose warn label reads "getProfileDetails Fault" — unambiguous match. Toast/redirect logic untouched.

## Blast radius
None — diagnostic string only.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean.

## Related
SAN-471, SAN-581, SAN-583 (same fix pattern/helper).
