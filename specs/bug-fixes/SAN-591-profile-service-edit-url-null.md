---
id: SAN-591
title: Cannot read properties of null (reading 'accountType') — ProfileService.getEditProfileUrl called before profile loads
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-591
sentry:
  - SC-SAAS-FRONTEND-C0
repos: [frontend]
commit: sc-saas-frontend@467e1979 (branch ai_native_setup_vishali, pushed)
created: 2026-09-04
updated: 2026-09-04
---

# SAN-591 — ProfileService.getEditProfileUrl null profileData

## Root cause
`ProfileService.profileData` (`profile.service.ts:59`) is assigned unconditionally from the `getProfileData` NgRx selector subscription (`profile.service.ts:66-67`, no `if (res)` guard on the assignment itself). `getEditProfileUrl()` (lines 490-517) reads `this.profileData.accountType` immediately with no null check. Called from `DashboardV2Component.handleEditProfile()` (`dashboard-v2.component.ts:337`) on the "Edit Profile" click — if the profile selector hasn't emitted yet, this throws.

## Fix
Added an early guard: `if (!this.profileData) { return profileEditPageUrl; }` (returns `undefined`) — mirrors the function's own existing fallback for the `ACCOUNT_TYPE.OTHER` branch, which already returns `undefined` for an unhandled case. No new failure mode introduced.

## Blast radius
None — only changes the crash case (profile not loaded) from throwing to a no-op navigation, same as the existing unhandled-account-type path.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean on the changed file (baseline `.spec.ts` noise only). No automated test suite exists for this repo.
