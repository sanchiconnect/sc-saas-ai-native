---
id: SAN-505
title: getProfileViewers throws bare Error for missing profile owner — 500 instead of 404
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-505
sentry:
  - SC-SAAS-BACKEND-21
repos: [backend]
commit: 899ed2d2 (branch ai_native_setup_aman)
created: 2026-08-25
updated: 2026-08-25
---

# SAN-505 — getProfileViewers bare Error → 500 in Sentry

## Root cause
`getProfileViewers()` in `user.repository.ts:1235` throws `new Error(...)` (a bare JS Error, not
a NestJS `HttpException`) when `getParentUserByProfileType()` returns null — meaning the startup,
investor, corporate, or mentor record has no associated owner user. NestJS's global exception filter
wraps an unrecognised Error as 500 `InternalServerErrorException`, which Sentry captures.

Startup ID 33 has no owner user (orphaned record or deleted user) — this triggered the single event.

## Fix
Two changes in `user.repository.ts`:
1. Added `NotFoundException` to the `@nestjs/common` import.
2. Replaced `throw new Error(...)` with `throw new NotFoundException(...)` at line 1235.

NestJS recognises `NotFoundException` as a 404 HTTP exception — the exception filter returns 404 to
the caller cleanly, and Sentry does not capture it as an unexpected error.

## Data note
Startup ID 33 with no owner user should be investigated via admin panel and either reassigned or
soft-deleted.

## Blast radius
Callers of `GET /api/v1/user/profile-viewers` now receive 404 (not 500) for profiles with no owner
user. Frontend should handle 404 gracefully on the profile viewers page.

## Verification
`tsc --noEmit --skipLibCheck` clean. No commit/push until Aman confirms.
