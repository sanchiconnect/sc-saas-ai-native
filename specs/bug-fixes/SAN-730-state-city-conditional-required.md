---
id: SAN-730
title: Conditionally-required State/City in the Country/State/City picker (all stakeholder edit forms)
type: feature
status: in-progress            # Implementation complete across all 11 forms as of this update; not yet
                                 # committed/pushed and not yet live-tested in a browser — see Test plan.
linear: https://linear.app/sanchiconnect/issue/SAN-730/make-statecity-conditionally-required-based-on-available-options-all
owner: vishali.k@sanchiconnect.com
repos: [frontend]
contracts:
  api: []
  flags: []
  events: []
tenant_scoped: true             # Operates on tenant-scoped stakeholder profile data (startups, mentors,
                                 # investors, etc., loaded via the backend at each tenant's own apiUrl per
                                 # invariant #5) — but this feature is pure client-side form logic; no query
                                 # or scoping mechanism is touched. See Contracts & invariants.
depends_on: []
created: 2026-09-09
updated: 2026-09-09
---

# Conditionally-required State/City in the Country/State/City picker

## Problem

Every stakeholder profile edit form in `sc-saas-frontend` (startup, mentor, investor ×2, service-provider,
program-office, partner, corporate, individual-profile, plus the programs-application variant) renders the
same Country/State/City picker, but only Country was ever a required field — State and City were declared
with an empty validator array regardless of whether the selected country/state actually has state- or
city-level data to choose from. For a country like India, where a real state and city choice is expected,
users could submit the form with State/City left blank. For a country with no state-level data at all (e.g.
Aland Islands), State/City are correctly optional either way — the requirement is to make required-ness
track the data, not hardcode either extreme.

## Acceptance criteria

- [x] Country remains required in every form.
- [x] State becomes required exactly when the states list returned for the selected country is non-empty;
      optional when it's empty.
- [x] City becomes required exactly when the cities list returned for the selected state is non-empty;
      optional when it's empty.
- [x] Changing Country resets State and City to empty and re-fetches the States list for the new country.
- [x] Selecting a State resets City to empty and re-fetches the Cities list for the new state.
- [x] The required asterisk on the State/City labels reflects the same non-empty-list condition (not a
      static asterisk).
- [x] "State is required" / "City is required" inline error messages show when the field is required, empty,
      and touched/dirty.
- [x] The Save/Update/Submit action stays disabled while a required State or City is empty, or any other
      form validation error exists — via each form's existing generic `formGroup.invalid`/`.valid` gating
      (no per-field wiring needed; State/City are ordinary controls in the same `FormGroup`).
- [x] A user's own in-progress Country/State/City selection is never silently overwritten by a background
      data refresh (e.g. after Save, or an autosave tick) before the user navigates away or reloads.
- [x] A City the user has selected survives an asynchronous States/Cities list refresh that lands shortly
      after — it does not go blank on its own.
- [ ] Manual click-through in a live browser, all 11 forms — not yet done (see Test plan).

## Per-repo plan

### frontend (`sc-saas-frontend`)

Applied identically to all 11 components that render the Country/State/City picker (`.ts` + `.html`, 22
files):

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

Each component carries four pieces of logic, all now consistent across all 11:

1. **Conditional required validators** — `getStates()`/`getCities()` toggle `Validators.required` on
   `registeredStateId`/`registeredCityId` based on the length of the list the API returns:
   ```ts
   getStates(cId: string) {
     this.globalService.getStates(cId).subscribe((res) => {
       this.states = res;
       const stateControl = this.<form>.get('registeredStateId');
       stateControl.setValidators(res?.length ? [Validators.required] : []);
       stateControl.updateValueAndValidity({ emitEvent: false });
     })
   }
   ```
   (mirrored for `getCities()`/`registeredCityId`). Templates show the asterisk via
   `*ngIf="states?.length"` / `*ngIf="cities?.length"` instead of a static one.

2. **Reset on genuine Country/State change** — pre-existing in all 11 forms, unchanged by this work:
   ```ts
   this.<form>.get('registeredCountryId').valueChanges.pipe(takeUntil(this.destroyed$)).subscribe((res) => {
     this.<form>.patchValue({ registeredStateId: null, registeredCityId: null });
     this.getStates(res);
   })
   this.<form>.get('registeredStateId').valueChanges.pipe(takeUntil(this.destroyed$)).subscribe((res) => {
     this.<form>.patchValue({ registeredCityId: null });
     this.getCities(res);
   })
   ```

3. **`geographySynced` guard** — each component's "load info" store/HTTP subscription re-runs its main
   `patchValue()`/`setValue()` on every re-emission (after any save, not just the true initial load).
   Country/State/City are pulled out of that call into their own block, gated to run exactly once:
   ```ts
   if (!this.geographySynced) {
     this.<form>.patchValue({
       registeredCountryId: res.registeredCountryR?.id || null,
       registeredStateId: res.registeredStateR?.id || null,
       registeredCityId: res.registeredCityR?.id || null,
     })
     this.geographySynced = true;
   }
   ```
   Without this, a save round-trip whose response still carries the pre-change State/City relation silently
   reverts a user's just-made Country change. Two components (`organization-details.component.ts`,
   `individual-investor-edit-form.component.ts`) used `.setValue()` for the main load call, which requires
   every control in one call — converted to `.patchValue()` so Country/State/City could be split out.

4. **`{ emitEvent: false }` on both `updateValueAndValidity()` calls** — `getStates()`'s async response
   lands after the initial load's `patchValue()` has already set City correctly. Without `emitEvent:false`,
   `updateValueAndValidity()` spuriously re-emits `registeredStateId`'s own `valueChanges` (validators
   changed, not the value), which re-triggers the State→"null City" subscriber from point 2 above and wipes
   out a City that was just correctly set — visible as City going blank shortly after being selected, or
   after a tab switch/hard refresh. `.invalid`/`.errors` and the parent `FormGroup`'s aggregate validity
   still recompute correctly; only the spurious re-emission is suppressed.

Every one of the 11 forms already declared `registeredStateId`/`registeredCityId` with an empty validator
array and no other validators, so `setValidators()` in point 1 doesn't clobber anything else.

## Contracts & invariants

- **Flags:** none.
- **API:** none — no backend controller/DTO change. Whether `sc-saas-backend`'s save endpoints (per
  stakeholder type) correctly null `registeredStateR`/`registeredCityR` when given `null` IDs is unaudited;
  point 3 above makes the frontend resilient to that either way, but it's worth a follow-up `/audit-contract`
  pass if State/City are still observed reverting after a save in live testing.
- **Events:** none.
- **Invariants at risk:** none of the 6 workspace invariants (flag names, API contract, tenant-verification
  shape, auth, tenant scoping, PowerPitch contract) are touched — this is pure client-side form logic. No
  shared/service code changed; each of the 11 components owns its own form group independently (there is no
  common location-picker component in this codebase).

## Test plan

- frontend: `npx tsc -p tsconfig.app.json --noEmit` — clean across the whole app.
- frontend: `ng test` (Karma) — attempted, currently blocked workspace-wide by pre-existing, unrelated TS
  errors in other `.spec.ts` files across the repo; not fixed as part of this feature (out of scope, flagged
  separately). No `.spec.ts` exists yet for any of the 11 components.
- frontend: the reactive-forms mechanics behind points 3 and 4 above (`geographySynced`, `emitEvent:false`)
  were each verified directly against the real `@angular/forms` `FormGroup`/`FormControl`/`Validators`
  classes, run standalone in Node (`import('@angular/compiler')` first, to work around the JIT-fallback
  error) — not simulated, and not `ng test` per the blocker above. Explicit before/after reproductions exist
  for both the Country-change-reverts-on-save bug and the City-blanks-after-refresh bug (see History below).
- manual: not yet done in a live browser — no backend/tenant auth available in this working environment.
  Pending: click through all 11 forms, per form — change Country to one with states (e.g. India) and confirm
  State becomes required with the asterisk, then City after picking a State; change Country to one without
  states (e.g. Aland Islands) and confirm State/City stay optional; pick a City, save, and confirm it
  survives; pick a City, switch tabs or hard-refresh, and confirm it survives.
- cross-repo: none — single-repo, frontend-only.

## Rollout

Single-repo, no migrations, no flag gating, behavior-preserving except for the explicitly-required
acceptance criteria above. First round (conditional validators + templates) is committed and pushed as
`sc-saas-frontend@7d9e3cc7` on `ai_native_setup_vishali`. Everything from `geographySynced` and
`emitEvent:false` onward is implemented and `tsc`-clean but **not yet committed** — recommend committing
promptly once live-tested, since an earlier round of this same work was lost once already to an upstream
merge before it was committed (see History below). This branch is also still ahead of/separate from `main`
per the workspace's known frontend deploy lag, so none of this reaches production until the next deploy
regardless of commit state.

## Out of scope

- Auditing `sc-saas-backend`'s save endpoints for whether they correctly null `registeredStateR`/
  `registeredCityR` given `null` IDs — noted as a risk this frontend fix is resilient to, not audited here.
- Extracting the Country/State/City picker into a shared component — the same ~20-line pattern is
  duplicated 11 times; deferred, not requested.
- Fixing the pre-existing, unrelated Karma/`ng test` breakage blocking automated test coverage for this
  feature.
- Writing new `.spec.ts` regression tests for the 11 components — proposed, not yet green-lit.

## Open questions

None blocking. Two things worth resolving before calling this fully done, tracked as pending Test-plan items
rather than open design questions: live browser confirmation on all 11 forms, and a decision on whether to
invest in fixing the Karma breakage now or file it separately.

## History

Kept for anyone who needs the detailed debugging trail — root-cause analyses, dead ends, and one real
incident worth knowing about if you're about to touch this code again.

**Round 1 (conditional validators + templates).** Applied to all 11 components as described in point 1 of
the Per-repo plan above. Verified with `npx tsc -p tsconfig.app.json --noEmit`. Committed and pushed as
`sc-saas-frontend@7d9e3cc7`.

**Round 2 — regression: City goes blank after selecting it.** `stateControl.updateValueAndValidity()` /
`cityControl.updateValueAndValidity()` (added by round 1) emit that control's own `valueChanges`
unconditionally in Angular, even when only validators changed. Every one of the 11 forms already had a
pre-existing subscriber that clears City when State changes (point 2 of the Per-repo plan) — the spurious
re-emission fired that subscriber for real, wiping a City the user had just picked. Fix: `{ emitEvent: false
}` on both calls (point 4 above).

**Incident: the round-2 fix was lost, then re-applied with two extra (later-abandoned) fixes.** The
`emitEvent:false` fix was applied but never committed. A merge commit (`ebd058d3`, merging the shared
`ai_native_setup` branch into `ai_native_setup_vishali`) required a clean working tree and silently discarded
the uncommitted fix across all 11 files — the round-1 logic, already committed, was unaffected. This
reintroduced City-blanking during testing. Re-applied `emitEvent:false`, plus two additional fixes at the
time: `distinctUntilChanged()` on the Country/State `valueChanges` subscribers, and an ng-select
"label-refresh nudge" (re-`setValue()` the control once its options list arrives, to force ng-select to
re-resolve a value set before the list loaded). **Both of those two extra fixes were later found not to fix
the symptom they were meant for** (reported directly: "this is not working") **and were removed** — take any
future troubleshooting notes that reference them with that in mind. They are not in the current code.

**Round 3 — deeper root cause: background data-refresh fighting live edits.** Even with round 2's fix in
place, City still showed blank / State-City still reset unexpectedly. Traced to each form's "load info"
subscription re-`patchValue()`ing the *entire* form — including Country/State/City — on every store/HTTP
re-emission, not just the true initial load (i.e. after every save). Fix: the `geographySynced` guard (point
3 above), pulling Country/State/City into their own once-only block.

**Round 3 was also found reverted at the start of a later session** — `git status` showed zero diff on any
of the 11 files despite Linear comments describing `geographySynced` as applied. Re-diagnosed from scratch
rather than re-applying blindly, with direct confirmation from Vishali on the exact symptom (the underlying
form *value* wasn't resetting — not just a stale label) and verification against the real `@angular/forms`
classes standalone in Node (`ng test`/Karma is currently broken workspace-wide by unrelated pre-existing TS
errors in other spec files — confirmed while investigating, still unfixed, see Out of scope). Re-applied
`geographySynced` to all 11 components.

**Round 4 — re-diagnosed, same session: City blank after select + tab switch/hard refresh.** Reported
against `step-one-company-info.component.ts`. Same underlying mechanism as round 2, still live because round
2's `emitEvent:false` fix had also been lost along with round 3's. Reconfirmed the exact sequence with the
real `@angular/forms` classes:
```
AFTER SYNC LOAD PATCH                                    { ..., registeredCityId: 'PUNE' }
AFTER getStates() ASYNC RESPONSE (no emitEvent:false)     { ..., registeredCityId: null }   <- bug
AFTER getStates() ASYNC RESPONSE (with emitEvent:false)   { ..., registeredCityId: 'PUNE' } <- fixed
```
Re-applied `emitEvent:false` to all 11 components (without re-adding the two abandoned extra fixes from the
incident above).

**Linear:** created flat (no project) per the small-enhancement bug-fix flow. Labels `Improvement`,
`Repo: Frontend`; priority Medium; assigned to Vishali. Moved Todo → In Progress → In Review → Done, then
reopened to In Progress once the round-2 regression was found; root-cause/fix summaries posted as Linear
comments each round, including a correction comment noting the two abandoned fixes are not in the current
code. Status left at In Progress pending live testing and commit.
