---
id: SAN-706
title: "Register fails with unhelpful generic message + unguarded err.error.message access"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-706
sentry:
  - SC-SAAS-FRONTEND-CG
repos: [frontend]
commit: sc-saas-frontend@0dd6e1ba (branch ai_native_setup_vishali, pushed)
created: 2026-09-08
updated: 2026-09-08
---

# SAN-706 — register-modal unguarded error access + unhelpful message

## Root cause
`register-modal.component.ts:218` (`register()`'s error callback) read `err.error.message` with no optional chaining, and didn't handle the case where `err.error?.message` is an array (NestJS class-validator shape):
```ts
this.toastAlertService.showToast(`User registered fail. ${err.error?.error?.[0] || err.error.message}`, 'error');
```
If `err.error` is `null`/`undefined` (network error, non-JSON body), this throws a second `TypeError` inside the error handler, hiding the real failure entirely. Separately, 5 distinct production users hit a generic `"Bad Request Exception"` backend message with no field-level detail over 2 days.

## Fix
```ts
const validationMessage = Array.isArray(err.error?.message) ? err.error.message.join(', ') : err.error?.message;
this.toastAlertService.showToast(`User registered fail. ${err.error?.error?.[0] || validationMessage || 'Please try again.'}`, 'error');
```
Fully-guarded chain, array-safe, with a static fallback so the user never sees a raw crash or "undefined".

## Blast radius
`sc-saas-frontend`'s `register-modal.component.ts` only. **Follow-up recommended but not filed**: the backend's generic `"Bad Request Exception"` message on the register endpoint isn't field-level actionable — a `Repo: Backend` issue may be warranted if confirmed, per single-repo scoping (not investigated here, out of this ticket's scope).

## Verification
`npx tsc --noEmit -p tsconfig.json` — no new errors on the touched file. Regression test proposed in the Linear comment (mock error shapes `{error: null}` and `{error: {message: [...]}}`), holding off on writing until user confirms. Committed and pushed as `sc-saas-frontend@0dd6e1ba`. Linear moved to Done; Sentry SC-SAAS-FRONTEND-CG marked resolved with a comment referencing the commit.
