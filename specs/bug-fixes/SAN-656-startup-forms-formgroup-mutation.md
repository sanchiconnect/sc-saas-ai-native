---
id: SAN-656
title: "TypeError: Cannot assign to read only property 'yearOfIncorporation' — direct FormGroup.value mutation"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-656
sentry:
  - SC-SAAS-FRONTEND-B7
repos: [frontend]
commit: sc-saas-frontend@2c0858f9 (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-656 — two startup-form components mutate live FormGroup.value directly

## Root cause
The named Sentry culprit (`StartupInformationComponent.saveStartupInfoSection`) doesn't literally match any method in that file — `onSubmit()` there already defensively spreads `const payload = { ...this.startupInfoForm.value };` before mutating, so it can't throw this. Two sibling components declared in the same/adjacent lazy chunks have the identical unsafe pattern (`const payload = this.startupInfoForm.value;` — no spread, mutating the live FormGroup value object directly) before doing `payload.yearOfIncorporation = payload.yearOfIncorporation + '';`:
- `step-one-company-info.component.ts`
- `startup-all-required-details-form.component.ts`

Sentry's minified stack likely misattributed the component given the near-identical code shape shared across the chunk.

## Fix
Applied the same defensive-copy fix already present in `startup-information.component.ts` to both siblings: `const payload = { ...this.startupInfoForm.value };`.

## Blast radius
None — the payload sent to `StartupActions.SaveStartUpInfo` is unchanged in shape/content; only the mutation target changes from the live form value to a copy.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.
