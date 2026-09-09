---
id: SAN-566
title: incubation.psgstep.org tenant — repeated 504 Gateway Timeout, missing error/retry UI
type: bug-fix
status: in-progress
linear: https://linear.app/sanchiconnect/issue/SAN-566
sentry:
  - SC-SAAS-FRONTEND-4C
  - SC-SAAS-FRONTEND-3W
  - SC-SAAS-FRONTEND-7V
repos: [frontend]
commit: sc-saas-frontend@cd6042ee (branch ai_native_setup_vishali, not pushed)
created: 2026-09-03
updated: 2026-09-03
---

# SAN-566 — psgstep tenant 504 cluster

## Root cause
Three different endpoints (profile_completeness, startup-information, documents) all returning 504 Gateway Timeout for the same tenant (`incubation.psgstep.org`) strongly suggests a backend/infra problem specific to that tenant's deployment — **out of scope for this repo** (likely `sc-saas-backend`, not checked out for diagnosis here).

Separately, a genuine, fixable frontend gap was found: `startupDashboardError` / `startupProfileCompletenessError` (in `startup.dashboard.reducer.ts`) and `StartUpState.error` (in `startup.reducer.ts`) were both tracked in NgRx state on failure but had **no selector and were never rendered anywhere** — so any backend failure on these calls (this 504 cluster included) silently left the UI in a stuck/default state with no error or retry option.

## Fix
- Added `getStartupDashboardError` / `getStartupProfileCompletenessError` selectors (`startup.dashboard.selectors.ts`) and `getStartUpInfoError` (`startup.selectors.ts`).
- Wired them into `dashboard.component.ts/.html`, `startup-information.component.ts/.html`, and the shared `pitch-deck-management.component.ts/.html` (backs fundraising-pitch, hiring-pitch, and sales-pitch together).
- Each now shows an `alert alert-danger` banner with a retry button that re-dispatches the original load action — reusing the exact banner convention already established in `startup-supporting-documents.component.html`/`pitch-deck-management.component.html`, not a new UI pattern.

## Blast radius
None on the happy path — banners only render when the corresponding error selector is non-null; existing successful-load rendering is untouched.

## Verification
`npx tsc -p tsconfig.app.json --noEmit` clean across all 6 changed files.

## Action required (Backend/infra owner)
Diagnose why `api.incubation.psgstep.org` is timing out across multiple endpoints — this fix only makes the failure visible/retriable, it does not address why it's failing.
