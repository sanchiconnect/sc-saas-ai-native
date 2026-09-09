---
id: SAN-607
title: "startupDashboard(Startup not found) on supernova.gdai.in — 6 users, 13 events"
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-607
sentry:
  - SC-SAAS-FRONTEND-3T
repos: [backend]
commit: sc-saas-backend@93d6359e (branch ai_native_setup_vishali, pushed)
created: 2026-09-04
updated: 2026-09-04
---

# SAN-607 — startupDashboard(Startup not found) on supernova.gdai.in

## Root cause
Same root cause and same tenant as SAN-606: `StartupService.getDashboard()`'s equivalent self-lookup (also keyed by `session.startupId`, never a user-typed name) threw the misleading `ApiErrors.STARTUP_NOT_FOUND` message instead of `STARTUP_PROFILE_NOT_ATTACHED`. This path's null check was already correctly ordered (no dead-code reorder needed here, unlike SAN-606).

## Fix
`startup.service.ts`: swapped `ApiErrors.STARTUP_NOT_FOUND` → `ApiErrors.STARTUP_PROFILE_NOT_ATTACHED` for this self-lookup path.

## Blast radius
Message-text-only change on an already-erroring path. Same consumer check as SAN-606 — no frontend UI branches on the specific wording.

## Verification
Ran the actual backend `startup` module test suite: 20/20 pass (same run as SAN-606, same commit).

## Related
SC-SAAS-FRONTEND-3V (SAN-606) — same tenant, same fault class, same commit.
