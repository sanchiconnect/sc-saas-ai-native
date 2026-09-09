---
id: SAN-463
title: TypeError — null.id in AuthService.generateAccessToken (3 events)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-463
sentry:
  - SC-SAAS-BACKEND-1M
repos: [backend]
commit: sc-saas-backend@2e01d244 (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-21
---

# SAN-463 — null user in generateAccessToken()

## Root cause
`generateAccessToken()` in `auth.service.ts` accessed `user.id` without a null guard. `verifyUser()` calls `getUserByMobileNumber()` which returns `null` when no user exists, then passes that `null` directly to `generateAccessToken()`, crashing as a 500 instead of a clean 401.

## Fix
1. Added `UnauthorizedException` to the `@nestjs/common` import.
2. Added null guard at the top of `generateAccessToken()`:
```ts
if (!user) throw new UnauthorizedException(ApiErrors.USER_NOT_FOUND);
```
This protects all 9 callers of `generateAccessToken` in a single place.

## Blast radius
Callers that previously got a 500 now get a 401 — correct behavior. No API contract change (error status code improvement only).

## Verification
`tsc --noEmit --skipLibCheck` clean. Committed `2e01d244`.
