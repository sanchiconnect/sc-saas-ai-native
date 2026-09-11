---
id: SAN-753
title: Default India Country & Country Selection Persistence (all stakeholder edit forms)
type: feature
status: in-review             # Implementation complete across all 11 forms, tsc-clean, committed and pushed;
                              # not yet live-tested in a browser — see Test plan.
linear: https://linear.app/sanchiconnect/issue/SAN-753/default-india-country-and-country-selection-persistence-all
owner: vishali.k@sanchiconnect.com
repos: [frontend]
contracts:
  api: []
  flags: []
  events: []
tenant_scoped: true           # Same rationale as SAN-730: operates on tenant-scoped stakeholder profile
                               # data, but is pure client-side form logic — no query or scoping mechanism
                               # is touched.
depends_on: [SAN-730]
created: 2026-09-11
updated: 2026-09-11          # committed/pushed to sc-saas-frontend@2915f4a4
---

# Default India Country & Country Selection Persistence

## Problem

Sub-task of [[SAN-730]] (Conditionally-required State/City). The same Country/State/City picker, present
identically in all 11 stakeholder edit forms, had no default Country: a form with no saved country left the
Country field blank until the user picked one, so State/City also stayed unpopulated for that first edit.
Requirement: default to **India** whenever no country is saved yet, without ever overriding a genuinely saved
or user-picked country.

## Acceptance criteria

- [x] When Country is empty/unselected → India is selected by default.
- [x] When the user selects another country → the manually selected country is displayed and takes priority
      over the default (default logic only ever patches an *empty* control, never overwrites one that already
      has a value).
- [x] On stakeholder edit → the saved country is displayed if available; otherwise, default to India.
- [x] State and City options are loaded according to the selected country (reuses SAN-730's existing
      `registeredCountryId` → `registeredStateId` → `registeredCityId` valueChanges cascade — the default is
      applied via the control's own `patchValue()`, so the cascade fires exactly as it would for a real user
      selection).
- [x] Changing the country refreshes/resets dependent State/City selections appropriately (unchanged,
      pre-existing SAN-730 behavior).
- [x] Behavior is consistent across all stakeholder edit forms (all 11).
- [x] Existing conditional required validation from SAN-730 continues to work with the default/selected
      country (no changes to `getStates()`/`getCities()` validator-toggle logic).
- [ ] Manual click-through in a live browser, all 11 forms — not yet done (see Test plan).

## Per-repo plan

### frontend (`sc-saas-frontend`)

Two pieces, applied identically to all 11 components from SAN-730's Per-repo plan, plus a new shared helper:

1. **`GlobalService.getDefaultCountryId(countries)`** (`core/service/global.service.ts`) — the one place all
   11 forms resolve "India" from, so the name-match isn't duplicated 11 times:
   ```ts
   public getDefaultCountryId(countries: any[]): string | null {
     return countries?.find((c) => c?.name?.toLowerCase() === 'india')?.id ?? null;
   }
   ```
   Countries are backend-driven (no static "India = id X" constant exists anywhere in this codebase), so the
   match is by name at runtime against whatever `GlobalService.getCountries()` returns.

2. **`applyDefaultCountryIfNeeded()`** — added to each of the 11 components, called from two points so
   whichever of the two async sources finishes last actually applies the default:
   ```ts
   defaultCountryApplied = false;   // new field, alongside the existing geographySynced

   getCountries() {
     this.globalService.getCountries().subscribe((res) => {
       this.countries = res;
       this.applyDefaultCountryIfNeeded();
     })
   }

   applyDefaultCountryIfNeeded(): void {
     if (this.defaultCountryApplied || !this.geographySynced || !this.countries?.length) {
       return;
     }
     this.defaultCountryApplied = true;
     const countryControl = this.<form>.get('registeredCountryId');
     if (!countryControl.value) {
       countryControl.patchValue(this.globalService.getDefaultCountryId(this.countries));
     }
   }
   ```
   The second call site is right after `this.geographySynced = true;` in each form's existing SAN-730
   "load saved Country/State/City once" block. Guard order matters:
   - Waits for **both** `this.countries` to be populated **and** `geographySynced` (the saved-profile patch,
     which may leave `registeredCountryId` at `null` if nothing was saved) before deciding.
   - Runs at most once (`defaultCountryApplied`), so it never fights a later user change.
   - Only patches when the control is still empty — a saved or already-picked country is left untouched.
   - Patches via the control's own `patchValue()` (not a silent/`emitEvent:false` set), so the pre-existing
     `registeredCountryId` valueChanges subscriber fires normally and loads State/City for India, exactly as
     it would for a manual selection.

Applied to the same 11 components as SAN-730:
`startups/pages/edit/startup-information`, `startups/components/edit-profile-modal/stepper/step-one-company-info`,
`mentors/pages/edit/mentor-intro`, `investors/pages/edit/organization-details`,
`investors/pages/edit/individual-investor-edit-form`, `service-provider/pages/edit/service-provider-intro`,
`program-office/edit/program-office-intro`, `partners-dashboard/pages/edit/partner-intro`,
`corporate/pages/edit/corporate-intro`, `individual-profile/pages/individual-profile-edit-form`,
`programs/programs-details-page/startup-all-required-details-form`.

## Contracts & invariants

- **Flags:** none.
- **API:** none — no backend controller/DTO change; India is matched client-side against the existing
  `GlobalService.getCountries()` response.
- **Events:** none.
- **Invariants at risk:** none of the 6 workspace invariants are touched — pure client-side form logic, same
  conclusion as SAN-730. No shared Country/State/City component exists in this codebase (confirmed during
  investigation); `GlobalService` is the only shared piece, and it now carries one pure helper method in
  addition to its existing HTTP calls.

## Test plan

- frontend: `npx tsc -p tsconfig.json --noEmit` — clean for all 12 touched files (`global.service.ts` + the
  11 components); the only errors in the full run are pre-existing, unrelated Jasmine/Karma type errors in
  vendored `cometchat-pro-angular-ui-kit` spec files.
- frontend: `ng test` (Karma) — not run; blocked workspace-wide by the same pre-existing, unrelated breakage
  noted in SAN-730's Test plan. No `.spec.ts` exists for any of the 11 components.
- manual: not yet done in a live browser. Pending: for a profile with no saved country, open each of the 11
  edit forms and confirm Country defaults to India and State/City populate; for a profile with a saved
  country, confirm it displays as-is (no override); manually pick a different country and confirm it takes
  priority and persists.
- cross-repo: none — single-repo, frontend-only.

## Rollout

Single-repo, no migrations, no flag gating. Committed and pushed as
`sc-saas-frontend@2915f4a4` ("SUb: SAN-753: Default India Country & Country Selection Persistence (all
stakeholder edit forms)") on `ai_native_setup_vishali`, matching the per-developer branch convention this
repo uses (not the workspace-default `ai_native_setup`). This branch is also still subject to the workspace's
known frontend deploy lag (prod is 17+ days behind `main` as of the last check), so none of this reaches
production until the next deploy regardless of commit state. Live browser testing (see Test plan) is still
outstanding before this is marked fully Done.

## Out of scope

- Extracting the Country/State/City picker into a shared component — same conclusion as SAN-730, deferred.
- Writing new `.spec.ts` regression tests for the 11 components.
- Handling the edge case where a stakeholder's edit-info API response never returns a data object at all (a
  true brand-new profile with zero prior data) — `geographySynced` never flips true in that case in any of
  the 11 forms today (pre-existing SAN-730 behavior), so the India default would also never apply there. Not
  observed as a real scenario for these edit-time forms; flagged here rather than silently assumed away.

## Open questions

None blocking. Live browser confirmation on all 11 forms is the only remaining Test-plan item before this is
fully done.
