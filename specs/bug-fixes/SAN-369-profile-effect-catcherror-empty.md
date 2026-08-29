---
id: SAN-369
title: getProfileTypes$ NgRx effect dies permanently on a 404, and reports it to Sentry
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-369
sentry:
  - SC-SAAS-FRONTEND-H
repos: [frontend]
commit: sc-saas-frontend@c0638d20 (branch ai_native_setup_aman)
created: 2026-08-19
updated: 2026-08-19
---

# SAN-369 — getProfileTypes$ effect unhandled error

## Root cause
Actual error: `HttpErrorResponse` — `GET .../api/v1/users/profile-types → 404 Not Found`. Traced to the backend: `UserService.getUserProfiles()` throws `NotFoundException` only when the JWT's `session.userId` no longer matches any `users` row — a stale-but-signature-valid session cookie surviving account deletion. `GetProfileTypes` is dispatched unconditionally for every logged-in user, every account type, 2 seconds after every page load (`app.component.ts:164`), explaining the 100-user count.

The real bug on the frontend side: `getProfileTypes$` (`profile.effect.ts`) had NO `catchError` in its inner pipe at all — an NgRx effect that errors without `catchError` doesn't just report once, it permanently terminates that effect stream app-wide until the page reloads.

## Fix
Added `catchError(() => EMPTY)` to the effect's inner pipe. Deliberately did **not** reuse the existing `ProfileFault` action (used by the sibling `getProfileData$` effect) — its reducer case sets `profileData: null`, which would wipe unrelated already-loaded profile state on every profile-types failure. `EMPTY` stops the stream from dying without touching any other state.

## Blast radius
None — grepped the whole repo for `ofType(GetProfileTypesSuccess)`; nothing else waits on this action besides the reducer. `exhaustMap` re-arms correctly on the next dispatch.

## Decision
Backend 404 semantics (stale session vs. returning `[]` like the sibling `parentUser`-not-found case) intentionally left unchanged — product decision, 2026-08-19: leave as-is for now.

## Verification
`tsc --noEmit` clean.
