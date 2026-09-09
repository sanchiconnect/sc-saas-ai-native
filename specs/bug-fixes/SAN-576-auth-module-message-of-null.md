---
id: SAN-576
title: Cannot read 'message' of null — auth module error path
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-576
sentry:
  - SC-SAAS-FRONTEND-7W
repos: [frontend]
commit: sc-saas-frontend@3791f938 (branch ai_native_setup_vishali, not pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-576 — message-of-null in auth module

## Root cause
`login.component.ts`'s `sendLoginRequest()` `.subscribe((res) => {...}, err => {...})` error callback read `err.error.message` with no guard — a status-0/empty-body failure on the login OTP call throws here. This is a component-level `subscribe`, not an NgRx effect, so the shared `httpFaultMessage()` helper (effects-only, see SAN-474/SAN-572) doesn't directly apply here.

## Fix
Matched the dominant convention used in ~30 other component files across the codebase for this exact situation (e.g. `hire.component.ts`, `individual-public-profile.component.ts`, `job-form.component.ts`):
```
// before
this.toastAlertService.showToast(err.error.message, 'error');
// after
this.toastAlertService.showToast(err?.error?.message || err.message || 'Something went wrong', 'error');
```
Happy path (`res` callback) untouched. No other unguarded `err.error.message`/`err.message` sites found elsewhere in `src/app/modules/auth`.

## Blast radius
None — error-path guard only.

## Verification
`npx tsc -p tsconfig.json --noEmit` clean.
