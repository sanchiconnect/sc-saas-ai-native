---
id: SAN-462
title: TypeError — null.investor/startup/etc in getOrganizationName (5 events)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-462
sentry:
  - SC-SAAS-BACKEND-1D
repos: [backend]
commit: sc-saas-backend@2e01d244 (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-21
---

# SAN-462 — null relation access in getOrganizationName / getOrganizationZohoAccountId

## Root cause
`getOrganizationName()` and `getOrganizationZohoAccountId()` in `src/core/utils/app.utils.ts` accessed profile relations directly (e.g. `user.investor.organizationName`) without optional chaining. When the relation is not eager-loaded on the user object, the access throws `TypeError`.

## Fix
Added `?.` optional chaining and `?? ''` fallback to all 8 relation accesses in both functions (startup, investor, corporate, mentor, service_provider, partner, program_office, individual cases):
```ts
// Before
organizationName = user.investor.organizationName;
// After
organizationName = user.investor?.organizationName ?? '';
```

## Blast radius
None — utility function only; callers receive `''` instead of crashing on a missing relation.

## Verification
`tsc --noEmit --skipLibCheck` clean. Committed `2e01d244`.
