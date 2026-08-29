---
id: SAN-461
title: TypeError — null.map on startupBusinessModels/startupIndustries in InvestorService (4 events)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-461
sentry:
  - SC-SAAS-BACKEND-C
repos: [backend]
commit: sc-saas-backend@2e01d244 (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-21
---

# SAN-461 — null.map on TypeORM relations in getRecommendedStartups

## Root cause
`getRecommendedStartups()` in `investor.service.ts` called `.map()` directly on `startupBusinessModels` and `startupIndustries` relations. TypeORM returns `null` (not `[]`) for these relations when no join rows exist, causing `TypeError: Cannot read properties of null (reading 'map')`.

## Fix
Added `?? []` null-coalescing before each `.map()` at lines 877 and 886:
```ts
const startupBusinessModelIds = (startups.items[i].startupBusinessModels ?? []).map(...)
const startupIndustryIds = (startups.items[i].startupIndustries ?? []).map(...)
```

## Blast radius
None — investor-service internal; recommended-startups response shape unchanged.

## Verification
`tsc --noEmit --skipLibCheck` clean. Committed `2e01d244`.
