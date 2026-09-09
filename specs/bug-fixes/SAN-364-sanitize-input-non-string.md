---
id: SAN-364
title: form-field sanitizeInput/sanitizeScriptTagsInput crash on non-string values
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-364
sentry:
  - SC-SAAS-FRONTEND-91
  - SC-SAAS-FRONTEND-94
  - SC-SAAS-FRONTEND-93
  - SC-SAAS-FRONTEND-8B
  - SC-SAAS-FRONTEND-8C
repos: [frontend]
commit: sc-saas-frontend@c0638d20 (branch ai_native_setup_aman)
created: 2026-08-19
updated: 2026-08-19
---

# SAN-364 — form-field sanitizeInput TypeError

## Root cause
`src/app/modules/dynamic-forms/event-forms/form-field/form-field.component.ts` — `sanitizeInput`/`sanitizeScriptTagsInput` called `.replace()` on the value passed from `control.valueChanges` with no `typeof === 'string'` guard, only an `if (value)` truthiness check. Legacy or malformed saved form answers (non-string values persisted for a `text_field`/`text_area`) reach these handlers on load and crash. Same root cause produced 5 distinct Sentry issues (SC-SAAS-FRONTEND-91/93/94/8B/8C) from the same handful of tenant forms.

## Fix
Added `typeof value === 'string' &&` to the guard in both methods, before calling `.replace()`.

## Blast radius
None — grepped the whole repo for other callers of these two method names; only internal callers exist, always fed from `control.valueChanges` on `text_field`/`text_area` types (string/null/undefined only). A separate, unrelated `sanitizeInput` method on `chat-message-form.component.ts` always receives a string and was untouched.

## Verification
`tsc --noEmit` clean on the modified file. No test coverage exists for this component; type-check was the strongest verification available.
