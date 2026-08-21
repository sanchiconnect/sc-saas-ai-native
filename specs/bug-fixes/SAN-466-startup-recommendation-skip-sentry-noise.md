---
id: SAN-466
title: Skipping startup sync — no top-level owner user found, flooding Sentry (3 events)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-466
sentry:
  - SC-SAAS-BACKEND-P
repos: [backend]
commit: sc-saas-backend@2e01d244 (branch ai_native_setup_aman)
created: 2026-08-20
updated: 2026-08-21
---

# SAN-466 — startup-recommendation cron skip logging as warn

## Root cause
Startup ID 4 has a team-member account (parentId IS NOT NULL) as its owner. The cron `getRecommendedStartupsForInvestor()` joins on `user.parentId IS NULL`, so startup 4 always yields an empty `user[]` and is skipped. This is correct and intentional behavior. The Sentry noise came from `logger.warn()` at line 60 — `CaptureConsole` forwards warn to Sentry.

## Fix
Downgraded `logger.warn` → `logger.debug` at `startup-recommendation-to-investor.service.ts:60`.

## Data fix (separate action — optional)
Startup ID 4's ownership can be reassigned to a top-level user account via the admin panel to include it in recommendations.

## Blast radius
None — logging change only; skip behavior unchanged.

## Verification
`tsc --noEmit --skipLibCheck` clean. Committed `2e01d244`.
