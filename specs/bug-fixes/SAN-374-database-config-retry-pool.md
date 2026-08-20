---
id: SAN-374
title: TypeORM production config had no retry/pool/reconnection settings
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-374
sentry:
  - SC-SAAS-BACKEND-1T
repos: [backend]
commit: sc-saas-backend@1e2a23ea (branch ai_native_setup_aman)
created: 2026-08-19
updated: 2026-08-19
---

# SAN-374 — ECONNREFUSED with no retry logic

## Root cause
`database.config.ts`'s production block had zero `retryAttempts`/`retryDelay`/`keepConnectionAlive`/`extra.connectionLimit` settings. Host is read from `process.env.DB_HOST` (not hardcoded — no tenant-isolation issue). Any transient DB blip (restart, failover, brief network drop) threw a raw unhandled `ECONNREFUSED` straight to Sentry with no retry. Production config was also silently missing `port`, falling back to TypeORM's default 3306.

## Fix
Added `port`, `retryAttempts: 10`, `retryDelay: 3000`, `keepConnectionAlive: true`, `extra: { connectionLimit: 10, connectTimeout: 10000 }` to the production config in `database.config.ts`; extended `IDatabaseConfigAttributes` in `dbConfig.interface.ts` to type the new fields.

## Blast radius
None — `development`/`local` configs untouched; `database.module.ts`'s `createTypeOrmOptions()` spreads `...config` without colliding with any of the new keys. Tenant-isolation check: host still comes from env, never hardcoded/cross-referenced — fix only adds resilience to the single tenant DB this deployment already points at.

## Verification
`tsc --noEmit` clean; `npm run build` clean; `npm run lint` on the 2 changed files shows only pre-existing unused-import warnings, 0 errors.
