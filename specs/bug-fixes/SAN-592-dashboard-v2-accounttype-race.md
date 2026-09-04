---
id: SAN-592
title: Cannot read properties of undefined (reading 'accountType') — dashboard-v2 profileCompleteness$/profileData race
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-592
sentry:
  - SC-SAAS-FRONTEND-48
  - SC-SAAS-FRONTEND-CC
repos: [frontend]
commit: sc-saas-frontend@b0c01ada (branch ai_native_setup_vishali, pushed)
created: 2026-09-04
updated: 2026-09-04
---

# SAN-592 — dashboard-v2 profileCompleteness$/profileData race

## Root cause
`DashboardV2Component.fetchData()` runs two independent async subscriptions with no ordering guarantee: `getProfileData$` (`dashboard-v2.component.ts:232-245`) sets `this.profileData`, and `profileService.profileCompleteness$` (lines 272-282) reads `this.profileData.accountType` at line 277 with no guard. If `profileCompleteness$` emits first, `this.profileData` is still `undefined` and the read throws. Same "counts race" bug class as SAN-588 — that fix's own description flagged this file as having other unguarded profile-race reads not covered by it. SC-SAAS-FRONTEND-48 and -CC are almost certainly the same event under two different webpack chunk-hash fingerprints across deploys.

Lines 344 and 357 in the same file also read `this.profileData.accountType` unguarded but are inside `prepareCountBoxes()`, which already checks `if (this.brandDetails && this.profileData)` before reaching them — not affected.

## Fix
`this.profileData?.accountType === ACCOUNT_TYPE.STARTUP` at line 277 — matches the optional-chaining convention already used elsewhere in the same file (lines 151, 194, 262, 453) for the identical race.

## Blast radius
None on the happy path — `openProfileModal()` simply doesn't fire on this particular emission if `profileData` isn't loaded yet; still fires correctly on the next `profileCompleteness$` emission once both subscriptions have resolved.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean on the changed file (baseline `.spec.ts` noise only). No automated test suite exists for this repo.

## Related
Same bug class as SAN-588 (service-provider-dashboard counts race) and SAN-483/SAN-512 (dashboard-v2/connection-v4 families).
