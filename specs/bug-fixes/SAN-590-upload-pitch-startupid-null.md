---
id: SAN-590
title: Cannot read properties of null (reading 'startupId') — UploadPitchComponent.handlePowerPitchConnect race
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-590
sentry:
  - SC-SAAS-FRONTEND-CB
repos: [frontend]
commit: sc-saas-frontend@d5c72753 (branch ai_native_setup_vishali, pushed)
created: 2026-09-04
updated: 2026-09-04
---

# SAN-590 — upload-pitch handlePowerPitchConnect race

## Root cause
`UploadPitchComponent.handlePowerPitchConnect()` (`upload-pitch.component.ts:67-90`) and `fetchVideo()` (lines 110-137) read `this.modalHandler.CURRENT_USER.startupId` and `this.profileData.name`/`.email` with no guard. `ModalHandlerService.CURRENT_USER` starts `null` and only populates via an async subscription (`modal-handler.service.ts:24,52`); `profileData` is likewise set asynchronously in `ngOnInit` (line 42). A user triggering "connect power pitch" before either resolves hits the crash.

## Fix
Optional-chained both reads (`this.modalHandler.CURRENT_USER?.startupId`, `this.profileData?.name`, `this.profileData?.email`) — matches the optional-chaining convention already used elsewhere in this codebase for async-populated profile/user fields.

## Blast radius
None on the happy path — same values once the async subscriptions resolve.

## Verification
`npx tsc -p tsconfig.json --noEmit` — no new errors on the changed file (only pre-existing `.spec.ts` jasmine-typings baseline noise elsewhere). No automated test suite exists for this repo.

## Related
Same file/root-cause class as SC-SAAS-FRONTEND-C3 ("reading 'name' of undefined" at the same `handlePowerPitchConnect`), not part of this batch but sharing the identical guard gap — worth a follow-up if it recurs.
