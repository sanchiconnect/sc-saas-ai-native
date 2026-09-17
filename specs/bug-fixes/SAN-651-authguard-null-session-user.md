---
id: SAN-651
title: "AuthGuard.canActivate() crashes reading 'accountType' of null session user"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-651
sentry:
  - SC-SAAS-FRONTEND-4X
repos: [frontend]
commit: sc-saas-frontend@8447e24f (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-651 — AuthGuard crashes on null session user from validateSession()

## Root cause
`AuthGuard.canActivate()`'s fallback path (no `localStorage` user) calls `this.authService.validateSession()` and passes the resolved `sessionUser` straight into `checkAccountType()`, which immediately reads `user.accountType`. The `localStorage`-sourced `user` earlier in the same guard is correctly null-checked (`if (user) {...}`), but the async `validateSession()` result had no equivalent guard — a falsy/empty session user threw, blocking navigation for the user.

## Fix
Added `if (!sessionUser) { return this.showErrorAndLogout(state); }` in the `map` callback, before `checkAccountType()` runs.

## Blast radius
None for the valid-session path (unchanged). For the invalid-session path, the user now gets routed through the existing `showErrorAndLogout()` flow (toast + logout + redirect) instead of crashing mid-navigation.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.
