---
id: SAN-561
title: "NG01002: missing value for form control 'ticketSizeMin'"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-561
sentry:
  - SC-SAAS-FRONTEND-61
repos: [frontend]
commit: sc-saas-frontend@63de8454 (branch ai_native_setup_vishali, not pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-561 — NG01002 on ticketSizeMin

## Root cause
The ticket's own hypothesis (a conditionally-registered `ticketSizeMin` control) didn't match the code: `ticketSizeMin` is always registered in `investmentForm` and always rendered. The real crash is in `investments-details.component.ts`'s `getInvestorOrganizationInfo()`, which calls `this.investmentForm.setValue({ turnAroundTime, ticketSizeMin, ticketSizeMax })`. Angular's `FormGroup.setValue()` throws `NG01002` if any supplied key resolves to `undefined`. `getTransformedVal(val)` (~line 163) only had a truthy branch (`if (val) return transform(...)`) and implicitly returned `undefined` otherwise — so a new investor who hasn't set `ticketSizeMin` yet (null/undefined from the API) fed `setValue` an `undefined` value and crashed.

## Fix
Added `return val ?? '';` as the fallback branch of `getTransformedVal`, guaranteeing `setValue` always receives a defined value.

## Blast radius
None — only affects the previously-crashing undefined case; existing truthy values behave identically.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean.
