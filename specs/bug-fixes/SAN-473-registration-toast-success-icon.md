---
id: SAN-473
title: Registration-failure toast shows success (green) icon
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-473
sentry:
  - SC-SAAS-FRONTEND-64
repos: [frontend]
commit: uncommitted (working tree only, awaiting review)
created: 2026-08-20
updated: 2026-08-20
---

# SAN-473 — Registration-failure toast shows success (green) icon

## Root cause
`ToastAlertService.showToast(title, type = 'success', ...)` defaults `type` to `'success'` when the second argument is omitted. Two call sites omitted it on a registration-failure path:
- `register.component.ts:660` — `registerError`-selector subscription in `register()`.
- `register-modal.component.ts:218` — direct `registerOtherUser()` HTTP subscribe error callback.

So a user hitting a real, well-formed validation error (e.g. duplicate mobile number, SC-SAAS-FRONTEND-64) saw a message that says "fail" but is visually styled as success — misleading UX on the signup flow. Confirmed as an oversight, not intentional: sibling calls in the same files (e.g. `register-modal.component.ts:183/277`) already pass `'error'` correctly.

## Fix
Added `'error'` as the second argument to both `showToast(...)` calls. No other lines touched.

## Blast radius
None — single-argument addition, no change to message content, selector, or effect logic.

## Verification
`npx tsc -p tsconfig.app.json --noEmit` clean. No automated test exists for this flow (workspace-wide guardrail); verification is a static read-through confirming the icon parameter is the only difference from the correctly-styled sibling calls in the same files.

## Related
See `sc-saas-frontend/src/app/modules/auth/module.spec.md` ("Watch out for") for the documented fix.
