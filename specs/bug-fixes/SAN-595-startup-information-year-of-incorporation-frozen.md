---
id: SAN-595
title: Cannot assign to read only property 'yearOfIncorporation' — mutating FormGroup's internal .value object after NgRx freezes it
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-595
sentry:
  - SC-SAAS-FRONTEND-73
repos: [frontend]
commit: sc-saas-frontend@02200123 (branch ai_native_setup_vishali, pushed)
created: 2026-09-04
updated: 2026-09-04
---

# SAN-595 — startup-information yearOfIncorporation frozen object

## Root cause
Same underlying bug class as SAN-594. `onSubmit()` (`startup-information.component.ts:637-658`, before fix) did `const payload = this.startupInfoForm.value;` then mutated `payload.yearOfIncorporation = payload.yearOfIncorporation + ''` before dispatching it via `StartupActions.SaveStartUpInfo(payload)`. Angular's `FormGroup.value` getter does **not** return a fresh object per access — it returns the form's internal `_value` object, updated in place as control values change. Once dispatched, `@ngrx/store`'s dev-mode runtime immutability checks freeze that same internal object; the next `onSubmit()` mutation of the same reference throws.

## Fix
`const payload = { ...this.startupInfoForm.value };` — a shallow copy, safe to mutate and dispatch. The form's internal value object is never touched, so it's never frozen.

## Blast radius
None — identical payload shape dispatched, built from a safe copy instead of the live form-internal object.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean on the changed file. No automated test suite exists for this repo.

## Related
Same anti-pattern class as SAN-594 (SC-SAAS-FRONTEND-BW) — worth a broader sweep for `= this.xForm.value;` followed by direct mutation elsewhere in the codebase if this recurs.
