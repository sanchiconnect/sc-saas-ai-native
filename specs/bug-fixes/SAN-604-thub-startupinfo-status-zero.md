---
id: SAN-604
title: "startupinfoFault(Http failure 0 Unknown Error) on thub.sanchidev.in — 9 users, 20 events"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-604
sentry:
  - SC-SAAS-FRONTEND-3M
repos: [frontend, backend]
commit: none — no fixable code defect found, see Investigation
created: 2026-09-04
updated: 2026-09-04
---

# SAN-604 — startupinfoFault(Http failure 0 Unknown Error) on thub.sanchidev.in

## Investigation — no code defect found
HTTP status `0` means no response reached the browser at all (CORS rejection, DNS/network failure, or an unhandled exception crashing the request before headers/CORS are set). Checked both ends:

- **Frontend**: `startup.service.ts:96-113` already has correct status-0 fallback handling — nothing to fix there.
- **Backend**: checked `sc-saas-backend`'s CORS configuration for an exact-string-vs-pattern mismatch that could reject `thub.sanchidev.in` specifically — found no code-level CORS bug. Only 2 of many endpoints on this tenant exhibit the symptom (this one and SAN-605's `profile_completeness`), which argues against a blanket CORS misconfiguration; both do heavier work (S3 signed-URL call; a large ~500-line report), consistent with an intermittent timeout/infra issue rather than a systematic code bug.

Fixed one unrelated latent null-check-ordering bug found along the way in `getStartupInformation()` (dead code today, folded into the SAN-606 commit).

## Disposition
No fixable frontend or backend code bug identified for the status-0 symptom itself. This looks tenant-deployment/infra-scoped (per this workspace's invariant: backend is one-deployment-per-tenant, config loaded at bootstrap from the tenants control-plane) — recommend checking `thub.sanchidev.in`'s specific deployment/CORS/network config outside this repo's source, rather than a further speculative code change.

## Related
SC-SAAS-FRONTEND-49 (SAN-605) — same tenant, same "0 Unknown Error" pattern, different endpoint.
