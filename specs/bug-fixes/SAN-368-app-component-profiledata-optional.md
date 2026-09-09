---
id: SAN-368
title: app.component profileData.accountType read before profile stream resolves
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-368
sentry:
  - SC-SAAS-FRONTEND-92
repos: [frontend]
commit: sc-saas-frontend@c0638d20 (branch ai_native_setup_aman)
created: 2026-08-19
updated: 2026-08-19
---

# SAN-368 — app.component accountType TypeError

## Root cause
`app.component.ts` constructor subscribes to `profileCompleteness$` and reads `this.profileData.accountType` — but `this.profileData` is assigned by a separate, unordered `getProfileData$` subscription. If `profileCompleteness$` emits first, `profileData` is still undefined.

## Fix
Changed to `this.profileData?.accountType` — matches the existing convention already used elsewhere in this same class (`isAllowedAccountType()`, `prepareCountBoxes()`).

## Blast radius
None — `formsManagementService.getFormsList(userType?: string)` already treats its parameter as optional and falls back to listing all forms when undefined.

## Verification
`tsc --noEmit` clean.
