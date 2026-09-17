---
id: SAN-579
title: Cannot read 'find' of null — corporate-intro edit step
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-579
sentry:
  - SC-SAAS-FRONTEND-BP
repos: [frontend]
commit: sc-saas-frontend@3e82ce59 (branch ai_native_setup_vishali, not pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-579 — find-on-null in corporate-intro

## Root cause
`corporate-intro.component.ts`'s `getCorporateInfo()` (line 282) declares `let sectoralInterestSubCategoryIds;` (unassigned) and only sets it inside an `if (response?.data?.sectoralInterestIds)` block from a nullable API field. The `this.industries.forEach(...)` block containing `.find()` on this variable runs unconditionally on every store emission, so a `null`/not-yet-populated value throws exactly the reported error.

## Fix
Guarded with optional chaining (`sectoralInterestSubCategoryIds?.find(...)`), matching the existing `ind.industrySubCategoryDomains?.length` guard style already used a few lines above in the same forEach.

## Blast radius
None — guard only; a populated array behaves identically.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean.
