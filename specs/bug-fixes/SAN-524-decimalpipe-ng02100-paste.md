---
id: SAN-524
title: DecimalPipe NG02100 crash on non-numeric paste into number fields (8 components)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-524
sentry:
  - SC-SAAS-FRONTEND-AB
repos: [frontend]
commit: sc-saas-frontend@8b53d449 (branch ai_native_setup_vishali)
created: 2026-08-26
updated: 2026-08-26
---

# SAN-524 — DecimalPipe NG02100 crash on non-numeric paste

## Root cause
`GrowthMatricsFormComponent` (and 7 other components) register a live-formatting subscription on every number-input control:

```ts
control.valueChanges.subscribe(val => {
  if(val) {
    val = val.replaceAll(',', '');
    control.setValue(this.decimalPipe.transform(val, '1.0-0'), {emitEvent: false});
  }
});
```

`replaceAll(',', '')` only strips commas; it does nothing for any other non-numeric content. The Sentry event shows the user pasted a large tab-separated block of text (apparently a whole row copied from a spreadsheet/table, including labels, `%`, and `₹` symbols) into the field. `DecimalPipe.transform()` throws Angular's `NG02100 InvalidPipeArgument` runtime error for any non-numeric string, and since this runs synchronously inside `valueChanges.subscribe` — not guarded by the control's own `NUMBER_VALIDATOR_WITH_COMMA` validator, which only affects validity state, not this side-effect — it crashes before the user ever sees a validation error.

The exact same unguarded shape was found in 7 more components:
1. `src/app/modules/investors/pages/edit/organization-details/organization-details.component.ts`
2. `src/app/modules/milestones/component/create-milestone-form/create-milestone-form.component.ts`
3. `src/app/modules/investors/pages/edit/investments-details/investments-details.component.ts`
4. `src/app/modules/investors/pages/edit/individual-investor-edit-form/individual-investor-edit-form.component.ts`
5. `src/app/modules/startups/pages/edit/financials-details/ongoing-commitments-list/ongoing-commitments-list.component.ts`
6. `src/app/modules/startups/pages/edit/financials-details/financials-details.component.ts`
7. `src/app/modules/startups/components/edit-profile-modal/stepper/step-financials-info/step-financials-info.component.ts`

Notably, the codebase already had the correct fix in one other place — `startup-all-required-details-form.component.ts` wraps the `decimalPipe.transform` call in try/catch and falls back to the raw value on failure — but that fix had never been applied to the 8 sites above. (`milestone-details.component.ts`'s similar-looking `checkValue()` is already safe — it has an explicit `isNaN(val)` guard that resets to `'0'` before calling `decimalPipe.transform`, so it wasn't part of this fix.)

## Fix
Applied the same try/catch pattern already validated in `startup-all-required-details-form.component.ts` to all 8 sites: on a `DecimalPipe.transform` failure, keep the raw (comma-stripped) value instead of crashing, and let the control's existing `NUMBER_VALIDATOR_WITH_COMMA` validator surface the invalid-input state to the user normally.

## Blast radius
None — no behavior change for valid numeric input; formatting still applies exactly as before. Diff is 8 files, +7/-1 each, identical shape.

## Verification
`tsc --noEmit` clean across all 8 files. No test suite configured for this repo; type-check was the strongest verification available.
