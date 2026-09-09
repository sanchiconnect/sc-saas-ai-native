---
id: SAN-723
title: "programs-details-page crashes reading startupId off null CURRENT_USER on ngOnInit"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-723
sentry:
  - SC-SAAS-FRONTEND-7M
repos: [frontend]
commit: sc-saas-frontend@07320233 (branch ai_native_setup_vishali, pushed)
created: 2026-09-09
updated: 2026-09-09
---

# SAN-723 — programs-details-page crashes reading startupId off null CURRENT_USER

## Root cause
`programs-details-page.component.ts:88` (`ngOnInit`) read `this.modalHandler.CURRENT_USER.startupId` with no optional chaining:
```ts
ngOnInit(): void {
  this.startupId=this.modalHandler.CURRENT_USER.startupId;
```
`ModalHandlerService.CURRENT_USER` is explicitly typed `IProfileDetails | null` and is populated asynchronously from an NgRx store subscription (`initStoreSubscriptions()` → `getProfileData`). On this page it's read synchronously in `ngOnInit`, before that subscription has necessarily emitted — the same race class already fixed elsewhere in the codebase for `profileDetails` (see the SC-SAAS-FRONTEND-3D guard in `program-public-apply.component.ts`). 4 production users hit this over 3+ weeks (mobile Safari/Chrome iOS), most recently 2026-09-08.

A second, identically-unguarded call site was found during investigation (not yet in Sentry's own top list, but same root cause, same fix):
- `program-details-top-bar.component.ts:220` (`onEnableApplication()`) — `this.modalHandler.CURRENT_USER.startupId`

## Fix
Both sites changed to optional chaining, matching the guarded pattern already used elsewhere in this codebase (`upload-pitch.component.ts:79,119`, `billing-form.component.ts:147`):
```ts
this.startupId = this.modalHandler.CURRENT_USER?.startupId;
```
```ts
"startupId": this.modalHandler.CURRENT_USER?.startupId,
```
`startupId` is already declared `startupId = null;` at the class level, so this preserves existing behavior for the not-yet-loaded case (resolves to `undefined`, same falsy value as before) — no downstream logic change, no API/DTO/flag/tenant-scoping impact.

## Blast radius
`sc-saas-frontend` only, both sites inside the `programs-details-page` module. No shared/service code touched.

## Verification
No existing `.spec.ts` covers either component (workspace-wide test blocker per CLAUDE.md — no `guardian` skill yet, so tests-first is substituted with the strongest available check). Ran `npx tsc --noEmit -p tsconfig.app.json` — clean, no errors. Manually traced every downstream use of `this.startupId` in `programs-details-page.component.ts` (`checkPricingDetails`, the `applicantId` payload field, `getPreviousOrder`) — all treat it as a plain passthrough value, so `undefined` behaves identically to `null`/the already-working case.

Vishali verified locally, then committed and pushed as `sc-saas-frontend@07320233` on `ai_native_setup_vishali`. Linear moved to Done. Sentry SC-SAAS-FRONTEND-7M marked resolved with a comment referencing the commit — note this branch is still behind `main` (per the workspace's known frontend deploy lag, tracked separately in SAN-589), so the fix won't reach production until the next deploy.
