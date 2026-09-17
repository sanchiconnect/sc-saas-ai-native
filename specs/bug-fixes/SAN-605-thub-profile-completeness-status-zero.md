---
id: SAN-605
title: "startupDashboard(Http failure 0 Unknown Error) on thub.sanchidev.in — 7 users, 24 events"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-605
sentry:
  - SC-SAAS-FRONTEND-49
repos: [frontend, backend]
commit: none — no fixable code defect found, see Investigation
created: 2026-09-04
updated: 2026-09-04
---

# SAN-605 — startupDashboard(Http failure 0 Unknown Error) on thub.sanchidev.in

## Investigation — no code defect found
Same tenant (`thub.sanchidev.in`) and same "0 Unknown Error" pattern as SAN-604, hitting `profile_completeness` (backed by `startup-dashboard.service.ts:38-68` on the frontend, `getStartupProfileCompletenessReport()` — a ~500-line report — on the backend) instead of `startup-information`. Frontend status-0 handling checked and correct. No backend CORS code bug found (same investigation as SAN-604, run together since they share tenant and symptom).

## Disposition
No fixable frontend or backend code bug identified — same conclusion as SAN-604: likely tenant-deployment/infra-scoped, not fixable by editing shared backend source.

## Related
SC-SAAS-FRONTEND-3M (SAN-604) — same tenant, same fault pattern, investigated together.
