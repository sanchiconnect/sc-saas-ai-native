---
id: SAN-455
title: AxiosError — Request failed with status 500, source unknown (13 events)
type: bug-fix
status: in-progress
linear: https://linear.app/sanchiconnect/issue/SAN-455
sentry:
  - SC-SAAS-BACKEND-X
repos: [backend]
commit: n/a — needs better error logging deployed first
created: 2026-08-20
updated: 2026-08-21
---

# SAN-455 — AxiosError 500, source unidentifiable from Sentry

## Root cause
No stacktrace available in Sentry — the AxiosError is caught and logged without the call stack, so the source service/endpoint cannot be identified. Error is still occurring as of 2026-08-20.

## Likely sources (most to least probable)
- `ecosystem.service.ts` — 20+ axios calls, called on profile approval flows
- `comet-chat.service.ts` — 13+ axios methods, some catch blocks swallow errors silently
- `power-pitch-external.service.ts` — external cross-workspace API

## Action required
1. Add the target URL and service name to AxiosError catch blocks so Sentry captures context, e.g. `this.logger.error('[EcosystemService] POST ${url} failed', err)`.
2. Deploy and wait for the next 500 — Sentry will then show which service/endpoint is responsible.
3. Fix the root 500 in the identified downstream service.

## Verification
Cannot verify until source is identified via improved logging.
