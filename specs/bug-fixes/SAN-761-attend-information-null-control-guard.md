---
id: SAN-761
title: "attend-information onValidationCheck crashes calling clearValidators() on a null form control"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-761
sentry:
  - SC-SAAS-FRONTEND-DQ
repos: [frontend]
commit: sc-saas-frontend@afd07ff5 (ai_native_setup_vishali)
created: 2026-09-14
updated: 2026-09-14
---

# SAN-761 — attend-information null-control guard

## Investigation

`attend-information.component.ts:onValidationCheck` reads `this.QuestionForm.get('question_' + questionId)`
and immediately calls `.clearValidators()`/`.setValidators()`/`.updateValueAndValidity()` on the result with no
null check. `FormGroup.get()` returns `null` when no control named `question_<questionId>` exists — e.g. a
stale/mismatched `questionId` from `clearFileSelection`, or the form not yet rebuilt for the current question
set. Confirmed still present/unguarded in current source.

## Fix

```ts
const control = this.QuestionForm.get('question_' + questionId);
if (!control) {
  return;
}
```
Added immediately after the lookup, before any use of `control`. Pure defensive guard — behavior for the
normal case (control exists) is unchanged.

## Blast radius

None — single-file, additive early-return only. No API/flag/tenant-isolation contract touched.

## Verification

`npx tsc -p tsconfig.json --noEmit` clean for the touched file (only pre-existing, unrelated Jasmine/Karma
`.spec.ts` type errors elsewhere in the run). No `.spec.ts` exists for this component. Tests-first is blocked
workspace-wide (no `guardian` skill yet); this is the substitute verification.

## Rollout

Committed and pushed as `sc-saas-frontend@afd07ff5` ("SAN-761: guard onValidationCheck against a null form
control") on `ai_native_setup_vishali`, after Vishali's review and explicit go-ahead. Still subject to the
workspace's known frontend deploy lag.

## Open questions

None blocking.
