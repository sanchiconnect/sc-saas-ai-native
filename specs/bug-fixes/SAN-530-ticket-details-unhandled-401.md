---
id: SAN-530
title: Unhandled 401 fetching ticket details
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-530
sentry:
  - SC-SAAS-FRONTEND-19
repos: [frontend]
commit: sc-saas-frontend@15c065b3 (branch ai_native_setup_vishali, pushed to origin, not yet on ai_native_setup/main)
created: 2026-08-26
updated: 2026-08-26
---

# SAN-530 — unhandled 401 fetching ticket details

## Root cause
`TicketDetailsComponent.fetchTicketDetails()` subscribes to `TicketService.getTicketDetails()` with a bare `.subscribe()` (no error callback). The service already `catchError`s the HTTP failure, toasts it, and re-throws; the pipe's `tap()` error callback only stops the loader as a side effect — it doesn't suppress the error, so it reaches the bare `.subscribe()` unhandled. Same class of defect fixed several times today (SC-1/SAN-509, SC-2W/SAN-507, SC-8/SAN-529).

## Fix
Added a no-op `error` callback to the `.subscribe()`, matching the established pattern already used elsewhere in this repo (`startup-all-required-details-form.component.ts`'s `getCountries()`/`getStates()`/`getCities()` under SAN-509).

## Blast radius
None — no behavior change on the success path; the service already toasts the error and the `tap`/`finalize` callbacks already stop the loader either way. Diff is 3 lines.

## Verification
`tsc --noEmit` clean. No test suite configured for this repo; type-check + code-review against the existing, already-proven no-op-error-callback pattern was the strongest verification available. Committed (`15c065b3`) and confirmed pushed to `origin/ai_native_setup_vishali`. Not yet on the shared `ai_native_setup` branch or `main`.
