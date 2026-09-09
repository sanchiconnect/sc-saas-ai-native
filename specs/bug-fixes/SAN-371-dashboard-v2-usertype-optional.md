---
id: SAN-371
title: dashboard-v2 userType.type read before profile stream resolves
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-371
sentry:
  - SC-SAAS-FRONTEND-30
repos: [frontend]
commit: sc-saas-frontend@c0638d20 (branch ai_native_setup_aman)
created: 2026-08-19
updated: 2026-08-19
---

# SAN-371 — dashboard-v2 userType TypeError

## Root cause
`dashboard-v2.component.html` reads `userType.type`/`userType.label` in the search-bar placeholder binding before `userType` is assigned (set inside a `getProfileData$` subscription in `fetchData()`). The surrounding block is gated only by an independent `brandDetails` stream, which frequently resolves first — matches the high frequency (45 users, 338 events).

## Fix
Changed to `userType?.type`/`userType?.label` with a fallback empty string for the label interpolation.

## Blast radius
None — `userType` is purely local to this component's search bar; the only other unguarded read (`dashboard-v2.component.ts:442`) is inside an `if (this.userType)` check and can't execute when undefined.

## Verification
`tsc --noEmit` clean (template-only change, verified via full-repo grep for other unguarded reads).
