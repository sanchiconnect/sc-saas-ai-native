---
id: SAN-662
title: "Uncaught (in promise): Cannot read 'isRejected' — missing guard in programs-details-page canSubmit check"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-662
sentry:
  - SC-SAAS-FRONTEND-4P
repos: [frontend]
commit: sc-saas-frontend@806bab13 (branch ai_native_setup_vishali)
created: 2026-09-07
updated: 2026-09-07
---

# SAN-662 — programs-details-page canSubmit race with profileCompleteness

## Root cause
`fetchProgram()`'s `fromSubmit` branch reads `this.profileCompleteness.isRejected`/`.isApproved`/`.percentage` with no null guard. `profileCompleteness` is only populated asynchronously via the `profileCompleteness$` subscription, and `fetchProgram(id, true)` fires immediately on route-param subscribe, before that store value has necessarily arrived — a race. Sibling method `isSubmitEnabled()` in `program-details-top-bar.component.ts` already guards this same data with `if (!this.profileCompleteness || this.loader) return false` — this call site was simply missed.

## Fix
Added `&& this.profileCompleteness` to the `if (fromSubmit)` condition, before the `canSubmit` computation runs.

## Blast radius
None — when `profileCompleteness` hasn't loaded yet, the submit-prompt flow is skipped for that render pass rather than crashing; it still runs normally once the data arrives and the component re-renders.

## Verification
`npx tsc --noEmit -p tsconfig.app.json` clean. No test suite change — no automated regression coverage added.
