---
id: SAN-730
title: "Make State/City conditionally required based on available options (all stakeholder edit forms)"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-730
sentry: []
repos: [frontend]
commit: sc-saas-frontend@7d9e3cc7 (branch ai_native_setup_vishali, pushed)
created: 2026-09-09
updated: 2026-09-09
---

# SAN-730 — State/City conditionally required across all stakeholder edit forms

## Requirement
Across every stakeholder profile edit form, the Country/State/City location picker had Country as the only required field — State and City were always optional, even for countries where state/city data exists and a real choice is expected (e.g. India). Requested behavior: Country stays required; State becomes required only when the states list returned for the selected country is non-empty; City becomes required only when the cities list returned for the selected state is non-empty. Countries with no state-level data (e.g. Aland Islands, per the reported screenshot) correctly keep State/City optional either way.

## Fix
In each affected component, `getStates()`/`getCities()` now toggle the control's validator based on the length of the list the API returns, then call `updateValueAndValidity()`:
```ts
getStates(cId: string) {
  this.globalService.getStates(cId).subscribe((res) => {
    this.states = res;
    const stateControl = this.<form>.get('registeredStateId');
    stateControl.setValidators(res?.length ? [Validators.required] : []);
    stateControl.updateValueAndValidity();
  })
}
```
(mirrored for `getCities()` / `registeredCityId`). Templates changed the static/commented-out red asterisk on the State and City labels to `*ngIf="states?.length"` / `*ngIf="cities?.length"`.

Applied identically to 11 components (`.ts` + `.html` each, 22 files):
- `startups/pages/edit/startup-information`
- `startups/components/edit-profile-modal/stepper/step-one-company-info`
- `mentors/pages/edit/mentor-intro`
- `investors/pages/edit/organization-details`
- `investors/pages/edit/individual-investor-edit-form`
- `service-provider/pages/edit/service-provider-intro`
- `program-office/edit/program-office-intro`
- `partners-dashboard/pages/edit/partner-intro`
- `corporate/pages/edit/corporate-intro`
- `individual-profile/pages/individual-profile-edit-form`
- `programs/programs-details-page/startup-all-required-details-form`

Every one of these forms already declared `registeredStateId`/`registeredCityId` with an empty validator array (`new FormControl(null, [])`) and no other validators, so `setValidators()` can't be clobbering anything else on those controls.

## Blast radius
`sc-saas-frontend` only. No API/DTO, flag, or tenant-scoping impact — purely client-side form validation. No shared/service code touched (each component owns its own form group; there is no common location-picker component in this codebase to change once).

## Verification
Ran `npx tsc -p tsconfig.app.json --noEmit` — clean, no errors, across the whole app build.

No `.spec.ts` exists for any of the 11 components; per the workspace's bug-fix flow, a regression test was proposed to the user (assert `registeredStateId` becomes required after `getStates()` resolves a non-empty list, and stays optional for an empty list) but not yet written — waiting on explicit go-ahead before adding it.

Manually traced the full flow on `startup-information.component.ts` to confirm no regression:
- Initial edit-load `patchValue()` sets Country → State → City in sequence; the existing subscribers reset State/City to `null` synchronously, then the real saved values are re-applied before `getStates()`/`getCities()` resolve asynchronously — so the new validator toggle only ever affects required-ness, never clobbers a loaded value.
- The Country/State/City block is never hidden by the "Is your startup incorporated?" toggle (only the section heading text changes), so there's no hidden-but-required deadlock.
- The Save button's `[disabled]="!startupInfoForm.valid || ..."` and the "N field(s) are not complete" counter (`countInvalidFields`) both iterate generically over `Object.keys(startupInfoForm.controls)`, so State/City are automatically picked up with no extra wiring.
- `onSubmit()` spreads `startupInfoForm.value` regardless of validity — payload shape is unaffected.

Residual known edge case (pre-existing async-race class, not a new regression): switching Country and hitting Save before `getStates()` resolves briefly leaves the previous country's required-ness in effect — self-resolves as soon as the API responds, same as the existing dropdown-population race.

## Linear
Created flat (no project) per the small-enhancement bug-fix flow. Labels `Improvement`, `Repo: Frontend`; priority Medium; assigned to Vishali. Moved Todo → In Progress → In Review → Done. Root-cause/fix summary posted as a Linear comment.

Vishali committed and pushed as `sc-saas-frontend@7d9e3cc7` on `ai_native_setup_vishali` (up to date with `origin/ai_native_setup_vishali`) — note this branch is still ahead of/separate from `main`, per the workspace's known frontend deploy lag, so the fix won't reach production until the next deploy.
