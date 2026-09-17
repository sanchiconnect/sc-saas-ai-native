---
id: SAN-569
title: startupinfoFault Unknown Error on pitch-deck fundraising page (thub.sanchidev.in)
type: bug-fix
status: in-progress
linear: https://linear.app/sanchiconnect/issue/SAN-569
sentry:
  - SC-SAAS-FRONTEND-3M
repos: [frontend]
commit: n/a — no frontend gap found, investigated only
created: 2026-09-03
updated: 2026-09-03
---

# SAN-569 — startupinfoFault 0 Unknown Error (thub.sanchidev.in)

## Finding
Same investigation and conclusion as SAN-567 (SC-SAAS-FRONTEND-49): traced the startup-information call path end-to-end, failure already degrades gracefully via existing `catchError`/reducer/consumer guards, no crash or missing fallback found. No change made.

Note: this page's underlying error state (`StartUpState.error`) *was* separately found to have no render site anywhere and was fixed as part of SAN-566 (psgstep 504 cluster) — that fix (a retry banner in `startup-information.component`) will also apply here, since it's the same NgRx slice/selector, even though the root network failure for *this* tenant is unrelated to psgstep.

## Re-investigated 2026-09-03
Re-confirmed the SAN-566 fix fully covers this ticket's render gap: `startup-information.component` and the shared `pitch-deck-management.component` (which backs the `fundraising-pitch` culprit URL specifically) both now render the `getStartUpInfoError` banner added under SAN-566. There is no further frontend gap here — the only open item is the underlying `0 Unknown Error` against `api.thub.sanchidev.in`, which is a backend/infra question, not frontend code.

## Action required (Backend/infra owner)
Investigate the `0 Unknown Error` against `api.thub.sanchidev.in` for this specific tenant/endpoint — same as SAN-567.

## Blast radius
None from this ticket directly — the render-gap portion is fixed via SAN-566's changes to `startup-information.component`.

## Verification
N/A — no code change made specific to this ticket (see SAN-566 for the shared fix).

## Related
SAN-567 (same tenant, same failure shape, different endpoint). SAN-566 (fixed the shared render gap this page benefits from).
