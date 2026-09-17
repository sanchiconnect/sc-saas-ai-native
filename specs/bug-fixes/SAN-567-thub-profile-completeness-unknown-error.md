---
id: SAN-567
title: startupDashboard Unknown Error fetching profile_completeness on thub.sanchidev.in
type: bug-fix
status: in-progress
linear: https://linear.app/sanchiconnect/issue/SAN-567
sentry:
  - SC-SAAS-FRONTEND-49
repos: [frontend]
commit: n/a — no frontend gap found, investigated only
created: 2026-09-03
updated: 2026-09-03
---

# SAN-567 — startupDashboard 0 Unknown Error (thub.sanchidev.in)

## Finding
Traced the full path: `startup-dashboard.service.ts` (HTTP call) → `startup.dashboard.effects.ts` (`catchError`, dispatches a `*Fault` action) → `startup.dashboard.reducer.ts` (sets the field to `null`, loading back to `false` — never stuck loading) → every consumer (`profile.service.ts`, `public-layout-sidebar`, `call-for-applications*`, `dashboard-v2`, etc.) reads the result via `if (res)`/`?.` guards. The failure already degrades gracefully to a default state everywhere it's read; no crash or missing fallback found. This is the same "quietly stay in default state" pattern used elsewhere in the app (e.g. `dashboard-v2.component.ts`'s plan-fetch error handlers).

No change made — inventing a new UI/retry pattern here without a confirmed gap would be speculative.

## Re-investigated 2026-09-03
Read `profile.service.ts` line by line (the actual source of `profileCompleteness$`, consumed by `call-for-applications.component.ts`/`call-for-applications-card.component.ts`, the culprit page). Every `catchError` in this file (~20 sites) already handles failure correctly: on error it does **not** call `.next(res)` on the `ReplaySubject` — it simply skips the emission rather than throwing or propagating an error into the stream. Consumers already guard with `if (profileCompleteness) { ... }`. This is intentional, working-as-designed graceful degradation, consistent with the rest of the codebase — confirmed, not a frontend bug. No fix applied because there is nothing to fix.

## Action required (Backend/infra owner)
The underlying `0 Unknown Error` (network/CORS-level failure, not a 401/403) against `api.thub.sanchidev.in` for this specific call needs investigation on the backend/hosting side — the frontend has nothing further to guard against.

## Blast radius
None — no change made.

## Verification
N/A — no code change made.

## Related
`SC-SAAS-FRONTEND-3M` (SAN-569) is the same tenant, same `0 Unknown Error` shape, different endpoint — investigate together.
