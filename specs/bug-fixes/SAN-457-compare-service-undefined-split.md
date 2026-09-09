---
id: SAN-457
title: TypeError — undefined.split in CompareService.compareStartups (11 events)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-457
sentry:
  - SC-SAAS-BACKEND-1K
repos: [backend]
commit: sc-saas-backend@2e01d244 (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-21
---

# SAN-457 — undefined.split in CompareService

## Root cause
`public/compare` routes have no auth guard. `@Query('ids') ids: string` in `compare.controller.ts:52` passes `undefined` to the service when the `ids` query param is missing. Both `compareStartups` and `compareInvestors` called `.split()` directly on the param without a null guard.

## Fix
Added missing-param guards in `compare.service.ts` before both `.split()` calls:
- `compareStartups`: `if (!ids) throw new BadRequestException(ApiErrors.PLEASE_CHOOSE_SOME_STARTUPS_TO_COMPARE);`
- `compareInvestors`: `if (!ids) throw new BadRequestException(ApiErrors.PLEASE_CHOOSE_SOME_INVESTORS_TO_COMPARE);`

## Blast radius
None — returns 400 instead of 500 for callers who omit `ids`. Frontend already handles this (it always sends ids), so no frontend change needed.

## Verification
`tsc --noEmit --skipLibCheck` clean. Committed `2e01d244`.
