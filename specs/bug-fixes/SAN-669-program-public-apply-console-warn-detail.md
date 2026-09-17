---
id: SAN-669
title: "applicationProgramManagementApplicationDetails failed [object Object] — cosmetic logging fix"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-669
sentry:
  - SC-SAAS-FRONTEND-2T
repos: [frontend]
commit: sc-saas-frontend@aa5df2c2 (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-669 — program-public-apply logs raw error object, renders as [object Object] in Sentry

## Root cause
`program-public-apply.component.ts` intentionally does `console.warn('applicationProgramManagementApplicationDetails failed', error)` for any non-404 failure (404 = "no application yet", silently ignored). `main.ts` installs `captureConsoleIntegration({ levels: ['warn'] })`, which forwards every `console.warn` to Sentry; passing the raw error object as a second arg (instead of `error?.message`) is what renders as "[object Object]" in the Sentry issue title. Working as designed for the warning itself — the underlying failure is server-side.

## Fix
Changed to `` console.warn(`applicationProgramManagementApplicationDetails failed: ${error?.status} ${error?.message}`) `` so future Sentry titles are actionable instead of "[object Object]". Cosmetic only — no behavior change.

## Blast radius
None — logging only.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.
