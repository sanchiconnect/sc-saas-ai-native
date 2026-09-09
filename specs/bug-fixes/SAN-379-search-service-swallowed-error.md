---
id: SAN-379
title: searchStartupOrLiveDeal swallows the real error into a generic InternalServerErrorException
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-379
sentry:
  - SC-SAAS-BACKEND-1X
repos: [backend]
commit: sc-saas-backend@1e2a23ea (branch ai_native_setup_aman)
created: 2026-08-19
updated: 2026-08-19
---

# SAN-379 — searchStartupOrLiveDeal generic 500

## Root cause
Same production incident as SAN-380. `SearchService.searchStartupOrLiveDeal`'s `try/catch` swallowed the real underlying error (the `QueryFailedError: Unknown column 'NaN'` from SAN-380) into a generic, unlogged `InternalServerErrorException` — the real cause was invisible in Sentry/logs.

## Fix
Added `this.logger.error({ error, startupSearchDto }, 'searchStartupOrLiveDeal failed')` before the existing `throw`, so the real cause is now visible instead of masked. The actual bug (unvalidated numeric param) is fixed in SAN-380.

## Blast radius
None — purely additive logging; the thrown exception and controller response shape are unchanged. `StartupOrLiveDealSearchDto` contains only search filters (ids, enums, pagination, keyword) — no PII/tokens, safe to log.

## Verification
`tsc --noEmit` clean; `npm run build` clean; lint shows only pre-existing unused-import warnings on this file, 0 errors.
